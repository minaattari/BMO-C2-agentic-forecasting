"""New York Fed Global Supply Chain Pressure Index data adapter."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd
from aieng.forecasting.data.adapters.base import BaseAdapter
from aieng.forecasting.data.features import canonical_three_col
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay


GSCPI_DATA_URL = "https://www.newyorkfed.org/medialibrary/research/interactives/data/gscpi/gscpi_interactive_data.csv"

_US_FEDERAL_BUSINESS_DAY = CustomBusinessDay(calendar=USFederalHolidayCalendar())


def _fourth_business_day_of_next_month(timestamp: pd.Timestamp) -> pd.Timestamp:
    """Return the New York Fed's approximate GSCPI publication date."""
    next_month = timestamp.to_period("M").to_timestamp() + pd.offsets.MonthBegin(1)
    return pd.date_range(next_month, periods=4, freq=_US_FEDERAL_BUSINESS_DAY)[-1]


def parse_gscpi_vintage_table(table: pd.DataFrame) -> pd.DataFrame:
    """Convert the official wide vintage table into one canonical monthly series.

    The source publishes one column per release vintage. This MVP deliberately
    uses the latest available vintage and assigns each reference month the New
    York Fed's normal fourth-business-day-of-the-following-month publication
    schedule. The resulting frame is release-lagged but is not a true real-time
    vintage history; older values can contain revisions.
    """
    if "Date" not in table.columns:
        raise ValueError("GSCPI data must contain a 'Date' column.")

    vintage_dates = pd.to_datetime(pd.Index(table.columns[1:]), format="%b-%y", errors="coerce")
    valid_vintages = [
        (column, vintage)
        for column, vintage in zip(table.columns[1:], vintage_dates, strict=True)
        if not pd.isna(vintage)
    ]
    if not valid_vintages:
        raise ValueError("GSCPI data contains no monthly vintage columns such as 'Jan-24'.")

    latest_column, _latest_vintage = max(valid_vintages, key=lambda item: item[1])
    timestamps = pd.to_datetime(table["Date"], format="%d-%b-%Y", errors="coerce")
    values = pd.to_numeric(table[latest_column], errors="coerce")
    out = pd.DataFrame(
        {
            "timestamp": timestamps.dt.to_period("M").dt.to_timestamp(),
            "value": values,
        }
    ).dropna(subset=["timestamp", "value"])
    out["released_at"] = out["timestamp"].map(_fourth_business_day_of_next_month)
    return canonical_three_col(out)


class NewYorkFedGSCPIAdapter(BaseAdapter):
    """Download, cache, and normalize the official New York Fed GSCPI CSV."""

    def __init__(
        self,
        *,
        cache_path: str | Path,
        refresh: bool = False,
        url: str = GSCPI_DATA_URL,
    ) -> None:
        self._cache_path = Path(cache_path)
        self._refresh = refresh
        self._url = url

    def fetch(self) -> pd.DataFrame:
        """Return the latest GSCPI vintage, downloading it on cache miss."""
        if self._cache_path.exists() and not self._refresh:
            return parse_gscpi_vintage_table(pd.read_csv(self._cache_path))

        request = Request(self._url, headers={"User-Agent": "agentic-forecasting/1.0"})
        try:
            with urlopen(request, timeout=30) as response:  # noqa: S310
                payload = response.read()
        except Exception as exc:
            raise RuntimeError(f"Failed to fetch New York Fed GSCPI data from {self._url}: {exc}") from exc

        if not payload:
            raise RuntimeError(f"New York Fed GSCPI download returned no data: {self._url}")

        table = pd.read_csv(BytesIO(payload))
        frame = parse_gscpi_vintage_table(table)
        self._cache_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self._cache_path.with_suffix(f"{self._cache_path.suffix}.tmp")
        temporary_path.write_bytes(payload)
        temporary_path.replace(self._cache_path)
        return frame


__all__ = ["GSCPI_DATA_URL", "NewYorkFedGSCPIAdapter", "parse_gscpi_vintage_table"]
