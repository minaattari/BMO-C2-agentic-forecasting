"""Focused tests for label construction and historical feature cutoffs."""

import pandas as pd
import pytest
from manufacturing_stress_forecasting.features import (
    CPI_YOY_SERIES_ID,
    FEATURE_SERIES_IDS,
    FED_FUNDS_SERIES_ID,
    SPY_RETURN_3M_SERIES_ID,
    SPY_RETURN_12M_SERIES_ID,
    XLI_RETURN_3M_SERIES_ID,
    XLI_RETURN_12M_SERIES_ID,
    YIELD_CURVE_SERIES_ID,
    build_feature_snapshot,
    build_macro_feature_frames,
)
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


def test_macro_features_use_month_end_values_with_next_business_day_release() -> None:
    timestamps = pd.to_datetime(["2024-01-30", "2024-01-31", "2024-02-28", "2024-02-29"])

    def frame(values: list[float]) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "timestamp": timestamps,
                "value": values,
                "released_at": timestamps,
            }
        )

    features = build_macro_feature_frames(
        frame([5.30, 5.31, 5.32, 5.33]),
        frame([4.00, 4.10, 4.20, 4.30]),
        frame([4.40, 4.50, 4.55, 4.60]),
    )

    fed = features[FED_FUNDS_SERIES_ID]
    spread = features[YIELD_CURVE_SERIES_ID]

    assert fed["timestamp"].tolist() == [pd.Timestamp("2024-01-01"), pd.Timestamp("2024-02-01")]
    assert fed["value"].tolist() == pytest.approx([5.31, 5.33])
    assert fed["released_at"].tolist() == [pd.Timestamp("2024-02-01"), pd.Timestamp("2024-03-01")]
    assert spread["value"].tolist() == pytest.approx([-0.40, -0.30])
    assert spread["released_at"].tolist() == [pd.Timestamp("2024-02-01"), pd.Timestamp("2024-03-01")]


def test_expanded_macro_features_include_cpi_yoy_and_monthly_market_return() -> None:
    timestamps = pd.date_range("2023-01-01", periods=13, freq="MS")

    def frame(values: list[float]) -> pd.DataFrame:
        return pd.DataFrame({"timestamp": timestamps, "value": values, "released_at": timestamps})

    features = build_macro_feature_frames(
        frame([5.0] * 13),
        frame([4.0] * 13),
        frame([3.0] * 13),
        frame([100.0] + [100.0] * 11 + [110.0]),
        frame([4.0] * 13),
        frame([200.0] * 13),
        frame([15.0] * 13),
        frame([300.0] * 13),
        frame([100.0 + 5.0 * index for index in range(13)]),
        frame([100.0] * 13),
    )

    assert features[CPI_YOY_SERIES_ID]["value"].iloc[-1] == pytest.approx(10.0)
    assert features[SPY_RETURN_3M_SERIES_ID]["value"].iloc[-1] == pytest.approx(100.0 * 15.0 / 145.0)
    assert features[SPY_RETURN_12M_SERIES_ID]["value"].iloc[-1] == pytest.approx(60.0)
    assert features[XLI_RETURN_3M_SERIES_ID]["value"].iloc[-1] == pytest.approx(0.0)
    assert features[XLI_RETURN_12M_SERIES_ID]["value"].iloc[-1] == pytest.approx(0.0)
