"""Pure checks for one small consistency experiment at a time."""


def _by_name(record):
    return {op["op"]: op for op in record["ops"]}


def _usable(op):
    return bool(op and op.get("ok"))


def _usable_value(op):
    return _usable(op) and op.get("value") is not None


def judge(record):
    """Keep the former four-step checker for reading old result files."""
    ops = _by_name(record)
    w1, r1 = ops.get("write1"), ops.get("read1")
    w2, r2 = ops.get("write2"), ops.get("read2")
    v1, v2 = record["v1"], record["v2"]
    return {
        "RYW": "holds" if _usable(w1) and _usable_value(r1) and r1["value"] >= v1
        else "violated" if _usable(w1) and _usable_value(r1) else "inconclusive",
        "MR": "holds" if _usable_value(r1) and _usable_value(r2) and r2["value"] >= r1["value"]
        else "violated" if _usable_value(r1) and _usable_value(r2) else "inconclusive",
        "MW": "inconclusive",
        "WFR": "holds" if _usable_value(r1) and _usable(w2) and _usable_value(r2) and r2["value"] >= v2
        else "violated" if _usable_value(r1) and _usable(w2) and _usable_value(r2) else "inconclusive",
    }


def _tag(entry):
    if "tag" in entry:  # Small synthetic records used by unit tests.
        return entry["tag"]
    update = entry.get("o", {})
    return update.get("write_id") or update.get("diff", {}).get("u", {}).get("write_id")


def _entries(op, node, snapshot_field="oplog"):
    snapshot = op.get(snapshot_field, {}).get(node, [])
    return snapshot.get("entries", []) if isinstance(snapshot, dict) else snapshot


def _history(predecessor, successor):
    if not (_usable(predecessor) and _usable(successor)):
        return "inconclusive"
    command = successor.get("command") or {}
    server = command.get("server")
    if not server:
        return "inconclusive"
    # New P_old records preserve the exact post-W2/pre-heal snapshot under an
    # explicit field.  Keep ``oplog`` only as a compatibility fallback for
    # older artifacts that cannot be retroactively retimed.
    snapshot_field = ("oplog_after_successor_ack"
                      if "oplog_after_successor_ack" in successor else "oplog")
    entries = _entries(successor, server.split(":", 1)[0], snapshot_field)
    tags = [_tag(entry) for entry in entries]
    if successor.get("tag") not in tags:
        return "inconclusive"
    if predecessor.get("tag") not in tags:
        return "violated"
    return "holds" if tags.index(predecessor["tag"]) < tags.index(successor["tag"]) else "violated"


def check(record):
    """Check one experiment from its raw result and its target-node oplog snapshot."""
    ops = _by_name(record)
    experiment = record["experiment"]
    if experiment == "ryw":
        w1, r1 = ops.get("write1"), ops.get("read1")
        return "holds" if _usable(w1) and _usable_value(r1) and r1["value"] >= record["v1"] \
            else "violated" if _usable(w1) and _usable_value(r1) else "inconclusive"
    if experiment == "mr":
        r1, r2 = ops.get("read1"), ops.get("read2")
        return "holds" if _usable_value(r1) and _usable_value(r2) and r2["value"] >= r1["value"] \
            else "violated" if _usable_value(r1) and _usable_value(r2) else "inconclusive"
    if experiment == "mw":
        return _history(ops.get("write1"), ops.get("write2"))
    if experiment == "wfr":
        seed, r1, w1 = ops.get("seed"), ops.get("read1"), ops.get("write1")
        # WFR only concerns the exact source version R1 observed.  A stale
        # document/tag from an older attempt is not evidence for this attempt.
        if not (_usable(seed) and _usable_value(r1) and r1.get("source_write_id") == seed.get("tag")):
            return "inconclusive"
        return _history({"ok": True, "tag": seed["tag"]}, w1)
    raise ValueError(f"unknown experiment {experiment!r}")
