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
  * **Slide 7:** Guardrail Deep Dive (Preventing LLM Overreaction)
  * **Slide 8:** Outcome-Grounded Adaptive Memory (`skill_state.yaml`)
  * **Slide 9:** Next Steps & System Improvements
  * **Slide 10:** Potential Value & Industry Applications
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

### Slide 2 — Business Problem & Opportunity (~40s)
> *"Credit risk teams need early warnings when an industry enters stress. But manufacturing stress is rare—occurring in only **20 out of 320 months** between 2000 and 2026, clustered in 2008–09, 2020, and brief 2021–22 episodes.*  
> *Our target definition: a month is in stress when U.S. manufacturing output—the FRED **IPMAN** index—falls **2% or more over 3 months**, forecasted **3 months ahead**. Combining rare historical events with opaque analyst judgment is the exact challenge a governed agent is built to address."*

### Slide 3 — High-Level Approach: Hybrid Workbench (~45s)
> *"Our solution pairs a transparent statistical model with a bounded LLM analyst. It features three core capabilities:*  
> *1. A **leakage-safe numerical anchor** using logistic regression refit at each point in time.*  
> *2. **Bounded LLM reasoning** where the agent proposes a probability and rationale, but its adjustment to the anchor is strictly **capped at ±0.03**.*  
> *3. **Governed adaptive memory** where hypotheses require 3 distinct confirmations before altering strategy, with every change hash-linked."*

### Slide 4 — Architecture: Boundaries & Control (~40s)
> *"Crucially, safety is enforced at the system boundary:*  
> *The agent **can** adjust its proposed probability within the ±0.03 bound and refine its strategy text.*  
> *The agent **cannot** alter underlying data, feature definitions, target definitions, or anchor code. No automated model retraining happens through the agent, ensuring zero data leakage and total code safety."*

### Slide 5 — Data & Backtest Setup (~30s)
> *"We evaluated our system using **15 monthly macroeconomic series** from FRED and Yahoo Finance across **84 monthly backtest origins** spanning 6 major stress episodes. Every origin strictly respects publication lags to prevent look-ahead bias."*

### Slide 6 — Primary Backtest Results (~45s)
> *"The headline result across all models? **No model beat the historical-frequency baseline (Brier score 0.0667)**.*  
> *Our bounded adaptive agent came in close at **0.0692**, while the *unbounded* LLM analyst performed poorly at **0.0979**. Why? Because macro signals 3 months out are largely coincident rather than leading. Handing over to Presenter 2 to explain how our guardrails saved performance."*

---

## Part 2: Presenter 2 — Guardrails, Memory & Strategic Value (Slides 7–11)

### Slide 7 — Guardrail In-Depth: Containing LLM Overreaction (~45s)
> *"Thanks [Presenter 1]. Did our safety guardrail work? Absolutely. Left unbounded, the LLM overreacted to transient news—proposing probabilities as high as **0.85** during volatile periods like mid-2020.*  
> *However, our **±0.03 cap** engaged on 7 critical origin dates, pulling the final forecast back near the baseline. The guardrail successfully **limited harm**, keeping our bounded agent tied near the anchor while unbounded variants failed."*

### Slide 8 — Outcome-Grounded Adaptive Memory (~40s)
> *"We also tested outcome-grounded learning with strict temporal controls. Outcomes stay hidden until their official publication date, logging into a resolution ledger only when published.*  
> *A dedicated reviewer evaluates resolved origins and updates a versioned strategy file (`skill_state.yaml`), recording timestamps, tools, and before/after hashes for complete auditability."*

### Slide 9 — Next Steps & System Improvements (~35s)
> *"To advance this proof of concept, our next steps are to:*  
> *1. Run a **frozen prospective test** with immutable pre-outcome logging.*  
> *2. Incorporate true **leading indicators** like new orders and survey indices.*  
> *3. Refine explanation quality and validate LLM rationales against feature snapshots."*

### Slide 10 — Potential Value & Industry Applications (~40s)
> *"The value of this work isn't just a forecasting metric—it’s a **reusable governance pattern for regulated finance**:*  
> *Combining a quantitative anchor + bounded LLM agent + immutable audit trail.*  
> *It allows institutions to deploy generative AI safely with hard limits on behavior and full traceability."*

### Slide 11 — Conclusion & Key Takeaways (~25s)
> *"In conclusion:*  
> *1. Always respect the base rate for rare events.*  
> *2. Anchor and bound your LLMs to prevent hallucination and overreaction.*  
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