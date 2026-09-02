"""Leak-safe monthly features for the manufacturing-stress MVP."""

from __future__ import annotations

import pandas as pd
from aieng.forecasting.data.features import canonical_three_col


IPMAN_CHANGE_1M_SERIES_ID = "ipman_change_1m_pct"
IPMAN_CHANGE_3M_SERIES_ID = "ipman_change_3m_pct"
IPMAN_CHANGE_6M_SERIES_ID = "ipman_change_6m_pct"
IPMAN_CHANGE_12M_SERIES_ID = "ipman_change_12m_pct"

FEATURE_PERIODS: dict[str, int] = {
    IPMAN_CHANGE_1M_SERIES_ID: 1,
    IPMAN_CHANGE_3M_SERIES_ID: 3,
    IPMAN_CHANGE_6M_SERIES_ID: 6,
    IPMAN_CHANGE_12M_SERIES_ID: 12,
}
FEATURE_SERIES_IDS: tuple[str, ...] = tuple(FEATURE_PERIODS)


def apply_conservative_monthly_release_lag(frame: pd.DataFrame, months: int = 1) -> pd.DataFrame:
    """Stamp observations as available ``months`` after their reference month.

    The standard FRED adapter uses ``released_at = timestamp`` because it does
    not retrieve release vintages. For this monthly prototype, one month is a
    deliberately conservative approximation that prevents a month-start
    forecast from seeing that same month's completed production observation.
    """
    if months < 0:
        raise ValueError(f"months must be non-negative; got {months}")
    out = frame.copy()
    out["released_at"] = pd.to_datetime(out["timestamp"]) + pd.offsets.MonthBegin(months)
    return canonical_three_col(out)


def percent_change_feature(ipman: pd.DataFrame, periods: int) -> pd.DataFrame:
    """Return the trailing ``periods``-month IPMAN percentage change."""
    if periods < 1:
        raise ValueError(f"periods must be positive; got {periods}")
    out = ipman.copy().sort_values("timestamp").reset_index(drop=True)
    out["value"] = out["value"].pct_change(periods=periods, fill_method=None) * 100.0
    return canonical_three_col(out)


def build_ipman_feature_frames(ipman: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Build the four small momentum features used by the first baseline."""
    return {series_id: percent_change_feature(ipman, periods) for series_id, periods in FEATURE_PERIODS.items()}


def build_feature_snapshot(
    origin: pd.Timestamp,
    feature_frames: dict[str, pd.DataFrame],
) -> dict[str, float] | None:
    """Return the latest feature values that were published by ``origin``.

    Filtering on ``released_at`` here is essential when reconstructing older
    training examples: the surrounding ``ForecastContext`` protects the current
    forecast origin, while this function recreates the stricter cutoff at each
    past origin used to train the fit-at-origin logistic model.
    """
    snapshot: dict[str, float] = {}
    for series_id in FEATURE_SERIES_IDS:
        frame = feature_frames[series_id]
        visible = frame[pd.to_datetime(frame["released_at"]) <= origin]
        if visible.empty:
            return None
        snapshot[series_id] = float(visible.sort_values("timestamp")["value"].iloc[-1])
    return snapshot


__all__ = [
    "FEATURE_PERIODS",
    "FEATURE_SERIES_IDS",
    "IPMAN_CHANGE_1M_SERIES_ID",
    "IPMAN_CHANGE_3M_SERIES_ID",
    "IPMAN_CHANGE_6M_SERIES_ID",
    "IPMAN_CHANGE_12M_SERIES_ID",
    "apply_conservative_monthly_release_lag",
    "build_feature_snapshot",
    "build_ipman_feature_frames",
    "percent_change_feature",
]
