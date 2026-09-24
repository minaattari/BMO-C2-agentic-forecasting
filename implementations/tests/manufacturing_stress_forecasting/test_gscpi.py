"""Tests for the New York Fed GSCPI adapter and statistical feature panel."""

from pathlib import Path

import pandas as pd
import pytest
from manufacturing_stress_forecasting.features import (
    FEATURE_SERIES_IDS,
    GSCPI_SERIES_ID,
    STATISTICAL_FEATURE_SERIES_IDS,
)
from manufacturing_stress_forecasting.gscpi import NewYorkFedGSCPIAdapter, parse_gscpi_vintage_table


def _vintage_table() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Date": ["31-Dec-2023", "31-Jan-2024", "29-Feb-2024"],
            "Jan-24": [0.9, 1.0, "#N/A"],
            "Feb-24": [1.1, 1.2, "#N/A"],
        }
    )


def test_gscpi_parser_selects_latest_vintage_and_applies_release_lag() -> None:
    """The parser uses the newest vintage and an honest monthly release date."""
    frame = parse_gscpi_vintage_table(_vintage_table())

    assert frame["timestamp"].tolist() == [pd.Timestamp("2023-12-01"), pd.Timestamp("2024-01-01")]
    assert frame["value"].tolist() == pytest.approx([1.1, 1.2])
    assert frame["released_at"].tolist() == [pd.Timestamp("2024-01-05"), pd.Timestamp("2024-02-06")]


def test_gscpi_adapter_reads_an_existing_cache_without_network(tmp_path: Path) -> None:
    """A populated cache must avoid network access."""
    cache_path = tmp_path / "gscpi.csv"
    _vintage_table().to_csv(cache_path, index=False)

    frame = NewYorkFedGSCPIAdapter(cache_path=cache_path, url="https://invalid.example").fetch()

    assert frame["value"].tolist() == pytest.approx([1.1, 1.2])


def test_gscpi_is_registered_as_an_optional_challenger() -> None:
    """GSCPI stays outside the active statistical and LLM feature panels."""
    assert GSCPI_SERIES_ID not in FEATURE_SERIES_IDS
    assert STATISTICAL_FEATURE_SERIES_IDS == FEATURE_SERIES_IDS
