"""Tests for the controlled manufacturing-stress parameter sweep."""

from datetime import datetime

import pytest
from aieng.forecasting.evaluation import BacktestSpec, ForecastingTask
from aieng.forecasting.evaluation.backtest import BacktestResult
from aieng.forecasting.evaluation.prediction import BinaryForecast, Prediction
from manufacturing_stress_forecasting.run_parameter_smoke import (
    BASELINE_NAME,
    CANDIDATES,
    build_experiment_spec,
    comparison_table,
    predictors_for_stage,
)


def _base_spec() -> BacktestSpec:
    return BacktestSpec(
        task=ForecastingTask(
            task_id="manufacturing_stress_3m",
            target_series_id="manufacturing_stress",
            horizons=[3],
            frequency="MS",
            payload_type="binary",
            description="Manufacturing stress three months ahead",
        ),
        start=datetime(2018, 1, 1),
        end=datetime(2024, 12, 1),
        stride=3,
        warmup=60,
    )


def _result(predictor_id: str, score: float) -> BacktestResult:
    prediction = Prediction(
        predictor_id=predictor_id,
        task_id=_base_spec().task.task_id,
        issued_at=datetime(2026, 1, 1),
        as_of=datetime(2020, 1, 1),
        forecast_date=datetime(2020, 4, 1),
        payload=BinaryForecast(probability=0.1),
    )
    return BacktestResult(
        spec=_base_spec(),
        predictor_id=predictor_id,
        predictions=[prediction],
        scores=[score],
        metric="brier",
        mean_score=score,
        ran_at=datetime(2026, 1, 1),
    )


def test_stage_windows_preserve_the_forecasting_task() -> None:
    base = _base_spec()

    tuning = build_experiment_spec(base, stage="tune", stride=1)
    confirmation = build_experiment_spec(base, stage="confirm", stride=3)

    assert tuning.start == datetime(2000, 1, 1)
    assert tuning.end == datetime(2017, 12, 1)
    assert tuning.stride == 1
    assert confirmation.start == datetime(2018, 1, 1)
    assert confirmation.end == datetime(2024, 12, 1)
    assert confirmation.stride == 3
    assert tuning.task == base.task
    assert confirmation.task == base.task


def test_tuning_stage_builds_unique_named_candidates_after_baseline() -> None:
    names = [name for name, _predictor in predictors_for_stage("tune")]

    assert names[0] == BASELINE_NAME
    assert len(names) == len(CANDIDATES) + 1
    assert len(names) == len(set(names))


def test_confirmation_stage_builds_only_the_selected_candidate() -> None:
    selected = CANDIDATES[0].name

    names = [name for name, _predictor in predictors_for_stage("confirm", selected)]

    assert names == [BASELINE_NAME, selected]


def test_confirmation_stage_requires_a_candidate() -> None:
    with pytest.raises(ValueError, match="candidate_name is required"):
        predictors_for_stage("confirm")


def test_comparison_table_reports_skill_against_historical_frequency() -> None:
    table = comparison_table(
        [
            (BASELINE_NAME, _result(BASELINE_NAME, 0.04)),
            ("candidate", _result("candidate", 0.03)),
        ]
    )

    candidate = table.set_index("candidate").loc["candidate"]
    assert candidate["delta_vs_baseline"] == pytest.approx(-0.01)
    assert candidate["brier_skill"] == pytest.approx(0.25)
