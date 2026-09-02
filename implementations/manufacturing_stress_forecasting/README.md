# Manufacturing stress forecasting — minimal IPMAN MVP

This implementation asks one Track 1 question:

> Given information available at a monthly forecast origin, what is the
> probability that U.S. manufacturing will be under stress three months later?

The first version intentionally uses only FRED's `IPMAN` series. It excludes
Yahoo Finance, macro covariates, news, LLMs, and agents until the target and
backtest are easy to inspect.

## Target

A month is labelled `1` (stress) when IPMAN has declined by at least 2% over
its preceding three months; otherwise it is `0`. The threshold is a provisional
version-1 definition and should be reviewed visually before expanding the
project.

The forecast made at month `t` predicts the stress label at `t + 3 months`.
That distinction makes this forecasting rather than current-state detection.

## Predictors

- `HistoricalFrequencyPredictor`: the visible historical stress rate.
- `ManufacturingStressLogisticPredictor`: fit-at-origin logistic regression on
  trailing 1-, 3-, 6-, and 12-month IPMAN percentage changes.

Both return `BinaryForecast` probabilities and are scored with Brier score.

## Data and cutoff assumptions

`FREDAdapter` caches `IPMAN` at `data/fred/IPMAN.parquet`. Because the standard
FRED response does not provide point-in-time release vintages, this prototype
conservatively shifts `released_at` one month beyond each reference timestamp.
The limitation remains: historical FRED observations may contain later
revisions. A production-quality study should use ALFRED vintages.

## Run

From the repository root, put a personal FRED key in `.env` or export it:

```bash
export FRED_API_KEY="..."
```

Populate the cache and inspect the registered series:

```bash
uv run python scripts/fetch_manufacturing_stress.py
```

Run the small backtest:

```bash
uv run --directory implementations python -m manufacturing_stress_forecasting.run_smoke
```

The output prints one mean Brier score per predictor; lower is better. The
logistic model should be compared against historical frequency, not judged in
isolation.

## Next steps

1. Plot IPMAN and the derived stress months; confirm or revise the 2% threshold.
2. Add a full monthly development backtest after the smoke run is stable.
3. Add a small FRED macro panel.
4. Add an agent only after the deterministic Track 1 experiment is credible.
