# Manufacturing stress forecasting — IPMAN and macro MVP

This implementation asks one Track 1 question:

> Given information available at a monthly forecast origin, what is the
> probability that U.S. manufacturing will be under stress three months later?

The feature service provides 15 active variables: trailing 1-, 3-, and
6-month IPMAN changes plus the requested FRED and Yahoo Finance fields:
`FEDFUNDS`, `YC_SPREAD`, `CPIAUCSL`, `CPI_YOY`, `UNRATE`, `ICSA`, `VIXCLS`,
`CREDIT_SPREAD` (Moody's Baa corporate yield minus the 10-year Treasury yield,
FRED `BAA10Y`), and 3- and 12-month returns for both `SPY` and `XLI`. FRED
levels are collapsed to monthly observations, derived fields use the documented
source series, and Yahoo returns use monthly adjusted-close prices.

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
IPMAN is conservatively treated as available one month after its reference
month. Daily rate observations are treated as available on the next business
day and collapsed to their final monthly observation. The standard FRED API
does not provide full point-in-time vintages, so historical observations may
contain later revisions; a production study should use ALFRED vintages.

## Run

The general interactive entry point is
[`manufacturing_stress_workbench.ipynb`](manufacturing_stress_workbench.ipynb).
Open it in VS Code or Jupyter and use its configuration cell to refresh input
data, run the deterministic smoke test, and explicitly opt in to the cached
LLMP backtest without using the terminal.

The dedicated
[`manufacturing_stress_parameter_sweep_workbench_2.ipynb`](manufacturing_stress_parameter_sweep_workbench_2.ipynb)
runs the controlled logistic/XGBoost tuning workflow across chronological
validation folds without requiring the CLI. The original parameter-sweep
workbench is unchanged.

The [`manufacturing_stress_workbench_2.ipynb`](manufacturing_stress_workbench_2.ipynb)
is a self-contained comparison notebook for the fixed 2018–2024 smoke window.
It compares historical frequency, logistic regression with `C=0.001`, XGBoost
with 50 trees, depth 2, and learning rate 0.03, plus the deterministic hybrid
anchor that averages the two numerical probabilities. It reports mean Brier
score, Brier skill, per-origin outcomes, and calibration diagnostics. Analyst
and hybrid shadow-agent evaluations are disabled by default and require an
explicit opt-in because they may make LLM calls. The window is a historical
diagnostic rather than an untouched future holdout.

The additive
[`manufacturing_stress_hybrid_workbench.ipynb`](manufacturing_stress_hybrid_workbench.ipynb)
is the interface for the initial hybrid expansion. It defaults to a dry run,
uses the full 15-feature set and the fixed candidates
`logistic_c_0_001` and `xgb_50_depth2_lr0_03`, and keeps the numerical anchor
as the official probability. Set `RUN_AGENT_CALL = True` explicitly to make
one LLM call through the existing ADK/Vector-proxy runner; the proposed agent
adjustment is retained as shadow metadata and bounded in Python.

From the repository root, put a personal FRED key in `.env` or export it:

```bash
export FRED_API_KEY="..."
```

Populate the FRED and Yahoo Finance caches and inspect the registered series:

```bash
uv run python scripts/fetch_manufacturing_stress.py
```

Run the deterministic small backtest:

```bash
uv run --directory implementations python -m manufacturing_stress_forecasting.run_smoke
```

Run the hybrid dry-run smoke interface:

```bash
uv run --directory implementations \
  python -m manufacturing_stress_forecasting.smoke_hybrid_agent
```

Use `--run-agent` only when the Vector-proxy environment is configured and an
explicit LLM call is intended. The hybrid smoke path is additive and does not
change existing predictors, agents, runners, or cached artifacts.

The output prints one mean Brier score per predictor; lower is better. The
logistic model should be compared against historical frequency, not judged in
isolation.

### Controlled deterministic parameter sweep

`run_parameter_smoke.py` compares candidates across three chronological tuning
folds within 2000–2017:

- `tune` compares six logistic regularization values and four small XGBoost
  configurations against historical frequency in 2000–2005, 2006–2011, and
  2012–2017 folds. Training remains expanding and cutoff-scoped at each origin.
- A candidate is suggested only if it beats historical frequency on pooled
  Brier score, in at least two folds, and in an event-bearing fold. Fold tables
  show scores, skipped origins, and resolved stress-event counts; per-origin
  probabilities and outcomes are available in the notebook.
- `confirm` evaluates only one selected candidate over the fixed 2018–2024
  window. This window has already been inspected and is a historical diagnostic,
  not an untouched holdout for selecting new parameters.
- `stride=3` evaluates every third month and is the default. `stride=1` is a
  slower every-month diagnostic. Use the same stride for both stages.

Run the tuning stage from the repository root:

```bash
uv run --directory implementations \
  python -m manufacturing_stress_forecasting.run_parameter_smoke
```

and positive Brier skill means the candidate beat historical frequency.
The tuning output reports fold-level and pooled mean Brier score, the gap from
historical frequency, Brier skill, and event counts. Lower Brier is better, a
negative `delta_vs_baseline` is better, and positive Brier skill means the
candidate beat historical frequency. If events appear in fewer than two folds,
any suggested candidate is explicitly marked provisional.

The tuning stage prints a stability-qualified candidate when one meets the
selection rule. The following command reproduces the historical diagnostic; it
does not create a fresh holdout result:

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

To run the fold-based workflow in Jupyter, open
[`manufacturing_stress_parameter_sweep_workbench_2.ipynb`](manufacturing_stress_parameter_sweep_workbench_2.ipynb)
and run it from top to bottom. Its controls are:

```python
STAGE = "tune"          # change to "confirm" after selecting a winner
CANDIDATE = None        # set to the printed winner for confirmation
BACKTEST_STRIDE = 3     # use the same value for tune and confirm
REFRESH_INPUT_DATA = False
RUN_SWEEP = True
SHOW_ORIGIN_DETAILS = False
```

The notebook reports fold and pooled tables. Set `SHOW_ORIGIN_DETAILS = True`
to inspect each scored probability and resolved label. A candidate can pass the
rule while remaining provisional when stress events appear in only one fold.
Because the 2018–2024 window has already been inspected, do not retune from its
results; a clean next confirmation requires future or prospectively recorded
outcomes.

The script and notebook read the local input-data caches but do not use
prediction-result caches or make LLM calls. Keeping tuning within 2000–2017
and reporting regime-level stability reduces the risk of choosing parameters
that fit only one part of the development period.

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
3. Compare the cached agent backtest against the deterministic baselines only
   after checking scored and skipped origin counts.
