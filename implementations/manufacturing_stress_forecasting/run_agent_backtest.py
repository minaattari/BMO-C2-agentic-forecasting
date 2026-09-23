"""Run the cached, token-limited manufacturing-stress agent backtest."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml
from aieng.forecasting.data import DataService
from aieng.forecasting.evaluation import BacktestSpec, backtest
from aieng.forecasting.evaluation.artifacts import load_backtest_result, save_backtest_result
from aieng.forecasting.evaluation.backtest import BacktestResult
from aieng.forecasting.evaluation.predictor import Predictor
from aieng.forecasting.methods import HistoricalFrequencyPredictor
from manufacturing_stress_forecasting.analyst_agent import build_manufacturing_stress_agent_predictor
from manufacturing_stress_forecasting.data import build_manufacturing_stress_service
from manufacturing_stress_forecasting.predictors import (
    ManufacturingStressLogisticPredictor,
    ManufacturingStressXGBoostPredictor,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = Path(__file__).resolve().parent / "specs" / "manufacturing_stress_smoke.yaml"
STORE_DIR = REPO_ROOT / "data" / "predictions"
SPEC_ID = "manufacturing_stress_smoke_llmp_v1"


def _parse_args() -> argparse.Namespace:
    """Parse explicit controls for the paid backtest."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Re-run predictors and overwrite cached results.",
    )
    return parser.parse_args()


def _run_or_load(
    predictor: Predictor,
    spec: BacktestSpec,
    service: DataService,
    *,
    force_refresh: bool,
) -> BacktestResult:
    """Load one cached result or run it with one retry and persist it."""
    predictor_id = predictor.predictor_id
    if not force_refresh:
        cached = load_backtest_result(SPEC_ID, predictor_id, store_dir=STORE_DIR)
        if cached is not None:
            print(f"{predictor_id}: loaded {STORE_DIR / SPEC_ID / (predictor_id + '.yaml')}")
            return cached

    result = backtest(
        predictor=predictor,
        spec=spec,
        data_service=service,
        max_retries=1,
        retry_delay=1.0,
    )
    path = save_backtest_result(result, spec_id=SPEC_ID, store_dir=STORE_DIR)
    print(f"{predictor_id}: saved {path}")
    return result


def main() -> None:
    """Run all predictors under the identical binary Brier-score harness."""
    args = _parse_args()
    with SPEC_PATH.open() as file:
        spec = BacktestSpec.model_validate(yaml.safe_load(file))

    service = build_manufacturing_stress_service()
    predictors = [
        HistoricalFrequencyPredictor(),
        ManufacturingStressLogisticPredictor(),
        ManufacturingStressXGBoostPredictor(),
        build_manufacturing_stress_agent_predictor(),
    ]
    for predictor in predictors:
        result = _run_or_load(predictor, spec, service, force_refresh=args.force_refresh)
        print(
            f"{result.predictor_id}: {result.mean_score:.4f} mean {result.metric}; "
            f"scored={len(result.scores)} skipped={result.skipped_origins}"
        )


if __name__ == "__main__":
    main()
