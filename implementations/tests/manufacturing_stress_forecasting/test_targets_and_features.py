"""Focused tests for label construction and historical feature cutoffs."""

import pandas as pd
import pytest
from manufacturing_stress_forecasting.features import FEATURE_SERIES_IDS, build_feature_snapshot
from manufacturing_stress_forecasting.targets import derive_manufacturing_stress_labels


def test_stress_label_uses_trailing_three_month_decline() -> None:
    dates = pd.date_range("2024-01-01", periods=5, freq="MS")
    ipman = pd.DataFrame(
        {
            "timestamp": dates,
            "value": [100.0, 100.0, 100.0, 100.0, 97.9],
            "released_at": dates + pd.offsets.MonthBegin(1),
        }
    )

    labels = derive_manufacturing_stress_labels(ipman)

    assert labels["value"].tolist() == [0.0, 1.0]
    assert labels["timestamp"].tolist() == [pd.Timestamp("2024-04-01"), pd.Timestamp("2024-05-01")]
    assert labels["released_at"].tolist() == [pd.Timestamp("2024-05-01"), pd.Timestamp("2024-06-01")]


def test_feature_snapshot_ignores_values_released_after_origin() -> None:
    origin = pd.Timestamp("2024-03-01")
    frames: dict[str, pd.DataFrame] = {}
    for index, series_id in enumerate(FEATURE_SERIES_IDS):
        frames[series_id] = pd.DataFrame(
            {
                "timestamp": [pd.Timestamp("2024-01-01"), pd.Timestamp("2024-02-01")],
                "value": [float(index), 999.0],
                "released_at": [pd.Timestamp("2024-02-01"), pd.Timestamp("2024-04-01")],
            }
        )

    snapshot = build_feature_snapshot(origin, frames)

    assert snapshot is not None
    for index, series_id in enumerate(FEATURE_SERIES_IDS):
        assert snapshot[series_id] == pytest.approx(float(index))
