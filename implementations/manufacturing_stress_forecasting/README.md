# Manufacturing stress forecasting — IPMAN and macro MVP

This implementation asks one Track 1 question:

> Given information available at a monthly forecast origin, what is the
> probability that U.S. manufacturing will be under stress three months later?

The feature service provides 15 active variables: trailing 1-, 3-, and
6-month IPMAN changes plus the requested FRED and Yahoo Finance fields:
`FEDFUNDS`, `YC_SPREAD`, `CPIAUCSL`, `CPI_YOY`, `UNRATE`, `ICSA`, `VIXCLS`,
`HY_SPREAD`, and 3- and 12-month returns for both `SPY` and `XLI`. FRED
levels are collapsed to monthly observations, derived fields use the documented
source series, and Yahoo returns use monthly adjusted-close prices.

The New York Fed GSCPI is also loaded and registered for controlled
experiments, but it is deliberately excluded from
`STATISTICAL_FEATURE_SERIES_IDS`. Logistic regression and XGBoost therefore
use the 15 active IPMAN, macroeconomic, and market variables without GSCPI.

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
  the active IPMAN, macroeconomic, and market variables.
- `ManufacturingStressXGBoostPredictor`: a small fit-at-origin gradient-boosted
  tree classifier using the same variables and cutoff-safe training rows.
- `manufacturing_stress_analyst`: a structured LLM predictor receiving the same
  cutoff-safe signals plus recent IPMAN history and historical base rates.

All predictors return `BinaryForecast` probabilities; backtested predictors are scored with Brier score.

## Data and cutoff assumptions
Compare XGBoost with logistic regression and historical frequency rather than judging it
in isolation, because this small monthly dataset can overfit flexible models.
`FREDAdapter` caches the required FRED series under `data/fred/`, and
`YFinanceDailyAdapter` caches `SPY` and `XLI` under `data/yfinance/`.
Yahoo refreshes request history from 1998 onward explicitly so the provider's
default recent-history window cannot replace the long-term cache.
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

GSCPI is currently loaded and registered but is not an active predictor input.
Add it back only as a controlled challenger and compare models with and without
GSCPI over identical dates.

## Run

The general interactive entry point is
[`manufacturing_stress_workbench.ipynb`](manufacturing_stress_workbench.ipynb).
Open it in VS Code or Jupyter and use its configuration cell to refresh input
data, run the deterministic smoke test, and explicitly opt in to the cached
LLMP backtest without using the terminal.

The dedicated
[`manufacturing_stress_parameter_sweep_workbench.ipynb`](manufacturing_stress_parameter_sweep_workbench.ipynb)
runs the controlled logistic/XGBoost parameter sweep one cell at a time without
requiring the CLI.

From the repository root, put a personal FRED key in `.env` or export it:

```bash
export FRED_API_KEY="..."
```

Populate the FRED, Yahoo Finance, and GSCPI caches and inspect the registered series:

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

`run_parameter_smoke.py` separates model selection from final confirmation:

- `tune` compares three logistic regularization values and four small XGBoost
  configurations over 2000–2017.
- `confirm` evaluates only the selected tuning winner over the fixed 2018–2024
  window.
- `stride=3` evaluates every third month and is the default. `stride=1` is a
  slower every-month diagnostic. Use the same stride for both stages.

Run the tuning stage from the repository root:

```bash
uv run --directory implementations \
  python -m manufacturing_stress_forecasting.run_parameter_smoke
```

The table reports mean Brier score, the gap from historical frequency, and
Brier skill. Lower Brier is better, a negative `delta_vs_baseline` is better,
and positive Brier skill means the candidate beat historical frequency.

The tuning stage prints the best non-baseline candidate and its exact
confirmation command. Confirm only that selected candidate, for example:

```bash
uv run --directory implementations \
  python -m manufacturing_stress_forecasting.run_parameter_smoke \
  --stage confirm --candidate logistic_c_0_1 --stride 3
```

For an every-month tuning diagnostic:

```bash
uv run --directory implementations \
  python -m manufacturing_stress_forecasting.run_parameter_smoke \
  --stage tune --stride 1
```

To run the same workflow in Jupyter, open
[`manufacturing_stress_parameter_sweep_workbench.ipynb`](manufacturing_stress_parameter_sweep_workbench.ipynb)
and run it from top to bottom. Its controls are:

```python
STAGE = "tune"          # change to "confirm" after selecting a winner
CANDIDATE = None        # set to the printed winner for confirmation
BACKTEST_STRIDE = 3     # use the same value for tune and confirm
REFRESH_INPUT_DATA = False
RUN_SWEEP = True
```

After tuning, copy the printed winning candidate into `CANDIDATE`, change
`STAGE` to `"confirm"`, and rerun the notebook. Do not choose a candidate after
examining the confirmation window.

The script and notebook read the local input-data caches but do not use
prediction-result caches or make LLM calls. Keeping selection and confirmation
separate reduces the risk of choosing parameters that merely fit the
confirmation period.

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
2. Compare the expanded macro-panel score with the earlier IPMAN-only result.
3. Compare a separate GSCPI challenger with the active statistical models over
   identical training and evaluation dates.
4. Compare the cached agent backtest against the deterministic baselines only
   after checking scored and skipped origin counts.
