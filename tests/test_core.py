from hmal.coalition.core import evaluate_core_feasibility


def test_core_feasibility_outputs_keys() -> None:
    result = evaluate_core_feasibility(
        grand_coalition=["a", "b"],
        coalition_worth={("a",): 1.0, ("b",): 1.0, ("a", "b"): 1.5},
        allocations={"a": 0.8, "b": 0.7},
    )
    assert "violation_rate" in result
    assert "violation_margin" in result
