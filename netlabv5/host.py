"""Host runner for the compact v5 experiment sequence.

A scenario always collects raw results first.  The collector writes a per-cell
``check`` only after both actions have completed; this runner never infers a
consistency verdict from Docker state.
"""

import argparse
import json
import os
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .matrix import cells

ROOT = Path(__file__).resolve().parents[1]
STACK = os.environ.get("NETLAB_STACK", "netlab-v5")
COMPOSE = ["docker", "compose", "-p", STACK, "-f", "compose.yaml",
           "-f", "compose.client.yaml"]
NETWORK = f"{STACK}-network"
PRIVATE = f"{STACK}-partition"
NODES = ("mongo1", "mongo2", "mongo3")
EXPERIMENTS = ("ryw", "mr", "wfr", "mw")


@dataclass(frozen=True)
class Scenario:
    id: str
    experiments: tuple[str, ...]
    phase: str
    fault: Optional[str] = None


SCENARIOS = (
    Scenario("baseline", EXPERIMENTS, "none"),
    Scenario("partition-ryw-mr", ("ryw", "mr"), "between", "partition-mongo12-vs-mongo3-client"),
    Scenario("stop-mongo3", EXPERIMENTS, "between", "stop-mongo3"),
    Scenario("recover-delay", EXPERIMENTS, "before", "delay"),
    Scenario("recover-partition-mongo12-vs-mongo3-client", EXPERIMENTS, "before", "partition-mongo12-vs-mongo3-client"),
    Scenario("recover-partition-mongo1", EXPERIMENTS, "before", "partition-mongo1"),
    Scenario("recover-partition-mongo2", EXPERIMENTS, "before", "partition-mongo2"),
    Scenario("recover-partition-mongo3", EXPERIMENTS, "before", "partition-mongo3"),
    Scenario("recover-partition-client", EXPERIMENTS, "before", "partition-client"),
)


def scenario_ids():
    return tuple(s.id for s in SCENARIOS)


def fault_plan(name):
    if name == "delay":
        return {"kind": "delay", "targets": ("mongo3",)}
    groups = {
        "partition-mongo12-vs-mongo3-client": (("mongo1", "mongo2"), ("mongo3", "labclient")),
        "partition-mongo1": (("mongo2", "mongo3", "labclient"), ("mongo1",)),
        "partition-mongo2": (("mongo1", "mongo3", "labclient"), ("mongo2",)),
        "partition-mongo3": (("mongo1", "mongo2", "labclient"), ("mongo3",)),
        "partition-client": (("mongo1", "mongo2", "mongo3"), ("labclient",)),
    }
    if name not in groups:
        raise ValueError(f"unknown fault {name!r}")
    return {"kind": "partition", "groups": groups[name]}


def run(command, **kwargs):
    env = {**os.environ, "NETLAB_STACK": STACK, **kwargs.pop("env", {})}
    return subprocess.run(command, cwd=ROOT, text=True, check=True, env=env, **kwargs)


def docker(*args, **kwargs):
    return run(["docker", *args], **kwargs)


def container(service):
    if service == "labclient":
        result = docker("ps", "--filter", f"label=com.docker.compose.project={STACK}",
                        "--filter", "label=com.docker.compose.service=labclient", "--format", "{{.Names}}",
                        capture_output=True)
        names = result.stdout.split()
        if len(names) != 1:
            raise RuntimeError(f"expected one labclient, found {names}")
        return names[0]
    return f"{STACK}-{service}"


def endpoints(network):
    result = docker("network", "inspect", network, "--format", "{{json .Containers}}", capture_output=True)
    return {details["Name"] for details in json.loads(result.stdout).values()}


def ensure_private_network():
    if subprocess.run(["docker", "network", "inspect", PRIVATE], cwd=ROOT, capture_output=True).returncode:
        docker("network", "create", PRIVATE)


def move_to_private(services):
    ensure_private_network()
    events = []
    for service in services:
        name = container(service)
        if name in endpoints(NETWORK):
            docker("network", "disconnect", NETWORK, name)
        if name not in endpoints(PRIVATE):
            docker("network", "connect", PRIVATE, name)
        events.append({"service": service, "container": name, "private": True})
    return events


def restore_network(services):
    events = []
    for service in services:
        name = container(service)
        if name in endpoints(PRIVATE):
            docker("network", "disconnect", PRIVATE, name)
        if name not in endpoints(NETWORK):
            docker("network", "connect", NETWORK, name)
        events.append({"service": service, "container": name, "private": False})
    return events


def delay_command(target=None):
    """Match v4's post-action degrade: 100±20 ms plus 3% egress loss on mongo3."""
    return [
        "netem", "--duration", "2h", "combine", "--delay", "--delay-time", "100",
        "--delay-jitter", "20", "--loss", "--loss-percent", "3", "--", target or container("mongo3"),
    ]


def start_delay(destination):
    """Install v4's 100±20 ms / 3% loss rule directly in mongo3's net namespace."""
    mongo3 = container("mongo3")
    command = ["docker", "run", "--rm", "--network", f"container:{mongo3}", "--cap-add", "NET_ADMIN",
               "--entrypoint", "tc", "ghcr.io/alexei-led/pumba-alpine-nettools:latest",
               "qdisc", "replace", "dev", "eth0", "root", "netem", "delay", "100ms", "20ms", "loss", "3%"]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
    proof = subprocess.run(["docker", "run", "--rm", "--network", f"container:{mongo3}",
                            "--cap-add", "NET_ADMIN", "--entrypoint", "tc",
                            "ghcr.io/alexei-led/pumba-alpine-nettools:latest", "qdisc", "show", "dev", "eth0"],
                           cwd=ROOT, text=True, capture_output=True, check=True).stdout.strip()
    if "netem" not in proof or "100ms" not in proof or "loss 3%" not in proof:
        raise RuntimeError(f"delay qdisc proof missing: {proof or result.stderr}")
    (destination / "delay.log").write_text("direct tc netem: " + proof + "\n", encoding="utf-8")
    return proof


def stop_delay(_handle):
    mongo3 = container("mongo3")
    subprocess.run(["docker", "run", "--rm", "--network", f"container:{mongo3}", "--cap-add", "NET_ADMIN",
                    "--entrypoint", "tc", "ghcr.io/alexei-led/pumba-alpine-nettools:latest",
                    "qdisc", "del", "dev", "eth0", "root"], cwd=ROOT, text=True, capture_output=True, check=False)


def wait(path, process, timeout=90):
    deadline = time.monotonic() + timeout
    while not path.exists():
        if process.poll() is not None:
            raise RuntimeError(f"collector exited {process.returncode} before {path.name}")
        if time.monotonic() > deadline:
            raise TimeoutError(path.name)
        time.sleep(.05)


def barrier(directory, experiment, row, suffix):
    return directory / f"{experiment}__{row['id']}.{suffix}"


def wait_for_mongo(node, timeout=90):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        probe = subprocess.run(["docker", "exec", node, "mongosh", "--quiet", "--eval", "db.runCommand({ping:1}).ok"],
                               cwd=ROOT, text=True, capture_output=True)
        if probe.returncode == 0 and probe.stdout.strip() == "1":
            return
        time.sleep(1)
    raise RuntimeError(f"{node} did not accept MongoDB connections")


def wait_for_primary(timeout=90):
    deadline = time.monotonic() + timeout
    script = "const s=rs.status();const p=s.members.find(m=>m.stateStr==='PRIMARY');print(p?p.name:'')"
    while time.monotonic() < deadline:
        probe = subprocess.run(["docker", "exec", container("mongo1"), "mongosh", "--quiet", "--eval", script],
                               cwd=ROOT, text=True, capture_output=True)
        if probe.returncode == 0 and probe.stdout.strip():
            return probe.stdout.strip().split(":", 1)[0]
        time.sleep(1)
    raise RuntimeError("replica set did not elect a primary")


def healthy_reset():
    run([*COMPOSE, "up", "-d", "mongo1", "mongo2", "mongo3"])
    for node in (container("mongo1"), container("mongo2"), container("mongo3")):
        wait_for_mongo(node)
    script = "try{rs.status()}catch(e){rs.initiate({_id:'rs0',members:[{_id:0,host:'mongo1:27017',priority:2},{_id:1,host:'mongo2:27017',priority:1},{_id:2,host:'mongo3:27017',priority:0}]})}"
    docker("exec", container("mongo1"), "mongosh", "--quiet", "--eval", script)
    primary = wait_for_primary()
    docker("exec", container(primary), "mongosh", "--quiet", "--eval",
           "db.getSiblingDB('netlabv5').dropDatabase({writeConcern:{w:'majority',wtimeout:15000}})")


def run_experiment(destination, scenario, experiment, only):
    barriers = destination / "barriers"
    barriers.mkdir(exist_ok=True)
    output = f"/work/artifacts-v5/{destination.parent.name}/{scenario.id}/{experiment}/results.json"
    run_id = destination.parent.name
    client_barriers = f"/work/artifacts-v5/{run_id}/{scenario.id}/barriers"
    command = [*COMPOSE, "run", "--rm", "labclient", "python", "-m", "netlabv5.client",
               "--experiment", experiment, "--output", output, "--no-reset"]
    if scenario.phase != "none":
        command.extend(("--barrier-dir", client_barriers))
    if scenario.phase == "before":
        command.append("--pre-action-barrier")
    if only:
        command.extend(("--only", only))
    process = subprocess.Popen(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               env={**os.environ, "NETLAB_STACK": STACK})
    rows = cells(only)
    events = []
    try:
        for row in rows:
            if scenario.phase == "none":
                continue
            if scenario.phase == "before":
                wait(barrier(barriers, experiment, row, "pre_ready"), process)
                event = activate_fault(scenario.fault, destination)
                barrier(barriers, experiment, row, "pre_release").touch()
                wait(barrier(barriers, experiment, row, "ready"), process)
                event["recovery"] = clear_fault(scenario.fault, event)
                barrier(barriers, experiment, row, "release").touch()
            else:
                wait(barrier(barriers, experiment, row, "ready"), process)
                event = activate_fault(scenario.fault, destination)
                barrier(barriers, experiment, row, "release").touch()
            wait(barrier(barriers, experiment, row, "done"), process)
            if scenario.phase == "between":
                event["recovery"] = clear_fault(scenario.fault, event)
            barrier(barriers, experiment, row, "proceed").touch()
            events.append({"cell": row["id"], **event})
        stdout, stderr = process.communicate(timeout=180)
        (destination / f"{experiment}.stdout.log").write_text(stdout, encoding="utf-8")
        (destination / f"{experiment}.stderr.log").write_text(stderr, encoding="utf-8")
        if process.returncode:
            raise RuntimeError(f"{experiment} failed: {stderr[-500:]}")
    finally:
        if process.poll() is None:
            process.terminate(); process.wait(timeout=30)
    return events


def activate_fault(name, destination):
    if name == "stop-mongo3":
        docker("stop", container("mongo3"))
        return {"fault": name, "proof": "mongo3 stopped"}
    plan = fault_plan(name)
    if plan["kind"] == "delay":
        proof = start_delay(destination)
        return {"fault": name, "proof": {"qdisc": proof}, "handle": proof}
    moved = move_to_private(plan["groups"][1])
    return {"fault": name, "proof": {"moved": moved}, "services": plan["groups"][1]}


def clear_fault(name, event):
    if name == "stop-mongo3":
        run([*COMPOSE, "up", "-d", "mongo3"])
        return {"mongo3_restarted": True}
    if name == "delay":
        stop_delay(event.pop("handle"))
        return {"delay_removed": True}
    return {"restored": restore_network(event["services"])}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=(*scenario_ids(), "all"), default="all")
    parser.add_argument("--run-id", default=datetime.now(timezone.utc).strftime("v5-%Y%m%d-%H%M%S"))
    parser.add_argument("--only")
    parser.add_argument("--experiment", choices=EXPERIMENTS,
                        help="Run one model in this isolated Compose stack.")
    args = parser.parse_args(argv)
    run(["docker", "build", "-t", "netlab-v5-client:latest", "client-image"])
    selected = SCENARIOS if args.scenario == "all" else tuple(s for s in SCENARIOS if s.id == args.scenario)
    for scenario in selected:
        experiments = scenario.experiments if args.experiment is None else (args.experiment,)
        if args.experiment is not None and args.experiment not in scenario.experiments:
            continue
        destination = ROOT / "artifacts-v5" / args.run_id / scenario.id
        destination.mkdir(parents=True, exist_ok=True)
        healthy_reset()
        events = []
        try:
            for experiment in experiments:
                events.extend({"experiment": experiment, **event}
                              for event in run_experiment(destination, scenario, experiment, args.only))
        finally:
            # A failed collector must never leak a partition or stopped node.
            if scenario.fault and scenario.fault.startswith("partition-"):
                try: restore_network(fault_plan(scenario.fault)["groups"][1])
                except Exception: pass
            if scenario.fault == "stop-mongo3":
                run([*COMPOSE, "up", "-d", "mongo3"])
        (destination / "run.json").write_text(json.dumps({"scenario": scenario.id, "only": args.only,
            "experiments": scenario.experiments, "events": events}, indent=2, default=str) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
