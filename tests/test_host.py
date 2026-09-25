from netlabv5.host import (SCENARIOS, delay_command, fault_plan, scenario_ids, tc_delay_script)


def test_requested_scenarios_replace_plain_partitions_with_dual_pold_arms():
    assert scenario_ids() == (
        "baseline",
        "between-delay",
        "between-partition-mongo12-vs-mongo3-client",
        "between-partition-mongo1-vs-mongo23-client",
        "between-stop-mongo3",
        "recover-delay",
        "recover-partition-mongo12-vs-mongo3-client",
        "recover-partition-mongo1-vs-mongo23-client",
        "recover-stop-mongo3",
    )
    assert all(s.experiments == ("ryw", "mr", "wfr", "mw") for s in SCENARIOS)
    pold = [s for s in SCENARIOS if s.phase == "pold-delay"]
    assert [s.id for s in pold] == [
        "between-partition-mongo12-vs-mongo3-client",
        "between-partition-mongo1-vs-mongo23-client",
    ]
    assert [s.fault for s in pold] == [
        "partition-mongo12-vs-mongo3-client",
        "partition-mongo1-vs-mongo23-client",
    ]


def test_fault_pair_uses_the_same_fault_name_for_remaining_recovery_arms():
    by_id = {scenario.id: scenario for scenario in SCENARIOS}
    for fault in ("delay", "partition-mongo12-vs-mongo3-client",
                  "partition-mongo1-vs-mongo23-client", "stop-mongo3"):
        assert by_id[f"between-{fault}"].fault == fault
        assert by_id[f"recover-{fault}"].fault == fault
    assert by_id["between-partition-mongo12-vs-mongo3-client"].phase == "pold-delay"
    assert by_id["recover-partition-mongo12-vs-mongo3-client"].phase == "before"


def test_pold_delay_targets_follow_the_partition_topology():
    from netlabv5.host import pold_delay_links, pold_second_uri
    assert pold_delay_links("partition-mongo12-vs-mongo3-client") == (
        ("mongo1", ("mongo3",)), ("mongo2", ("mongo3",)),
    )
    assert pold_second_uri("partition-mongo12-vs-mongo3-client") == "mongodb://mongo3:27017/?directConnection=true"
    assert pold_delay_links("partition-mongo1-vs-mongo23-client") == (
        ("mongo1", ("mongo2", "mongo3")),
    )
    assert "mongo2:27017,mongo3:27017" in pold_second_uri("partition-mongo1-vs-mongo23-client")



def test_cells_filter_accepts_numeric_write_concern_text():
    from netlabv5.matrix import cells
    rows = cells("rc=local,wc=1,preference=primary,causal=off")
    assert len(rows) == 1
    assert rows[0]["wc"] == 1
    assert fault_plan("delay") == {"kind": "delay", "targets": ("mongo3",)}
    assert fault_plan("partition-mongo1-vs-mongo23-client")["groups"] == (
        ("mongo2", "mongo3", "labclient"), ("mongo1",),
    )



def test_pold_delay_targets_mongo1_egress_to_both_future_majority_members():
    script = tc_delay_script(["172.30.0.3", "172.30.0.4"], 60_000)
    assert "netem delay 60000ms 0ms" in script
    assert "match ip dst 172.30.0.3/32" in script
    assert "match ip dst 172.30.0.4/32" in script


def test_delay_reuses_the_original_post_action_degrade_parameters():
    assert delay_command() == [
        "netem", "--duration", "2h", "combine", "--delay", "--delay-time", "100",
        "--delay-jitter", "20", "--loss", "--loss-percent", "3", "--", "netlab-v5-mongo3",
    ]
