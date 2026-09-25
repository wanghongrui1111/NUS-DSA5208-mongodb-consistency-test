from netlabv5.judge import check, judge


def operation(kind, ok=True, value=None, acknowledged=True):
    return {"op": kind, "ok": ok, "value": value, "acknowledged": acknowledged}


def test_judge_marks_observable_read_guarantees_but_not_mw():
    record = {
        "v1": 1,
        "v2": 2,
        "ops": [
            operation("write1"), operation("read1", value=1),
            operation("write2"), operation("read2", value=2),
        ],
    }
    assert judge(record) == {"RYW": "holds", "MR": "holds", "MW": "inconclusive", "WFR": "holds"}


def test_judge_is_inconclusive_when_an_operation_errors():
    record = {
        "v1": 1,
        "v2": 2,
        "ops": [
            operation("write1"), operation("read1", ok=False),
            operation("write2"), operation("read2", value=2),
        ],
    }
    assert judge(record)["RYW"] == "inconclusive"
    assert judge(record)["WFR"] == "inconclusive"


def test_judge_is_inconclusive_when_a_successful_read_has_no_document_value():
    record = {
        "v1": 1,
        "v2": 2,
        "ops": [
            operation("write1", acknowledged=False), operation("read1", value=None),
            operation("write2", acknowledged=False), operation("read2", value=None),
        ],
    }
    assert judge(record) == {"RYW": "inconclusive", "MR": "inconclusive", "MW": "inconclusive", "WFR": "inconclusive"}


def test_mw_is_inconclusive_when_this_single_primary_sequence_has_two_acks():
    record = {
        "v1": 1,
        "v2": 2,
        "ops": [
            operation("write1"), operation("read1", value=None),
            operation("write2"), operation("read2", value=None),
        ],
    }
    assert judge(record)["MW"] == "inconclusive"


def test_ryw_w0_is_checked_from_the_observed_operations():
    record = {
        "experiment": "ryw", "wc": 0, "v1": 7,
        "ops": [operation("write1", acknowledged=False), operation("read1", value=7)],
    }
    assert check(record) == "holds"


def test_mw_uses_the_w2_primary_oplog_history():
    record = {
        "experiment": "mw",
        "ops": [
            {"op": "write1", "tag": "W1", "ok": True},
            {"op": "write2", "tag": "W2", "ok": True,
             "command": {"server": "mongo2:27017"},
             "oplog": {"mongo2": [
                 {"tag": "W1"}, {"tag": "W2"},
             ]}},
        ],
    }
    assert check(record) == "holds"


def test_mw_detects_w2_on_a_history_missing_w1():
    record = {
        "experiment": "mw",
        "ops": [
            {"op": "write1", "tag": "W1", "ok": True},
            {"op": "write2", "tag": "W2", "ok": True,
             "command": {"server": "mongo2:27017"},
             "oplog": {"mongo2": [{"tag": "W2"}]}},
        ],
    }
    assert check(record) == "violated"


def test_mw_uses_the_explicit_post_w2_pre_heal_snapshot_not_legacy_oplog():
    record = {
        "experiment": "mw",
        "ops": [
            {"op": "write1", "tag": "W1", "ok": True},
            {"op": "write2", "tag": "W2", "ok": True,
             "command": {"server": "mongo2:27017"},
             "oplog": {"mongo2": [{"tag": "W1"}, {"tag": "W2"}]},
             "oplog_after_successor_ack": {"mongo2": [{"tag": "W2"}]}},
        ],
    }
    assert check(record) == "violated"


def test_wfr_detects_a_successor_branch_missing_the_exact_source_read_by_r1():
    record = {
        "experiment": "wfr",
        "ops": [
            {"op": "seed", "tag": "source", "ok": True},
            {"op": "read1", "ok": True, "value": 1, "source_write_id": "source"},
            {"op": "write1", "tag": "successor", "ok": True,
             "command": {"server": "mongo2:27017"},
             "oplog_after_successor_ack": {"mongo2": [{"tag": "successor"}]}},
        ],
    }
    assert check(record) == "violated"



def test_wfr_pold_delay_uses_the_delayed_source_write_not_the_seed_as_predecessor():
    record = {
        "experiment": "wfr",
        "ops": [
            {"op": "seed", "tag": "seed", "ok": True},
            {"op": "source", "tag": "source", "ok": True},
            {"op": "read1", "ok": True, "value": 1, "source_write_id": "source"},
            {"op": "write1", "tag": "successor", "ok": True,
             "command": {"server": "mongo2:27017"},
             "oplog_after_successor_ack": {"mongo2": [{"tag": "successor"}]}}
        ],
    }
    assert check(record) == "violated"
    record = {
        "experiment": "wfr",
        "ops": [
            {"op": "seed", "tag": "source-current", "ok": True},
            {"op": "read1", "ok": True, "value": 1, "source_write_id": "source-old"},
            {"op": "write1", "tag": "successor", "ok": True,
             "command": {"server": "mongo2:27017"},
             "oplog_after_successor_ack": {"mongo2": [{"tag": "source-old"}, {"tag": "successor"}]}},
        ],
    }
    assert check(record) == "inconclusive"
