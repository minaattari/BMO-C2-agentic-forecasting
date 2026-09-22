# Manufacturing stress forecasting — minimal IPMAN MVP

This implementation asks one Track 1 question:

> Given information available at a monthly forecast origin, what is the
> probability that U.S. manufacturing will be under stress three months later?

The model deliberately uses only five explanatory variables: trailing
1-, 3-, and 6-month IPMAN changes, the effective federal funds rate, and the
10-year minus 2-year Treasury yield spread. The small panel keeps the first
multivariate experiment interpretable.

## Target

A month is labelled `1` (stress) when IPMAN has declined by at least 2% over
its preceding three months; otherwise it is `0`. The threshold is a provisional
version-1 definition and should be reviewed visually before expanding the
project.

The forecast made at month `t` predicts the stress label at `t + 3 months`.
That distinction makes this forecasting rather than current-state detection.

## Predictors

  the five IPMAN/rate variables.
  `ManufacturingStressXGBoostPredictor`: a small fit-at-origin gradient-boosted
  tree classifier using the same five variables and cutoff-safe training rows.
  five cutoff-safe signals plus recent IPMAN history and historical base rates.

All predictors return `BinaryForecast` probabilities; backtested predictors are scored with Brier score.

## Data and cutoff assumptions
Compare XGBoost with logistic regression and historical frequency rather than judging it
in isolation, because this small monthly dataset can overfit flexible models.
`FREDAdapter` caches `IPMAN`, `DFF`, `DGS10`, and `DGS2` under `data/fred/`.
IPMAN is conservatively treated as available one month after its reference
month. Daily rate observations are treated as available on the next business
day and collapsed to their final monthly observation. The standard FRED API
does not provide full point-in-time vintages, so historical observations may
still contain later revisions; a production study should use ALFRED vintages.

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

Run one current forecast, including the structured agent:

```bash
uv run --directory implementations python -m manufacturing_stress_forecasting.run_agent_prediction
```

## Next steps

1. Plot IPMAN and the derived stress months; confirm or revise the 2% threshold.
2. Compare the five-variable logistic score with the earlier IPMAN-only result.
3. Backtest the agent only after the deterministic model is stable.
