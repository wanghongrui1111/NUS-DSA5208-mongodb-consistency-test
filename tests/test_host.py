from netlabv5.host import SCENARIOS, delay_command, fault_plan, scenario_ids


def test_requested_scenarios_are_present_in_execution_order():
    assert scenario_ids() == (
        "baseline",
        "partition-ryw-mr",
        "stop-mongo3",
        "recover-delay",
        "recover-partition-mongo12-vs-mongo3-client",
        "recover-partition-mongo1",
        "recover-partition-mongo2",
        "recover-partition-mongo3",
        "recover-partition-client",
    )
    assert SCENARIOS[1].experiments == ("ryw", "mr")


def test_fault_plans_separate_delay_and_all_requested_partition_shapes():
    assert fault_plan("delay") == {"kind": "delay", "targets": ("mongo3",)}
    assert fault_plan("partition-mongo12-vs-mongo3-client")["groups"] == (
        ("mongo1", "mongo2"), ("mongo3", "labclient"),
    )


def test_delay_reuses_the_original_post_action_degrade_parameters():
    assert delay_command() == [
        "netem", "--duration", "2h", "combine", "--delay", "--delay-time", "100",
        "--delay-jitter", "20", "--loss", "--loss-percent", "3", "--", "netlab-v5-mongo3",
    ]
