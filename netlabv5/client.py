"""In-network collector: four small experiments plus raw command/oplog evidence."""

import argparse
import time
import uuid
from pathlib import Path

from bson import json_util
from pymongo import MongoClient, monitoring
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import Primary, PrimaryPreferred, SecondaryPreferred
from pymongo.write_concern import WriteConcern

from .judge import check
from .matrix import cells

URI = "mongodb://mongo1:27017,mongo2:27017,mongo3:27017/netlabv5?replicaSet=rs0"
NODES = ("mongo1", "mongo2", "mongo3")
SEED_VERSION = 0
EXPERIMENTS = {
    "ryw": ("write1", "read1"),
    "mr": ("read1", "read2"),
    "wfr": ("read1", "write1"),
    "mw": ("write1", "write2"),
}
PREFERENCES = {
    "primary": Primary(),
    "primaryPreferred": PrimaryPreferred(),
    "secondaryPreferred": SecondaryPreferred(),
}


def error(exc):
    return {"type": type(exc).__name__, "message": str(exc)[:500]}


def server_name(connection_id):
    return f"{connection_id[0]}:{connection_id[1]}"


class Commands(monitoring.CommandListener):
    """Keep one complete command trace per explicitly tagged workload operation."""
    def __init__(self):
        self.pending = {}
        self.finished = {}

    def started(self, event):
        tag = event.command.get("comment")
        if tag:
            self.pending[event.request_id] = (tag, {
                "server": server_name(event.connection_id),
                "request_id": event.request_id,
                "command_name": event.command_name,
                "command": event.command,
            })

    def succeeded(self, event):
        item = self.pending.pop(event.request_id, None)
        if item:
            tag, record = item
            record.update(status="succeeded", duration_micros=event.duration_micros, reply=event.reply)
            self.finished[tag] = record

    def failed(self, event):
        item = self.pending.pop(event.request_id, None)
        if item:
            tag, record = item
            record.update(status="failed", duration_micros=event.duration_micros, failure=str(event.failure))
            self.finished[tag] = record

    def take(self, tag):
        return self.finished.pop(tag, None)


def tag(collection, name, attempt_id=None):
    parts = [collection.name]
    if attempt_id is not None:
        parts.append(attempt_id)
    parts.append(name)
    return "|".join(parts)


def barrier_paths(directory, experiment, row):
    stem = f"{experiment}__{row['id']}"
    return tuple(directory / f"{stem}.{suffix}" for suffix in ("ready", "release", "release2", "done", "proceed"))


def pre_action_paths(directory, experiment, row):
    """Host/client gate used to arm a fault before MW emits W1."""
    stem = f"{experiment}__{row['id']}"
    return directory / f"{stem}.pre_ready", directory / f"{stem}.pre_release"


def wait_for(path, timeout=60):
    deadline = time.monotonic() + timeout
    while not path.exists():
        if time.monotonic() >= deadline:
            raise TimeoutError(f"barrier timed out waiting for {path.name}")
        time.sleep(0.05)


def pause_between(directory, experiment, row, wait_release2=False):
    if directory is None:
        return None
    ready, release, release2, done, proceed = barrier_paths(directory, experiment, row)
    ready.write_text("ready\n", encoding="utf-8")
    wait_for(release)
    if wait_release2:
        wait_for(release2)
    return {"ready": ready.name, "release": release.name, "done": done.name, "proceed": proceed.name}


def pause_before_action(directory, experiment, row, enabled=False):
    if directory is None or not enabled:
        return None
    ready, release = pre_action_paths(directory, experiment, row)
    ready.write_text("pre_ready\n", encoding="utf-8")
    wait_for(release)
    return {"pre_ready": ready.name, "pre_release": release.name}


def finish_between(directory, experiment, row):
    if directory is None:
        return
    _, _, _, done, proceed = barrier_paths(directory, experiment, row)
    done.write_text("done\n", encoding="utf-8")
    wait_for(proceed)


def write(collection, session, version, name, commands, attempt_id=None):
    started = time.monotonic()
    marker = tag(collection, name, attempt_id)
    record = {"op": name, "tag": marker, "version": version}
    try:
        result = collection.update_one(
            {"_id": collection.name},
            {"$set": {"v": version, "write_id": marker}},
            upsert=True, session=session, comment=marker,
        )
        record.update(ok=True, acknowledged=result.acknowledged)
    except Exception as exc:
        record.update(ok=False, acknowledged=False, error=error(exc))
    record.update(ms=int((time.monotonic() - started) * 1000), command=commands.take(marker))
    if session is not None:
        record.update(operation_time=session.operation_time, cluster_time=session.cluster_time)
    return record


def read(collection, session, name, commands, max_time_ms=None, attempt_id=None):
    started = time.monotonic()
    marker = tag(collection, name, attempt_id)
    record = {"op": name, "tag": marker}
    try:
        options = {} if max_time_ms is None else {"max_time_ms": max_time_ms}
        doc = collection.find_one({"_id": collection.name}, session=session, comment=marker, **options)
        record.update(ok=True, value=None if doc is None else doc.get("v"),
                      source_write_id=None if doc is None else doc.get("write_id"))
    except Exception as exc:
        record.update(ok=False, error=error(exc))
    record.update(ms=int((time.monotonic() - started) * 1000), command=commands.take(marker))
    if session is not None:
        record.update(operation_time=session.operation_time, cluster_time=session.cluster_time)
    return record


def oplog(collection, nodes=NODES):
    """Read selected containers' local oplogs directly; no Docker socket is required."""
    query = {"ns": f"netlabv5.{collection.name}", "$or": [
        {"o._id": collection.name}, {"o2._id": collection.name},
    ]}
    snapshots = {}
    for node in nodes:
        client = MongoClient(f"mongodb://{node}:27017/?directConnection=true", serverSelectionTimeoutMS=3_000)
        try:
            entries = list(client.local.oplog.rs.find(query).sort("$natural", 1))
            snapshots[node] = {"entries": entries}
        except Exception as exc:
            snapshots[node] = {"entries": [], "error": error(exc)}
        finally:
            client.close()
    return snapshots


def capture_successor_oplog(operation, collection):
    """Snapshot the serving primary immediately after an acknowledged successor write.

    This runs in the collector before it creates the ``.done`` barrier.  The host
    therefore cannot reconnect mongo1 or remove the netem qdisc before this
    evidence exists.  No journal/read-concern wait is requested: this is the
    current local oplog branch at W2 completion.
    """
    server = (operation.get("command") or {}).get("server")
    if operation.get("ok") and server:
        operation["oplog_after_successor_ack"] = oplog(
            collection, (server.split(":", 1)[0],))
        operation["oplog_after_successor_ack_monotonic_ns"] = time.monotonic_ns()


def session_for(client, row):
    if row["wc"] == 0:
        return None
    return client.start_session(causal_consistency=row["causal"])


def seed_successor_session(predecessor, successor):
    """Port causal timestamps when the partition moves the client to mongo3."""
    if predecessor is None or successor is None:
        return
    if predecessor.cluster_time:
        successor.advance_cluster_time(predecessor.cluster_time)
    if predecessor.operation_time:
        successor.advance_operation_time(predecessor.operation_time)


def collection_for(client, row, experiment):
    wc = {"w": row["wc"]}
    if row["wc"] != 0:
        wc["wtimeout"] = 15_000
    name = f"{experiment}__{row['id']}"
    return client.netlabv5[name].with_options(
        read_concern=ReadConcern(row["rc"]),
        write_concern=WriteConcern(**wc),
        read_preference=PREFERENCES[row["preference"]],
    )


def seed_is_converged(observed, expected_write_id):
    """A seed is usable only when every data-bearing member has its exact tag."""
    return all(observed.get(node) == expected_write_id for node in NODES)


def wait_for_seed(collection, expected_write_id, timeout=30):
    """Poll direct local reads until every member contains the setup document."""
    deadline = time.monotonic() + timeout
    observed = {}
    while time.monotonic() < deadline:
        observed = {}
        for node in NODES:
            client = MongoClient(f"mongodb://{node}:27017/?directConnection=true", serverSelectionTimeoutMS=3_000)
            try:
                document = client.netlabv5[collection.name].find_one({"_id": collection.name})
                observed[node] = None if document is None else document.get("write_id")
            except Exception:
                observed[node] = None
            finally:
                client.close()
        if seed_is_converged(observed, expected_write_id):
            return {"ok": True, "nodes": observed, "wait_ms": int((time.monotonic() - (deadline - timeout)) * 1000)}
        time.sleep(0.05)
    raise TimeoutError(f"seed did not converge on all nodes: {observed}")


def seed(client, collection, commands, attempt_id=None, write_concern="majority"):
    """Create the measured document and prove it exists on all three nodes."""
    setup = collection.with_options(write_concern=WriteConcern(w=write_concern, wtimeout=15_000),
                                    read_preference=PrimaryPreferred())
    record = None
    for _ in range(3):
        record = write(setup, None, SEED_VERSION, "seed", commands, attempt_id)
        if record.get("ok"):
            break
        time.sleep(1)
    if not record.get("ok"):
        raise RuntimeError(f"seed write failed: {record.get('error')}")
    return record, wait_for_seed(collection, record["tag"])


def partition_timeout_options(timeout_ms):
    return {
        "serverSelectionTimeoutMS": timeout_ms,
        "connectTimeoutMS": timeout_ms,
        "socketTimeoutMS": timeout_ms + 1_000,
    }


def workload_client(uri, commands, timeout_options=None):
    options = {
        "serverSelectionTimeoutMS": 15_000,
        "connectTimeoutMS": 10_000,
        "socketTimeoutMS": 20_000,
    } if timeout_options is None else timeout_options
    return MongoClient(uri, appName="netlab-v5", event_listeners=[commands], retryReads=False,
                       retryWrites=False, **options)


def successor_context(row, experiment, predecessor, commands, second_uri, timeout_options=None):
    if second_uri is None:
        return None, None, None
    client = workload_client(second_uri, commands, timeout_options)
    session = session_for(client, row)
    seed_successor_session(predecessor, session)
    return client, collection_for(client, row, experiment), session


def pold_needs_source(experiment):
    """Read-first relations need an old-primary write to establish lag before Action1."""
    return experiment in ("mr", "wfr")


def run_cell(client, row, experiment, barrier_dir=None, second_uri=None, first_uri=URI,
             partition_timeout_ms=None, wait_release2=False, pre_action_barrier=False, pold_delay=False):
    commands = Commands()
    attempt_id = uuid.uuid4().hex
    timeout_options = None if partition_timeout_ms is None else partition_timeout_options(partition_timeout_ms)
    # A separate client keeps workload command monitoring scoped to this one cell.
    workload = workload_client(first_uri, commands, timeout_options)
    collection = collection_for(workload, row, experiment)
    session = session_for(workload, row)
    ops = []
    successor_workload = successor_session = None
    try:
        seed_record, seed_convergence = seed(client, collection, commands, attempt_id)
        ops.append(seed_record)
        pre_action = pause_before_action(barrier_dir, experiment, row, pre_action_barrier)
        between = None
        if experiment == "ryw":
            w1 = write(collection, session, row["v1"], "write1", commands, attempt_id)
            between = pause_between(barrier_dir, experiment, row, wait_release2)
            successor_workload, successor_collection, successor_session = successor_context(
                row, experiment, session, commands, second_uri, timeout_options)
            r1 = read(successor_collection if successor_collection is not None else collection,
                      successor_session if successor_workload else session,
                      "read1", commands, partition_timeout_ms, attempt_id)
            finish_between(barrier_dir, experiment, row)
            ops.extend((w1, r1))
        elif experiment == "mr":
            if pold_delay and pold_needs_source(experiment):
                ops.append(write(collection, session, row["v1"], "source", commands, attempt_id))
            r1 = read(collection, session, "read1", commands, partition_timeout_ms, attempt_id)
            between = pause_between(barrier_dir, experiment, row, wait_release2)
            successor_workload, successor_collection, successor_session = successor_context(
                row, experiment, session, commands, second_uri, timeout_options)
            r2 = read(successor_collection if successor_collection is not None else collection,
                      successor_session if successor_workload else session,
                      "read2", commands, partition_timeout_ms, attempt_id)
            finish_between(barrier_dir, experiment, row)
            ops.extend((r1, r2))
        elif experiment == "wfr":
            if pold_delay:
                source = write(collection, session, row["v1"], "source", commands, attempt_id)
                ops.append(source)
            r1 = read(collection, session, "read1", commands, partition_timeout_ms, attempt_id)
            between = pause_between(barrier_dir, experiment, row, wait_release2)
            successor_workload, successor_collection, successor_session = successor_context(
                row, experiment, session, commands, second_uri, timeout_options)
            w1 = write(successor_collection if successor_collection is not None else collection,
                       successor_session if successor_workload else session,
                       row["v2"], "write1", commands, attempt_id)
            capture_successor_oplog(w1, successor_collection if successor_collection is not None else collection)
            finish_between(barrier_dir, experiment, row)
            ops.extend((r1, w1))
        elif experiment == "mw":
            pre_action = pause_before_action(barrier_dir, experiment, row, pre_action_barrier)
            w1 = write(collection, session, row["v1"], "write1", commands, attempt_id)
            between = pause_between(barrier_dir, experiment, row, wait_release2)
            successor_workload, successor_collection, successor_session = successor_context(
                row, experiment, session, commands, second_uri, timeout_options)
            w2 = write(successor_collection if successor_collection is not None else collection,
                       successor_session if successor_workload else session,
                       row["v2"], "write2", commands, attempt_id)
            capture_successor_oplog(w2, successor_collection if successor_collection is not None else collection)
            finish_between(barrier_dir, experiment, row)
            ops.extend((w1, w2))
        record = {**row, "experiment": experiment, "attempt_id": attempt_id, "ops": ops,
                  "seed_convergence": seed_convergence, "pre_action": pre_action, "between": between,
                  "session_id": None if session is None else session.session_id}
        record["check"] = check(record)
        return record
    finally:
        if successor_session is not None:
            successor_session.end_session()
        if successor_workload is not None:
            successor_workload.close()
        if session is not None:
            session.end_session()
        workload.close()


def finish_record(row, ops, session_id, *, judge_results):
    """Compatibility helper for raw-result callers; new runs always use ``check``."""
    record = {**row, "ops": ops, "session_id": session_id}
    if judge_results:
        record["check"] = check(record)
    return record


def reset(client):
    client.netlabv5.command("dropDatabase", write_concern=WriteConcern(w="majority", wtimeout=15_000))


def save(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json_util.dumps(records, indent=2) + "\n", encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--experiment", choices=(*EXPERIMENTS, "all"), default="all")
    parser.add_argument("--only")
    parser.add_argument("--barrier-dir", help="Host-controlled pause between the two measured actions.")
    parser.add_argument("--second-uri", help="Use this direct URI only for the post-barrier action.")
    parser.add_argument("--first-uri", default=URI, help="Use this URI for the pre-barrier action.")
    parser.add_argument("--partition-timeout-ms", type=int,
                        help="Bound reads and connections to an intentionally isolated member.")
    parser.add_argument("--wait-release2", action="store_true",
                        help="Action 2 also waits for a .release2 barrier file.")
    parser.add_argument("--pre-action-barrier", action="store_true",
                        help="Wait before Action 1 so the host can arm a fault.")
    parser.add_argument("--pold-delay", action="store_true",
                        help="WFR writes a delayed source after the pre-action barrier.")
    parser.add_argument("--reset-only", action="store_true")
    parser.add_argument("--no-reset", action="store_true", help="The host already reset and seeded the database.")
    args = parser.parse_args(argv)

    client = MongoClient(URI, appName="netlab-v5-reset", retryReads=False, retryWrites=False,
                         serverSelectionTimeoutMS=15_000, connectTimeoutMS=10_000, socketTimeoutMS=20_000)
    try:
        if not args.no_reset:
            reset(client)
        if args.reset_only:
            return
        selected = EXPERIMENTS if args.experiment == "all" else {args.experiment: EXPERIMENTS[args.experiment]}
        destination = Path(args.output)
        barrier_dir = None if args.barrier_dir is None else Path(args.barrier_dir)
        for experiment in selected:
            records = [run_cell(client, row, experiment, barrier_dir, args.second_uri, args.first_uri,
                                args.partition_timeout_ms, args.wait_release2, args.pre_action_barrier,
                                args.pold_delay)
                       for row in cells(args.only)]
            path = destination / experiment / "results.json" if args.experiment == "all" else destination
            save(path, records)
            print(experiment, len(records), "records stored", flush=True)
    finally:
        client.close()


if __name__ == "__main__":
    main()
