from pathlib import Path

from netlabv5.client import (EXPERIMENTS, barrier_paths, finish_record, partition_timeout_options,
                             pre_action_paths, seed_is_converged, seed_successor_session, session_for, tag)


def test_finish_record_can_preserve_raw_operations_without_a_consistency_verdict():
    row = {"id": "cell", "v1": 1, "v2": 2}
    record = finish_record(row, [{"op": "write1", "ok": True}], "session", judge_results=False)
    assert record["ops"] == [{"op": "write1", "ok": True}]
    assert "consistency" not in record


def test_w0_does_not_create_a_session_or_enable_causality():
    class Client:
        def start_session(self, **kwargs):
            raise AssertionError(f"unexpected session: {kwargs}")

    assert session_for(Client(), {"wc": 0, "causal": True}) is None


def test_between_operation_barrier_paths_are_unique_per_cell():
    ready, release, release2, done, proceed = barrier_paths(Path("/tmp/barriers"), "mw", {"id": "cell"})
    assert (ready.name, release.name, done.name, proceed.name) == (
        "mw__cell.ready", "mw__cell.release", "mw__cell.done", "mw__cell.proceed",
    )


def test_pre_action_barrier_precedes_mw_write1():
    ready, release = pre_action_paths(Path("/tmp/barriers"), "mw", {"id": "cell"})
    assert (ready.name, release.name) == ("mw__cell.pre_ready", "mw__cell.pre_release")



def test_seed_convergence_requires_the_exact_seed_write_id_on_every_node():
    expected = "seed-attempt"
    assert seed_is_converged({"mongo1": expected, "mongo2": expected, "mongo3": expected}, expected)
    assert not seed_is_converged({"mongo1": expected, "mongo2": None, "mongo3": expected}, expected)
    assert not seed_is_converged({"mongo1": expected, "mongo2": "older-seed", "mongo3": expected}, expected)



def test_pold_delay_adds_a_source_write_when_action1_is_a_read():
    from netlabv5.client import pold_needs_source
    assert pold_needs_source("mr")
    assert pold_needs_source("wfr")
    assert not pold_needs_source("ryw")
    assert not pold_needs_source("mw")


def test_operation_tag_includes_the_unique_attempt_id():
    class Collection:
        name = "mw__cell"

    assert tag(Collection(), "write1", "attempt-uuid") == "mw__cell|attempt-uuid|write1"



def test_successor_session_receives_the_predecessor_causal_times():
    class Session:
        cluster_time = {"clusterTime": "signed"}
        operation_time = "operation-time"

        def __init__(self):
            self.cluster = []
            self.operations = []

        def advance_cluster_time(self, value):
            self.cluster.append(value)

        def advance_operation_time(self, value):
            self.operations.append(value)

    successor = Session()
    seed_successor_session(Session(), successor)
    assert successor.cluster == [{"clusterTime": "signed"}]
    assert successor.operations == ["operation-time"]

    assert EXPERIMENTS == {
        "ryw": ("write1", "read1"),
        "mr": ("read1", "read2"),
        "wfr": ("read1", "write1"),
        "mw": ("write1", "write2"),
    }


def test_partition_timeout_options_bound_expected_unavailability_waits():
    assert partition_timeout_options(2500) == {
        "serverSelectionTimeoutMS": 2500,
        "connectTimeoutMS": 2500,
        "socketTimeoutMS": 3500,
    }
