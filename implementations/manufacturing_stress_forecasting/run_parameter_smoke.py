"""Run a controlled deterministic parameter sweep for manufacturing stress."""

from __future__ import annotations

import argparse
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd
import yaml
from aieng.forecasting.data import DataService
from aieng.forecasting.evaluation import BacktestSpec, backtest
from aieng.forecasting.evaluation.backtest import BacktestResult
from aieng.forecasting.evaluation.predictor import Predictor
from aieng.forecasting.methods import HistoricalFrequencyPredictor
from manufacturing_stress_forecasting.data import build_manufacturing_stress_service
from manufacturing_stress_forecasting.predictors import (
    ManufacturingStressLogisticPredictor,
    ManufacturingStressXGBoostPredictor,
)


SPEC_PATH = Path(__file__).resolve().parent / "specs" / "manufacturing_stress_smoke.yaml"
BASELINE_NAME = "historical_frequency"
STAGE_WINDOWS = {
    "tune": (datetime(2000, 1, 1), datetime(2017, 12, 1)),
    "confirm": (datetime(2018, 1, 1), datetime(2024, 12, 1)),
}


@dataclass(frozen=True)
class Candidate:
    """Named predictor factory used by the controlled sweep."""

    name: str
    factory: Callable[[], Predictor]


CANDIDATES = (
    Candidate(
        "logistic_c_0_01",
        lambda: ManufacturingStressLogisticPredictor(regularization_c=0.01),
    ),
    Candidate(
        "logistic_c_0_1",
        lambda: ManufacturingStressLogisticPredictor(regularization_c=0.1),
    ),
    Candidate(
        "logistic_c_1_0",
        lambda: ManufacturingStressLogisticPredictor(regularization_c=1.0),
    ),
    Candidate(
        "xgb_25_depth1_lr0_05",
        lambda: ManufacturingStressXGBoostPredictor(
            n_estimators=25,
            max_depth=1,
            learning_rate=0.05,
        ),
    ),
    Candidate(
        "xgb_50_depth1_lr0_05",
        lambda: ManufacturingStressXGBoostPredictor(
            n_estimators=50,
            max_depth=1,
            learning_rate=0.05,
        ),
    ),
    Candidate(
        "xgb_50_depth2_lr0_03",
        lambda: ManufacturingStressXGBoostPredictor(
            n_estimators=50,
            max_depth=2,
            learning_rate=0.03,
        ),
    ),
    Candidate(
        "xgb_100_depth2_lr0_05",
        lambda: ManufacturingStressXGBoostPredictor(
            n_estimators=100,
            max_depth=2,
            learning_rate=0.05,
        ),
    ),
)


def _parse_args() -> argparse.Namespace:
    """Parse the sweep stage and forecast-origin stride."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stage",
        choices=tuple(STAGE_WINDOWS),
        default="tune",
        help="Tune all candidates or confirm exactly one previously selected candidate.",
    )
    parser.add_argument(
        "--candidate",
        choices=tuple(candidate.name for candidate in CANDIDATES),
        help="Candidate to evaluate during the confirm stage.",
    )
    parser.add_argument(
        "--stride",
        type=int,
        choices=(1, 3),
        default=3,
        help="Months between forecast origins. This does not change the forecast horizon.",
    )
    args = parser.parse_args()
    if args.stage == "confirm" and args.candidate is None:
        parser.error("--candidate is required when --stage confirm is selected.")
    if args.stage == "tune" and args.candidate is not None:
        parser.error("--candidate is only valid when --stage confirm is selected.")
    return args


def build_experiment_spec(base_spec: BacktestSpec, *, stage: str, stride: int) -> BacktestSpec:
    """Return the fixed tuning or confirmation window without changing the task."""
    if stage not in STAGE_WINDOWS:
        raise ValueError(f"Unknown stage {stage!r}; expected one of {tuple(STAGE_WINDOWS)}.")
    if stride not in (1, 3):
        raise ValueError(f"stride must be 1 or 3; got {stride}.")
    start, end = STAGE_WINDOWS[stage]
    return base_spec.model_copy(update={"start": start, "end": end, "stride": stride})


def predictors_for_stage(stage: str, candidate_name: str | None = None) -> list[tuple[str, Predictor]]:
    """Build the baseline plus all tuning candidates or one confirmation candidate."""
    if stage == "tune":
        selected = CANDIDATES
    elif stage == "confirm":
        if candidate_name is None:
            raise ValueError("candidate_name is required for the confirm stage.")
        matches = tuple(candidate for candidate in CANDIDATES if candidate.name == candidate_name)
        if not matches:
            raise ValueError(f"Unknown candidate {candidate_name!r}.")
        selected = matches
    else:
        raise ValueError(f"Unknown stage {stage!r}; expected one of {tuple(STAGE_WINDOWS)}.")

    return [
        (BASELINE_NAME, HistoricalFrequencyPredictor()),
        *((candidate.name, candidate.factory()) for candidate in selected),
    ]


def _scored_origin_keys(result: BacktestResult) -> set[tuple[datetime, datetime]]:
    """Return the exact origin and forecast-date pairs scored by one result."""
    return {(prediction.as_of, prediction.forecast_date) for prediction in result.predictions}


def validate_comparable_results(results: list[tuple[str, BacktestResult]]) -> None:
    """Reject comparisons that were not scored on identical dates."""
    if len(results) < 2:
        return
    reference_name, reference = results[0]
    reference_keys = _scored_origin_keys(reference)
    for name, result in results[1:]:
        keys = _scored_origin_keys(result)
        if keys != reference_keys:
            missing = len(reference_keys - keys)
            extra = len(keys - reference_keys)
            raise ValueError(
                f"Cannot compare {name} with {reference_name}: "
                f"scored origins differ (missing={missing}, extra={extra})."
            )


def run_candidates(
    named_predictors: list[tuple[str, Predictor]],
    *,
    spec: BacktestSpec,
    service: DataService,
) -> list[tuple[str, BacktestResult]]:
    """Backtest each named predictor without caches or LLM calls."""
    results: list[tuple[str, BacktestResult]] = []
    for name, predictor in named_predictors:
        print(f"Running {name}...")
        result = backtest(predictor=predictor, spec=spec, data_service=service)
        results.append((name, result))
    validate_comparable_results(results)
    return results


def comparison_table(results: list[tuple[str, BacktestResult]]) -> pd.DataFrame:
    """Summarize Brier score and skill relative to historical frequency."""
    result_by_name = dict(results)
    if BASELINE_NAME not in result_by_name:
        raise ValueError(f"Results must include {BASELINE_NAME}.")
    if any(result.metric != "brier" for _, result in results):
        raise ValueError("The parameter sweep requires binary Brier-score results.")

    baseline_brier = result_by_name[BASELINE_NAME].mean_score
    rows = []
    for name, result in results:
        skill = float("nan") if baseline_brier == 0 else 1.0 - result.mean_score / baseline_brier
        rows.append(
            {
                "candidate": name,
                "mean_brier": result.mean_score,
                "delta_vs_baseline": result.mean_score - baseline_brier,
                "brier_skill": skill,
                "scored": len(result.scores),
                "skipped": result.skipped_origins,
            }
        )
    return pd.DataFrame(rows).sort_values(["mean_brier", "candidate"]).reset_index(drop=True)


def _print_table(table: pd.DataFrame) -> None:
    """Print stable, readable score precision."""
    print(
        table.to_string(
            index=False,
            formatters={
                "mean_brier": "{:.4f}".format,
                "delta_vs_baseline": "{:+.4f}".format,
                "brier_skill": "{:+.1%}".format,
            },
        )
    )


def main() -> None:
    """Run the requested stage and report comparable deterministic scores."""
    args = _parse_args()
    with SPEC_PATH.open() as file:
        base_spec = BacktestSpec.model_validate(yaml.safe_load(file))

    spec = build_experiment_spec(base_spec, stage=args.stage, stride=args.stride)
    named_predictors = predictors_for_stage(args.stage, args.candidate)
    service = build_manufacturing_stress_service()

    print(
        f"Stage={args.stage}; origins={spec.start.date()} to {spec.end.date()}; "
        f"stride={spec.stride}; horizon={spec.task.horizons[0]} month(s)"
    )
    results = run_candidates(named_predictors, spec=spec, service=service)
    table = comparison_table(results)
    print()
    _print_table(table)

    if args.stage == "tune":
        best_model = table[table["candidate"] != BASELINE_NAME].iloc[0]
        candidate_name = str(best_model["candidate"])
        print(f"\nBest non-baseline tuning candidate: {candidate_name}")
        if float(best_model["brier_skill"]) <= 0:
            print("Historical frequency still has the lower tuning-period Brier score.")
        print("Confirm only this selected candidate with:")
        print(
            "uv run --directory implementations python -m "
            "manufacturing_stress_forecasting.run_parameter_smoke "
            f"--stage confirm --candidate {candidate_name} --stride {args.stride}"
        )
    else:
        print("\nConfirmation stage completed without evaluating the other candidates.")


if __name__ == "__main__":
    main()
