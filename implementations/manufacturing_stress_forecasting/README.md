# Manufacturing stress forecasting — IPMAN and GSCPI MVP

This implementation asks one Track 1 question:

> Given information available at a monthly forecast origin, what is the
> probability that U.S. manufacturing will be under stress three months later?

The deterministic models use six explanatory variables: trailing 1-, 3-, and
6-month IPMAN changes, the effective federal funds rate, the 10-year minus
2-year Treasury yield spread, and the New York Fed Global Supply Chain
Pressure Index (GSCPI). The small panel keeps the multivariate experiment
interpretable.

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
  the six IPMAN, rate, and supply-chain variables.
- `ManufacturingStressXGBoostPredictor`: a small fit-at-origin gradient-boosted
  tree classifier using the same six variables and release-lagged training rows.
- `manufacturing_stress_analyst`: a structured LLM predictor that remains on
  the original five IPMAN/rate signals plus recent IPMAN history and historical
  base rates; GSCPI is added only to logistic regression and XGBoost for this
  controlled comparison.

All predictors return `BinaryForecast` probabilities; backtested predictors are scored with Brier score.

## Data and cutoff assumptions
Compare XGBoost with logistic regression and historical frequency rather than judging it
in isolation, because this small monthly dataset can overfit flexible models.
`FREDAdapter` caches `IPMAN`, `DFF`, `DGS10`, and `DGS2` under `data/fred/`.
`NewYorkFedGSCPIAdapter` downloads the official GSCPI vintage table without an
API key and caches it under `data/new_york_fed/gscpi_interactive_data.csv`.
IPMAN is conservatively treated as available one month after its reference
month. Daily rate observations are treated as available on the next business
day and collapsed to their final monthly observation. GSCPI is treated as
available on the fourth U.S. federal business day of the following month.

The GSCPI adapter uses the latest column in the New York Fed's revision table.
Consequently, its historical values are release-lagged but are not true
point-in-time vintages and can include later revisions. The standard FRED API
also does not provide full point-in-time vintages. A production study should
retain each GSCPI release and use ALFRED vintages for the FRED series.

## Run

The primary interactive entry point is
[`manufacturing_stress_workbench.ipynb`](manufacturing_stress_workbench.ipynb).
Open it in VS Code or Jupyter and use its configuration cell to refresh FRED
data, run the deterministic smoke test, and explicitly opt in to the cached
LLMP backtest without using the terminal.

From the repository root, put a personal FRED key in `.env` or export it:

```bash
export FRED_API_KEY="..."
```

Populate both the FRED and GSCPI caches and inspect the registered series:

```bash
uv run python scripts/fetch_manufacturing_stress.py
```

Run the deterministic small backtest:

```bash
uv run --directory implementations python -m manufacturing_stress_forecasting.run_smoke
```

The output prints one mean Brier score per predictor; lower is better. The
logistic model should be compared against historical frequency, not judged in
isolation.

### Controlled deterministic parameter sweep

Use the tuning stage to compare three logistic regularization values and four
small XGBoost configurations over 2000–2017:

    uv run --directory implementations python -m manufacturing_stress_forecasting.run_parameter_smoke

The table reports mean Brier score, the gap from historical frequency, and
Brier skill. The tuning stage prints the best non-baseline candidate and the
exact confirmation command. Confirm only that selected candidate on the fixed
2018–2024 window, for example:

    uv run --directory implementations python -m manufacturing_stress_forecasting.run_parameter_smoke \
      --stage confirm --candidate logistic_c_0_1

Pass --stride 1 to either stage for an every-month diagnostic; the default
stride is 3. Use the same stride for tuning and confirmation. This script does
not use caches or make LLM calls. Keeping selection and confirmation separate
reduces the risk of choosing parameters that merely fit the confirmation
period.
Run the token-limited LLMP backtest explicitly:

```bash
uv run --directory implementations python -m manufacturing_stress_forecasting.run_agent_backtest
```

This evaluates historical frequency, logistic regression, XGBoost, and the
`manufacturing_stress_analyst` agent through the same binary backtest and
Brier-score calculation. The agent run uses the default lite model, a
12-month IPMAN history, compact JSON prompts, a 384-token response cap, and
one retry per failed origin. It uses zero-temperature generation and explicitly
requests strict double-quoted JSON. A manufacturing-local runner safely
normalizes the proxy's occasional single-quoted Python dictionary response
before schema validation; the shared Vector AgentPredictor remains unchanged.
The local predictor keeps optional Langfuse tracing disabled, so these test runs
do not export prompts and responses or attach Langfuse trace URLs.
Calendar dates are replaced by relative month offsets in retrospective agent
prompts to reduce historical-event recall.

Complete results are cached under a specification-fingerprinted directory in
`data/predictions/`, so changing the stride, horizon, dates, or warmup cannot
silently reuse an incompatible result. Incomplete runs with skipped origins
are not cached. Use `--force-refresh` to intentionally re-run every predictor.
The command also verifies that every reported model was scored on the exact
same origin and forecast-date pairs.

This remains a retrospective LLM pseudo-backtest: anonymizing dates reduces,
but cannot eliminate, the possibility that a modern model recognizes a
historical episode from its training knowledge. Use prospectively recorded
forecasts for a clean out-of-sample LLM evaluation.

Run one current forecast, including the structured agent:

```bash
uv run --directory implementations python -m manufacturing_stress_forecasting.run_agent_prediction
```

## Next steps

1. Plot IPMAN and the derived stress months; confirm or revise the 2% threshold.
2. Compare the six-variable scores with the five-variable results to measure
   whether GSCPI improves out-of-sample Brier score.
3. Compare the cached agent backtest against the deterministic baselines only
  after checking scored and skipped origin counts.
