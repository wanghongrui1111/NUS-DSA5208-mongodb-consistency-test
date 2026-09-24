from netlabv5.matrix import CELLS, PREFERENCES, cells


def test_matrix_is_the_requested_two_by_two_by_three_by_two_space():
    space = cells()
    assert len(space) == 24
    assert {row["rc"] for row in space} == {"local", "majority"}
    assert {row["wc"] for row in space} == {1, "majority"}
    assert {row["preference"] for row in space} == {"primary", "primaryPreferred", "secondaryPreferred"}
    assert {row["causal"] for row in space} == {False, True}
    assert PREFERENCES == ("primary", "primaryPreferred", "secondaryPreferred")


def test_cell_order_and_filter_are_deterministic():
    assert CELLS[0]["id"] == "rc=local|wc=1|pref=primary|causal=off"
    assert CELLS[-1]["id"] == "rc=majority|wc=majority|pref=secondaryPreferred|causal=on"
    assert cells("rc=majority,wc=majority,preference=secondaryPreferred,causal=on") == [CELLS[-1]]
