# 📊 Presentation Script & Notes: Forecasting U.S. Manufacturing Stress

**Target Duration:** 7 – 10 Minutes (Ideally ~7 Minutes)  
**Format:** 2 Presenters (~3.5 minutes each)  
**Goal:** Deliver a crisp, honest, and high-impact narrative focusing on rare-event macro forecasting, safety guardrails, and AI governance in finance.

---

## ⏱️ Deck Structure & Presenter Split Overview

* **Presenter 1 (Slides 1–6) — The Problem, System Architecture & Empirical Results (~3.5 mins)**
  * **Slide 1:** Title & Honest Framing
  * **Slide 2:** The Business Problem (U.S. Manufacturing Stress)
  * **Slide 3:** High-Level Approach & Solution Architecture
  * **Slide 4:** System Boundaries & Safety Controls
  * **Slide 5:** Technical Setup & Data Leakage Controls
  * **Slide 6:** Primary Backtest Results (The Base Rate Challenge)

* **Presenter 2 (Slides 7–11) — Guardrail Behavior, Adaptive Memory & Strategic Value (~3.5 mins)**
  * **Slide 7:** Full-History Evaluation: The Base Rate Still Leads
  * **Slide 8:** Outcome-Grounded Adaptive Memory (`skill_state.yaml`)
  * **Slide 9:** Governance Improved, Forecast Skill Did not
  * **Slide 10:** Next Steps, Potential Value & Industry Applications
  * **Slide 11:** Conclusion & Key Takeaways

---

## 🧠 Master Class: What You Have & What to Teach the Audience

### 1. The Core Story Arc
* **The Frame:** This was a **governance and safety experiment**, not a pitch for a silver-bullet trading model.
* **The Hard Reality:** Predicting macro stress 3 months ahead is extremely difficult because macro indicators (like industrial production) are mostly *coincident*, not leading.
* **The Surprise Finding:** No complex ML or LLM model beat the simple historical base rate (Brier Score: `0.0667` / `0.0710`).
* **The Victory:** The experiment successfully proved that **safety guardrails work**. An unbounded LLM catastrophically overreacted (Brier score `0.0979`), but our $\pm 0.03$ adjustment cap pulled it back near the statistical baseline (`0.0692`).

### 2. Key Concepts & Numbers to Know
* **Target Definition:** U.S. Manufacturing Stress = FRED `IPMAN` series falling $\ge 2\%$ over a 3-month period, forecasted 3 months ahead.
* **Rarity:** Occurred in only **20 out of 320 months** (2000–2026).
* **The Anchor:** A leakage-safe Logistic Regression model refit dynamically at each point in time.
* **The Guardrail:** The LLM can suggest probability tweaks, but they are capped at $\pm 0.03$.
* **The Code Boundaries:** The LLM can update strategy text and adjust probabilities within bounds, but **cannot edit data, feature code, or model weights**.
* **Versioned Memory:** Strategy adjustments are logged in `skill_state.yaml` with hashes, timestamps, and multi-origin confirmations.

---

# 🎙️ Complete Two-Presenter Speaker Script

---

## Part 1: Presenter 1 — Problem, Architecture & Results (Slides 1–6)

### Slide 1 — Title & Executive Framing (~30s)
> *"Good [morning/afternoon]. We are Team BMO Two, presenting **Forecasting U.S. Manufacturing Stress with a Governed Adaptive Agent**.*  
> *Upfront, our honest framing: this was a **bootcamp learning exercise** to design, evaluate, and govern an agentic forecaster in finance—**not** to claim a production-ready trading model. Please keep that governance lens on everything we present today."*

### Slide 2 — Meet the Team (~10s)
-"Our team brings together experience across wholesale, IFRS 9 model development, and machine learning from BMO's Enterprise Risk Modeling and Analytics" 

### Slide 3 — Business Problem & Opportunity (~40s)
> *"Credit risk teams need early warnings when an industry enters stress. But manufacturing stress is rare, occurring in only **20 out of 320 months** between 2000 and 2026, clustered in 2008–09, 2020, and brief 2021–22 episodes.*  
> *Our target definition: a month is in stress when U.S. manufacturing output—the FRED **IPMAN** index, has fallen **2% or more over 3 months**. We forecasted **3 months ahead**. Combining rare historical events with analyst judgment is the exact challenge a governed agent is built to address."*

### Slide 4 — High-Level Approach: Hybrid Workbench (~45s)
> *"Our solution pairs a transparent statistical model with a bounded LLM analyst. It features three core capabilities:*  
> *1. A **leakage-safe numerical anchor** using logistic regression fit at each forecast date.*  
> *2. **Bounded LLM reasoning** where the agent proposes a probability and rationale, but its adjustment to the anchor is **capped at ±0.03**.*  
> *3. **Governed adaptive memory** where hypotheses require 3 distinct confirmations before altering strategy, with every change hash-linked."*

### Slide 5 — Architecture: Boundaries & Control (~40s)
- "The process begins with leakage-controlled macroeconomic and market data. Logistic regression produces the anchor probability, the LLM reviews the evidence and proposes an adjustment, the +- 0.03 guardrail is applied, and the final probability is stored as a forecast record for evaluation. Crucially, safety is enforced at the system boundary. the agent can adjust its proposed probability within the bound and refine the strategy test that future prompts read. The agent cannot alter the underlying data, feature definitions, target, model parameters, or anchor code. No automated model retraining occurs through the agent. This creates clear boundaries and materially reduces the risk of uncontrolled model changes or look ahead leakage."

### Slide 6 — Data, Models & Evaluation Setup (~30s)
_ *"We used **15 monthly macroeconomic series** from FRED and Yahoo Finance covering manufacturing, interest rates, inflation, labour markets, volatility, credit spreads, and equity-market returns. We compared 7 approaches, ranging from historical frequency and logistic regression to xgboost, and LLM-based agents.Each forecast only sees information released by that date, with a conservative 1-month release lag applied to IPMAN. We evaluated the probability forecasts using the **Brier score**, where lower is better, and Brier skill relative to the historical-frequency baseline. With that setup, I will hand over to [Presenter 2] to explain what the evaluation showed and what we learned about adaptive-agent governance."_

---

## Part 2: Presenter 2 — Guardrails, Memory & Strategic Value (Slides 7–11)

### Slide 7 — Full Histroy Evaluation: The Base Rate still leads (~45s)
- *"Thanks [Presenter 1]. The headline result is that the simplest historical frequency baseline remained the strongest benchmark. On the longer evaluatiob of **264 monbthly origins from 2003 to 2024**, including **20 stress outcomes**, histrorical frequency produced a Brier score of 0.0710. Logistic regression scored 0.0728. its small difference from the baseline was not statistically significant, so we treated the two as effectively tied. XGboost scored 0.0778 and was reliably worse. The conclusion is not that manufacturing stress is inherently unpredictable. it is that these inputs offered limited forward-looking separation at three-month horizon."-

### Slide 8 — Outcome-Grounded Adaptive learning (~40s)
> *"We also tested outcome-grounded learning with strict temporal controls. The key principal is that the agent is not allowed to learn from forecat outcome before that aooutcome has actually become available. First, the system saves an immutable probability, anchor, and stable origin ID. The outcome remains hidden untill its release date. Once published, it enters a sesolution ledger and becomes eligible for review. A dedicated reviewer evaluates resolved origins and can update a versioned strategy file (`skill_state.yaml`). A calibration rule requires 3 confirmations from distinct resolved origins before promotion. Every update records the review origin, tool, timestamps,and before/after hashes for complete auditability.  "*

### Slide 9 — Governance improved, forecast skill did not (~35s)
- "The outcome-grounded walk-forward evaluation included **76 resolved origins** and **6 stress outcomes**. The reviewer ran 24 times and created 35 audited mutations, demonstrating that the governed review and memory mechanism operated as designed. However, reveiwed and no-review agents were almost identical, with Brier scores of 0.0757 and 0.0755. The reveiwed agent's small improvement over its anchor was not statistically significant. Therefore, this run does not demonstrate improved learning or forecasting skill. it does demonstrate a valid and auditable way to test adaptive learning." _

### Slide 10 — Potential Value & Industry Applications (~40s)
> *"The value of this work isn't just a forecasting metric—it’s a **reusable governance pattern for regulated finance**:*  
> *Combining a quantitative anchor + bounded LLM agent + immutable audit trail.*  
> *It allows institutions to deploy generative AI safely with hard limits on behavior and full traceability."*

### Slide 11 — Conclusion & Key Takeaways (~25s)
> *"In conclusion:*  
> *1. Always respect the base rate for rare events.*  
> *2. Anchor and bound your LLMs to limit overreaction.*  
> *3. System safety and governance can be proven even before predictive superiority is achieved.*  
> *Thank you, and we welcome your questions!"*

---

# 🧠 Q&A Fast-Reference Cheat Sheet

* **Q1: "If no model beat the base rate, did the project fail?"**
  * **Answer:** No. The project goal was to evaluate **governance, safety, and agentic design**. In rare-event macro forecasting (only 6.25% of months in stress), beating the historical frequency is notoriously difficult. We successfully proved that a bounded LLM prevents catastrophic overreaction while preserving a complete audit trail.

* **Q2: "Why was the guardrail cap set to ±0.03?"**
  * **Answer:** It was established as a conservative parameter to keep the LLM anchored to the quantitative baseline. Backtesting confirmed its necessity: without the cap, the unbounded agent overreacted to noise and scored significantly worse (Brier score 0.0979 vs 0.0692).

* **Q3: "Did the agent actually learn over time?"**
  * **Answer:** While predictive accuracy remained tied to the baseline, the agent proved out an **auditable learning workflow**. Across 24 reviews, 35 controlled mutations were safely executed in `skill_state.yaml` without breaking temporal controls or code boundaries.