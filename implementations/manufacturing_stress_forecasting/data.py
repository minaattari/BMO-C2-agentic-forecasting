"""FRED/IPMAN data service for the manufacturing-stress MVP."""

from __future__ import annotations

from pathlib import Path

from aieng.forecasting.data import DataService, SeriesMetadata
from aieng.forecasting.data.adapters import FREDAdapter
from aieng.forecasting.data.features import StaticFrameAdapter
from manufacturing_stress_forecasting.features import (
    FEATURE_PERIODS,
    apply_conservative_monthly_release_lag,
    build_ipman_feature_frames,
)
from manufacturing_stress_forecasting.targets import (
    DEFAULT_LOOKBACK_MONTHS,
    DEFAULT_STRESS_THRESHOLD_PCT,
    derive_manufacturing_stress_labels,
)


IPMAN_FRED_ID = "IPMAN"
IPMAN_SERIES_ID = "ipman_us_manufacturing_production"
STRESS_SERIES_ID = "manufacturing_stress"

_REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FRED_CACHE_DIR = _REPO_ROOT / "data" / "fred"


def build_manufacturing_stress_service(
    *,
    cache_dir: str | Path = DEFAULT_FRED_CACHE_DIR,
    refresh: bool = False,
    release_lag_months: int = 1,
    stress_lookback_months: int = DEFAULT_LOOKBACK_MONTHS,
    stress_threshold_pct: float = DEFAULT_STRESS_THRESHOLD_PCT,
) -> DataService:
    """Build a service containing IPMAN, momentum features, and stress labels."""
    raw_ipman = FREDAdapter(IPMAN_FRED_ID, cache_dir=cache_dir, refresh=refresh).fetch()
    ipman = apply_conservative_monthly_release_lag(raw_ipman, months=release_lag_months)
    feature_frames = build_ipman_feature_frames(ipman)
    stress = derive_manufacturing_stress_labels(
        ipman,
        lookback_months=stress_lookback_months,
        threshold_pct=stress_threshold_pct,
    )

    service = DataService()
    service.register(
        IPMAN_SERIES_ID,
        StaticFrameAdapter(ipman),
        SeriesMetadata(
            series_id=IPMAN_SERIES_ID,
            description="U.S. manufacturing industrial production index (IPMAN)",
            source="FRED (IPMAN)",
            units="Index",
            frequency="MS",
        ),
    )

    for series_id, frame in feature_frames.items():
        periods = FEATURE_PERIODS[series_id]
        service.register(
            series_id,
            StaticFrameAdapter(frame),
            SeriesMetadata(
                series_id=series_id,
                description=f"Trailing {periods}-month percentage change in IPMAN",
                source="Derived from FRED IPMAN",
                units="Percent",
                frequency="MS",
            ),
        )

    service.register(
        STRESS_SERIES_ID,
        StaticFrameAdapter(stress),
        SeriesMetadata(
            series_id=STRESS_SERIES_ID,
            description=(
                "Binary U.S. manufacturing stress label: 1 when trailing "
                f"{stress_lookback_months}-month IPMAN change is at or below {stress_threshold_pct:.1f}%"
            ),
            source="Derived from FRED IPMAN",
            units="Binary event (0=no stress, 1=stress)",
            frequency="MS",
        ),
    )
    return service


__all__ = [
    "DEFAULT_FRED_CACHE_DIR",
    "IPMAN_FRED_ID",
    "IPMAN_SERIES_ID",
    "STRESS_SERIES_ID",
    "build_manufacturing_stress_service",
]
