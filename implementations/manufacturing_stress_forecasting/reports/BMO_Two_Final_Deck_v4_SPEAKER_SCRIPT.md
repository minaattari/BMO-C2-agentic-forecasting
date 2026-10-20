# Speaker Script — BMO Two Final Deck v4
**Forecasting U.S. Manufacturing Stress with a Governed Adaptive Agent**
Agentic AI Forecasting Bootcamp · 23 slides · target ~18–20 min + Q&A

> How to use this: each slide has a time hint and a spoken script you can read
> almost verbatim, then tighten to your own voice. **Bold** = numbers/phrases to
> land clearly. Every figure here comes straight off the slide — don't add new
> numbers on the day.

---

## The one thing to land
If the audience remembers one sentence: **"We built a governed, auditable agentic
forecaster on a genuinely hard rare-event problem; the headline result is what we
*learned* — for rare events the base rate is a demanding benchmark, bounding the
LLM prevented harm, and governance can be proven before accuracy is."**

## Suggested 5-way speaker split
Map these to the team on slide 2 however you prefer.

| Speaker | Slides | Section | Approx time |
|---|---|---|---|
| A | 1–3 | Open, team, executive summary | ~2.5 min |
| B | 4–7 | Problem, intent, solution, architecture | ~4 min |
| C | 8–12 | Technical approach, data, results 1–3 | ~5 min |
| D | 13–18 | Results 4–6, discussion, learnings, next steps | ~4.5 min |
| E | 19–23 | Adaptive-learning branch, results 7–8, close | ~3.5 min |

**If you run short:** compress slides 19–20 into a single handoff and keep only
the headlines on 21–22. The core story is complete at slide 18.

---

# Speaker A — Open & frame (slides 1–3)

### Slide 1 — Title (~30s)
> "Good [morning/afternoon]. We're **Team BMO Two**, and our project is
> *Forecasting U.S. Manufacturing Stress with a Governed Adaptive Agent*.
> Up front, the honest framing: this was a **bootcamp learning exercise**. The
> goal was to learn how to *design, evaluate and govern* an agentic forecaster —
> **not** to ship a production model. Keep that lens on everything we show."

### Slide 2 — Meet the team (~20s)
> "Quick introductions — we're five from across the modelling and ML functions:
> Mina, Nitya, Pratyush, Vaibhav and Navid. Between us we cover wholesale credit,
> retail IFRS 9, wholesale IFRS 9 and machine learning. We'll hand off as we go."

### Slide 3 — Executive summary (~90s)
> "Here's the whole story on one page.
> **The opportunity:** earlier warning of manufacturing stress could support
> sector-level portfolio monitoring — but stress is **rare, 6.25% of months since
> 2000**, and hard to anticipate.
> **Our solution:** a forecasting workbench where an LLM agent starts from a
> logistic-regression anchor, adds evidence-based reasoning **within a ±0.03
> bound**, and keeps a versioned, auditable strategy memory.
> **The results, stated plainly:** across **84 monthly backtest origins with 6
> stress events, no model beat the historical-frequency baseline of Brier
> 0.0667**. Our bounded adaptive agent was **close at 0.0692**; the *unbounded*
> LLM analyst was far worse at **0.0979**.
> **Next:** a frozen, prospective evaluation with more stress events and leading
> indicators before we judge whether agents add skill. I'll hand to [B]."

---

# Speaker B — Problem → architecture (slides 4–7)

### Slide 4 — Business problem & opportunity (~70s)
> "Why does this matter? Credit teams monitor sector exposures and want earlier
> warning when an industry heads into stress. But manufacturing stress is rare —
> **20 of 320 months** from 2000 to 2026 — clustered in **2008–09, 2020, and brief
> 2021–22** episodes. Our target definition: a month is *stressed* when U.S.
> manufacturing production — the FRED **IPMAN** series — has fallen **2% or more
> over the previous three months**, and we forecast that **three months ahead**.
> Few events plus hard-to-audit analyst judgment is exactly where a governed
> agent *might* help — reading many signals, explaining its view, with a full
> audit trail."

### Slide 5 — What we set out to learn (~50s)
> "We framed four learning questions: **Can an LLM agent improve on a statistical
> forecast? How do we keep an LLM forecaster safe? Can an agent learn from
> experience, transparently? And how should we evaluate rare-event forecasts?**
> Everything after this is us answering those four."

### Slide 6 — Our solution (~60s)
> "The solution is a workbench pairing a transparent statistical model with an LLM
> analyst. Three capabilities: a **leakage-safe numerical anchor** — logistic
> regression refit at each forecast date on only data released by that date; a
> **bounded LLM** that returns a probability, rationale and evidence but whose
> change to the anchor is **capped at ±0.03**; and a **governed adaptive memory**
> where a hypothesis needs **3 confirmations from distinct origins** before it
> changes strategy, and every change is hash-linked."

### Slide 7 — Architecture (~60s)
> "End to end: **leakage-safe data → logistic anchor → LLM agent proposes a
> probability → ±0.03 guardrail → scored forecast record.** The adaptive agent
> also has a strategy memory that later prompts read, with a redacted audit log of
> before/after hashes. Crucially — what the agent **can** change is only its
> probability within the bound and the strategy text it reads next time. What it
> **cannot** change: data, features, target, model parameters or the anchor code.
> **No retraining happens through the agent.** Over to [C]."

---

# Speaker C — Methods, data, first results (slides 8–12)

### Slide 8 — Technical approach (~70s)
> "The inputs: **15 monthly public series** — IPMAN 1/3/6-month changes, Fed funds,
> the 10y–2y spread, CPI, unemployment, jobless claims, VIX, the Baa credit spread
> from FRED, plus SPY and XLI returns from Yahoo Finance. **Leakage control:** each
> forecast sees only data released by its date, with a conservative 1-month lag on
> IPMAN. We compared **7 models**, from the historical-frequency baseline through
> logistic, XGBoost, hybrids and the agents, across **five experiments**. Our
> metric is the **Brier score — lower is better — and Brier skill versus the base
> rate**, plus calibration and regime slices."

### Slide 9 — What the data told us (~60s)
> "Two findings. One: stress months really do look different — **VIX averages 35
> versus 19, credit spreads 4.0 versus 2.3 points, the industrial ETF down 23% versus
> up 13%** — and all six signs held under bootstrap and leave-one-out checks. But
> two, and this is the crux: those signals are **largely coincident, not leading** —
> lagged correlations peak near zero lag. **That's the core reason a three-month-ahead
> forecast is hard, for any model.**"

### Slide 10 — Results 1: the tuning winner didn't hold (~50s)
> "First results. The logistic model tuned to **C=1.0 ranked first in tuning at
> +28.8% skill — and dead last on 2018–2024 at minus 554%.** Why? Only **5 stress
> events in the tuning period, all in one fold.** The lesson: with rare events,
> tuning can reward a confident model that fit one episode. So we **froze
> conservative settings** and did not retune on the inspected window."

### Slide 11 — Results 2: no model beat the base rate (~60s)
> "The headline comparison, **84 origins, 6 stress events.** **No model beat the
> base rate.** The **adaptive agent came in at minus 3.8% skill** — essentially tied
> — while the **unbounded LLM analyst was minus 46.8%.** The base rate won because
> events were rare and signals coincident. Blending logistic with XGBoost never
> helped — the best weight was **100% logistic**. And with only six events, **we do
> not claim any gap is statistically meaningful.**"

### Slide 12 — Results 3: models reacted too late (~50s)
> "Looking at forecasts against outcomes: **all six stress events were missed.** At
> the origins just before real stress, the anchor and adaptive agent forecast
> **0.05 to 0.11**. Probabilities only spiked at the **April–June 2020** origins —
> *after* the COVID drop was already visible — by which point production was
> recovering, so the actual outcome was zero. Late, not leading. Over to [D]."

---

# Speaker D — Guardrail, governance, takeaways (slides 13–18)

### Slide 13 — Results 4: the guardrail did its job (~55s)
> "This slide is the safety story. The adaptive agent *wanted* higher probabilities —
> **average proposal 0.094 versus the anchor's 0.071** — but the **±0.03 cap pulled
> the final forecast back to 0.072.** The cap engaged on **7 of 84 origins**,
> including April–June 2020 when the agent proposed **up to 0.85.** Bounded agents
> landed at **minus 3.8% to minus 6% skill; the unbounded analyst at minus 46.8%.**
> The guardrail **limited harm — it did not create skill.**"

### Slide 14 — Results 5: a stronger LLM overreacted less (~55s)
> "We also compared two LLMs read-only — Gemini Lite versus Advanced. Advanced
> scored better, but **about 98% of the gap came from just three post-COVID
> origins** where Lite stuck at **0.85** and Advanced backed off. Important nuance:
> **Advanced was not better at spotting stress — both missed all six events** — it
> was just more willing to expect a rebound. The two even **disagreed on risk
> direction on 40% of origins**, and we found rationales quoting **inconsistent
> input values** — a data-quality flag we logged for follow-up."

### Slide 15 — Results 6: auditable memory works (~45s)
> "The governance demonstration: a full hypothesis lifecycle — **open, observe,
> confirm, gate, graduate, update.** Every change carries a **timestamp, tool,
> version and before/after hash**, and the **gate blocked a hypothesis from becoming
> guidance until three distinct confirmations** were recorded. This is the part that
> worked cleanly end to end."

### Slide 16 — Challenges & how we addressed them (~45s)
> "Briefly, the hard parts and our responses: **rare events** — scored against the
> base rate, no significance claims; **look-ahead leakage** — filter by release date,
> lag IPMAN, audit visibility; **overfitting** — froze conservative settings;
> **LLM overconfidence** — anchor and cap; **unreliable explanations** — logged and
> flagged; **reproducibility** — cached runs so report builds make **zero LLM calls**."

### Slide 17 — Key learnings (~55s)
> "Five takeaways. **One, start with the base rate** — for rare events it's a
> demanding benchmark. **Two, anchor and bound the LLM** — unbounded, it overreacts.
> **Three, signals matter more than models** — better leading indicators beat a
> bigger model. **Four, governance can come first** — versioned memory and audit logs
> can be built *before* accuracy is proven. **Five, be careful with explanations** —
> agent rationales aid review but are not causal evidence."

### Slide 18 — Next steps (~45s)
> "Where we'd take it: a **frozen prospective test** with immutable pre-outcome
> forecasts; a prospective test of **memory** updated only from *resolved* forecasts;
> **leading indicators** like new orders and surveys; and **fixing explanation
> quality.** The reusable value is the pattern itself — **statistical anchor +
> bounded agent + audit trail** — as a governance template for agentic models in
> regulated settings. Over to [E]."

---

# Speaker E — Adaptive-learning branch & close (slides 19–23)

### Slide 19 — Outcome-grounded adaptive learning (~55s)
> "We went one step further on *how* an agent is allowed to learn. The control is
> **temporal**: a forecast is saved as an **immutable probability with a stable
> origin ID**; the **outcome stays hidden until its release date**; only *published*
> outcomes enter a **resolution ledger**; a dedicated reviewer then evaluates newly
> resolved origins and writes a new versioned strategy. The hard rule: **an
> unresolved origin cannot confirm or refute a hypothesis**, and a calibration rule
> still needs **3 confirmations from distinct resolved origins.**"

### Slide 20 — What changed in the branch (~40s)
> "Concretely, five additions: a **cutoff-aware outcome ledger**; a **separate
> strategy reviewer** that updates memory only after outcomes resolve; **enforced
> evidence gates** that reject unresolved IDs; **statistical evaluation** — a
> 264-origin history with block-bootstrap intervals and DM tests; and **reproducible
> validation** with hash-linked audit events and passing tests. The point: the
> adaptive process is now **testable**, with a real evidence chain."

### Slide 21 — Results 7: base rate still leads (~45s)
> "On the longer **264-origin history, 2003–2024, 20 stress outcomes**, the base rate
> still leads. **Historical frequency scored 0.0710; logistic 0.0728** — that gap had
> a 90% interval spanning zero, **p = 0.207** — and **XGBoost was reliably worse,
> p = 0.0006.** The longer history **strengthens** the conclusion that these inputs
> add little forward-looking separation. One caveat we're careful about: that's about
> *this feature set*, not proof that stress is inherently unpredictable."

### Slide 22 — Results 8: governance improved, skill did not (~45s)
> "And the outcome-grounded walk-forward — **76 resolved origins, 6 stress events.**
> The reviewer ran **24 times and created 35 audited mutations.** Reviewed and
> no-review agents were **nearly identical, 0.0756 versus 0.0755.** The reviewed agent
> beat its anchor by a hair, **not significant, p = 0.396**, and late-period
> performance was worse. So honestly: **this run does not show learning — but it does
> show a valid, auditable test design.** That distinction is the contribution."

### Slide 23 — Thank you (~20s)
> "That's our story: a hard problem, an honest result, and a governance pattern we're
> confident in. Thank you — we'd welcome questions and feedback."

---

# Q&A prep (grounded answers only)

**"If nothing beat the base rate, did the project fail?"**
No — the deliverable was *learning* and *governance*. For rare events the base rate
is a demanding benchmark; we built a credible, leakage-safe, auditable evaluation
and a governance pattern that worked. Skill was never the sole success criterion
(slides 3, 5, 17, 22).

**"Why three months ahead, and why the 2%-over-3-months definition?"**
That's our stated target: IPMAN down ≥2% over the prior 3 months, forecast 3 months
out (slide 4). It's a design choice for this exercise, not a firm standard.

**"Isn't ±0.03 arbitrary?"**
It's a deliberately small, conservative bound to keep the agent tied to the anchor.
The deck shows it engaged on 7 of 84 origins and limited harm (−3.8% vs −46.8%).
The empirical payoff: on the 84-origin backtest the bounded adaptive agent is the
*only* agent whose confidence interval still includes zero — i.e. statistically tied
with the base rate (p = 0.249) — while the stateless hybrid-adjusted agent (p = 0.039)
and XGBoost (p = 0.031) are reliably worse.
*Be honest:* the code doesn't justify the exact magnitude — it's a chosen parameter
to revisit, not a derived threshold (slides 6, 13; `reports/full_history/executive_report.md`).

**"How do you know there's no look-ahead leakage?"**
Every input is filtered by release date, IPMAN carries a 1-month lag, and we audited
what was visible at the latest origin (slides 6, 8, 16).

**"Did the agent actually learn?"**
Not in these runs — reviewed and no-review agents were nearly identical and the
anchor gap wasn't significant (p = 0.396). A telling detail: the first single-call
design (forecast *and* update strategy in one call) made **zero** strategy changes
across 76 origins — the model just forecast. Only when we split out a dedicated
*review* step did the agent use its governed learning tools (76 forecasts, 24
reviews, 35 audited mutations). So we validated the *design* — an auditable,
outcome-grounded learning process — not a gain in accuracy (slides 17, 19–22).

**"Why Brier score instead of accuracy/AUC?"**
It's a proper scoring rule for probabilities — lower is better — and Brier skill
compares directly against the base rate. With 6 events, threshold metrics are
unstable (slides 8, 11).

**"Are any of the differences statistically significant?"**
No model is significantly *better* than the base rate. Some are reliably *worse*:
in the 84-origin backtest the stateless hybrid-adjusted agent (p = 0.039) and
XGBoost (p = 0.031) sit below it, while the bounded adaptive agent's interval still
includes zero. On the 264-origin history, logistic vs base rate was p = 0.207
(indistinguishable) and XGBoost was reliably worse at p = 0.0006. We use a circular
block bootstrap plus a horizon-aware Diebold-Mariano test because overlapping
3-month targets are serially correlated (slides 11, 21).

**"Would you put this in production?"**
No — it's a proof of concept. The next gate is a frozen prospective evaluation with
more stress events and leading indicators before judging whether agents add skill
(slides 3, 18).

**"What's the tech stack?"**
Agents are built on **Google ADK**, run through an internal **Vector LLM proxy**,
using **Gemini "lite" (512-token cap)** and **"advanced" (4096-token cap)** configs.
The numerical models are **scikit-learn** logistic regression (in a StandardScaler
pipeline) and **XGBoost**. **Langfuse** gives optional per-call tracing, and every
durable strategy change is appended to a redacted local audit log. Packaging and
tests use **uv** and **pytest**.

**"Are your features truly point-in-time — what about data revisions?"**
We filter every input by release date and lag IPMAN by a month, but we use
**latest-vintage FRED data, not ALFRED point-in-time vintages**, so older observations
can carry later revisions. We flag that as a known limitation; a production study
should source ALFRED. And the LLM backtest is retrospective — we anonymise dates to
relative month offsets, which *reduces* but can't *eliminate* the chance a model
recognises a historical episode.

**"If the signals are real, why don't the models discriminate?"**
A Murphy decomposition shows almost no *resolution* — the ability to separate stressed
from calm months. Logistic resolution is 0.00004 and XGBoost 0.00051 against an
uncertainty of 0.070. The signals are strong *coincidentally* but barely *leading*,
so three months out there is little separation to exploit.

**If a question goes beyond the deck:** say so plainly — "that's not something we
evaluated in this study; we'd need to check" — rather than improvising a number.

---

# Appendix A — Technical depth & backup facts (not on the slides)

Pull these only if asked — all are verifiable in the repo (sources noted). They add
credibility in Q&A; don't read them as part of the main flow.

## A1 · Engineering & reproducibility
- **Agent framework:** Google ADK agents via the shared `aieng.forecasting` layer,
  run through an internal Vector LLM proxy (`analyst_agent/json_runner.py`).
- **Numerical models:** scikit-learn `LogisticRegression` in a `StandardScaler`
  pipeline (`max_iter=1000`) and `XGBClassifier` (`predictors/`).
- **Zero-LLM report builds:** every figure and table rebuilds from saved CSVs with no
  model calls (`reports/*/build_report.py`) — cheap, deterministic, reviewable.
- **Fingerprinted caches:** predictions cache under a spec fingerprint, so changing
  stride, horizon, dates or warmup can't silently reuse an incompatible result; the
  harness checks every model was scored on identical origin/date pairs.
- **Speed:** a vectorised as-of join (`features.build_feature_matrix`) reproduces the
  per-origin snapshot ~100× faster, so the 264-origin run finishes in under a minute.
- **Tests:** 6 test files for this implementation; the 4 outcome-grounding tests in
  `test_adaptive_learning.py` pass.

## A2 · Exact model configuration
- **Anchor:** logistic regression, **C = 0.001** (strong regularisation), refit at
  every origin on cutoff-safe rows.
- **XGBoost (comparison only):** 50 trees, max depth 2, learning rate 0.03,
  min_child_weight 3, reg_lambda 5 — never part of the anchor.
- **Hybrid sweep:** best of 11 blend weights was **100% logistic**; adding XGBoost
  never helped.
- **Safe fallback:** with too few rows or a single class, the fitted models fall back
  to the visible base rate; usable training rows start in 1999 and carry no stress
  before 2008.

## A3 · Leakage controls (deeper than slide 8)
- Each origin sees only data released by its date; IPMAN carries a conservative
  1-month release lag; daily rates are treated as available next business day and
  collapsed to monthly.
- Retrospective agent prompts replace calendar dates with **relative month offsets**
  to reduce event recall.
- **Known limitation (volunteer it):** FRED values are latest-vintage, not ALFRED
  point-in-time vintages, so older rows may carry revisions; and date anonymisation
  reduces but can't eliminate LLM episode-recognition.

## A4 · Governance mechanics (exact rules)
- `skill_state.yaml` is the source of truth — approach narrative, observations,
  hypotheses, confirmation/refutation counts, graduated calibration corrections. It
  is **strategy memory, not model weights**. Every save backs up the prior state to
  `.history/` and regenerates a human-readable `SKILL.md`.
- An `OutcomeLedger` reveals an outcome only when its publication date ≤ the current
  origin. Tools **refuse** missing, unknown, unresolved or duplicate origins.
- `graduate_hypothesis` needs **3 confirmations from distinct resolved origins and
  more confirmations than refutations**; **3 refutations** close a hypothesis.
- **Why it exists:** an earlier design let a hypothesis self-confirm before its
  forecast resolved (legacy commit `cc4ea72`, whose "origins" were notes like
  "Manual analysis"). The ledger fixed that (`adaptive_agent/README.md`).

## A5 · The most honest finding
- The first **single-call** design (forecast + maintain strategy together) made
  **zero strategy changes across 76 origins**. Only splitting out a dedicated
  **review** step made the agent use its governed tools: **76 forecasts, 24 reviews,
  35 audited mutations** (no-review arm: 76 forecasts, 0 mutations). Proves the
  mechanism works — not that accuracy improved.

## A6 · Statistical rigor (backup numbers)
- **Full history (264 origins, 20 stress months):** base rate 0.0710; logistic 0.0728
  (skill −2.6%, 90% CI [−0.0008, +0.0043], DM p = 0.207 → tied); XGBoost 0.0778
  (skill −9.6%, DM p = 0.0006 → reliably worse).
- **84-origin agents:** adaptive 0.0692 (−3.8%, CI includes zero, p = 0.249);
  hybrid-adjusted 0.0707 (−6.0%, p = 0.039); XGBoost 0.0722 (−8.2%, p = 0.031);
  analyst 0.0979 (−46.8%).
- **Why so little skill:** Murphy resolution ≈ 0 (logistic 0.00004, XGBoost 0.00051
  vs uncertainty 0.070).
- **Lead-up:** mean probability in the 3 origins before each episode sat ~0.05 (2008)
  to ~0.06 (2020); only XGBoost's late-2022 reading rose (0.132).
- **Methods:** circular block bootstrap (block length 6) + horizon-aware (HAC)
  Diebold-Mariano, because overlapping 3-month targets are serially correlated
  (`evaluation_stats.py`).

## A7 · Protected-evaluation discipline
- A separate protected-evaluation surface with an `EvalTracker` and a **5-run budget**
  is kept apart from the ordinary lite-vs-advanced comparison — a held-out discipline
  built even though the headline results came from diagnostics
  (`specs/manufacturing_stress_protected_eval.yaml`).

---

# Delivery tips
- **Pace:** ~20 min total; don't rush results 2 (slide 11) and the guardrail (13) —
  those are the memorable ones.
- **Tone:** confident about the *method and governance*, candid about *skill*. The
  honesty is a strength, not an apology.
- **Transitions:** each speaker ends by naming the next ("…over to [C]").
- **If time is tight:** merge slides 19–20, keep headline numbers on 21–22.
- **Numbers discipline:** only say figures printed on the slide; if pressed for one
  that isn't there, offer to follow up.
- **Backup depth:** Appendix A has grounded detail (tech stack, exact configs,
  governance rules, statistics) for deep-dive questions — all verifiable in the repo.
