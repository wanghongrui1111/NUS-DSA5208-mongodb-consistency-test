"""Test-only proof that v4's P_old pre-delay creates a stale new-primary side."""

import json
import time
import uuid

from netlabv5 import host


def mongo_json(node, script):
    result = host.docker("exec", host.container(node), "mongosh", "--quiet", "--eval", script,
                         capture_output=True)
    return json.loads(result.stdout.strip().splitlines()[-1])


def update_script(collection, version, write_id, concern):
    return (
        "const d=db.getSiblingDB('netlabv5');const c=" + json.dumps(collection) + ";"
        "const tag=" + json.dumps(write_id) + ";"
        "print(JSON.stringify(d.runCommand({update:c,updates:[{q:{_id:'source'},"
        f"u:{{$set:{{v:{version},write_id:tag}}}},upsert:true}}],"
        "writeConcern:" + json.dumps(concern) + "})))"
    )


def wait_for_mongo2_primary(timeout=90):
    deadline = time.monotonic() + timeout
    script = "const s=rs.status();print(s.members.find(m=>m.stateStr==='PRIMARY')?.name||'')"
    while time.monotonic() < deadline:
        result = host.docker("exec", host.container("mongo2"), "mongosh", "--quiet", "--eval", script,
                             capture_output=True, check=False)
        if result.returncode == 0 and result.stdout.strip().startswith("mongo2:"):
            return
        time.sleep(1)
    raise RuntimeError("mongo2 did not become the new primary")


def stale_script(collection, source_tag):
    return (
        "const d=db.getSiblingDB('netlabv5');const c=" + json.dumps(collection) + ";"
        "const tag=" + json.dumps(source_tag) + ";"
        "const entries=db.getSiblingDB('local').getCollection('oplog.rs').countDocuments({ns:'netlabv5.'+c,"
        "$or:[{'o.write_id':tag},{'o.diff.u.write_id':tag}]});"
        "const doc=d.getCollection(c).findOne({_id:'source'});"
        "print(JSON.stringify({oplog_matches:entries,document:doc,stale:entries===0&&doc&&doc.v===0}));"
    )


def run_probe(fault, observer, require_new_primary):
    source_tag = f"pold-delay-stale-smoke|{uuid.uuid4()}"
    collection = f"pold_delay_probe_{observer}"
    host.healthy_reset()
    host.run([*host.COMPOSE, "up", "-d", "tc-injector", "tc-injector-mongo2"])
    try:
        baseline = mongo_json("mongo1", update_script(collection, 0, "pold-delay-baseline", {"w": 3, "wtimeout": 15000}))
        if not baseline.get("ok"):
            raise RuntimeError(f"baseline write failed: {baseline}")
        delay = host.start_pold_delay(fault)
        source = mongo_json("mongo1", update_script(collection, 1, source_tag, {"w": 1, "wtimeout": 15000}))
        if not source.get("ok"):
            raise RuntimeError(f"source write failed: {source}")
        moved_services = tuple(s for s in host.fault_plan(fault)["groups"][1] if s != "labclient")
        event = {"fault": fault, "proof": {"moved": host.move_to_private(moved_services)}, "services": moved_services}
        if require_new_primary:
            wait_for_mongo2_primary()
        stale = mongo_json(observer, stale_script(collection, source_tag))
        if not stale.get("stale"):
            raise RuntimeError(f"{fault} stale-side proof failed: {stale}")
        return {"fault": fault, "observer": observer, "source": source_tag, "delay": delay, "event": event, "stale": stale}
    finally:
        try:
            services = tuple(s for s in host.fault_plan(fault)["groups"][1] if s != "labclient")
            host.restore_network(services)
        finally:
            host.stop_pold_delay()


def main():
    proofs = [
        run_probe("partition-mongo1-vs-mongo23-client", "mongo2", True),
        run_probe("partition-mongo12-vs-mongo3-client", "mongo3", False),
    ]
    print(json.dumps(proofs, indent=2))


if __name__ == "__main__":
    main()
