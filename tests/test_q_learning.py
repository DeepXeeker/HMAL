from hmal.models.tier1_q import TabularQSelector


def test_q_update_changes_value() -> None:
    q = TabularQSelector(modes=["Sense", "Idle"], alpha=0.5, gamma=0.9, epsilon=0.0)
    q.update("s0", "Sense", 1.0, "s1")
    assert q.q_table["s0"][0] != 0.0
