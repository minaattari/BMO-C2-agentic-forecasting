from manufacturing_stress_forecasting.hybrid import NumericalAnchor, validate_agent_adjustment


def test_numerical_anchor_averages_the_two_fixed_candidates() -> None:
    anchor = NumericalAnchor(logistic_probability=0.08, xgboost_probability=0.12)

    assert anchor.probability == 0.1
    assert anchor.as_dict()["anchor_method"] == "mean_logistic_xgboost"


def test_agent_adjustment_is_clamped_and_official_probability_stays_at_anchor() -> None:
    result = validate_agent_adjustment(0.08, 0.20, max_adjustment=0.03)

    assert result["agent_adjustment"] == 0.03
    assert result["shadow_probability"] == 0.11
    assert result["official_probability"] == 0.08
    assert result["validation_status"] == "clamped"
