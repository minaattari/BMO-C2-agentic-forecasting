# 📊 Presentation Script & Notes: Forecasting U.S. Manufacturing Stress

**Target Duration:** 7 – 10 minutes  
**Format:** 2 Presenters  
**Goal:** Deliver a concise, impactful narrative focusing on the core problem, system architecture, guardrails, and key governance learnings.

---

## ⏱️ Time & Handoff Summary

* **Presenter 1 (Slides 1–11):** Frame the problem, business context, hybrid architecture/guardrails, and main backtest results. (~3.5 to 4.5 mins)
* **Presenter 2 (Slides 12–23):** Explain model performance, guardrail behavior, governance/adaptive memory framework, key takeaways, and next steps. (~3.5 to 4.5 mins)

---

## 🗣️ Speaker Script

### Part 1: Presenter 1 — The Problem, Solution & Architecture

#### Slide 1 — Title Page (~25 seconds)
> *"Good [morning/afternoon]. We're Team BMO Two, and today we’re presenting **Forecasting U.S. Manufacturing Stress with a Governed Adaptive Agent**.
> 
> Up front, our honest framing: this was a learning exercise to design, evaluate, and govern an agentic forecaster—not to ship an immediate production model. Please keep that lens on everything we show today."*

#### Slide 3 — Business Problem & Opportunity (~45 seconds)
> *"Why does this matter? Credit teams want earlier warnings when an industry heads into stress. But manufacturing stress is rare—occurring in only **20 of 320 months** between 2000 and 2026, clustered around 2008–09, 2020, and brief 2021–22 episodes.
> 
> Our target definition: a month is stressed when U.S. manufacturing production—the FRED **IPMAN** series—falls **2% or more over the previous 3 months**, forecasted **3 months ahead**. 
> 
> Having few events combined with hard-to-audit analyst judgment is precisely where a governed agent can help."*

#### Slides 4 & 6 — Our Solution & Architecture (~45 seconds)
> *"Our solution is a workbench pairing a transparent statistical model with an LLM analyst. It has three core components:
> 
> 1. A **leakage-safe numerical anchor** using logistic regression refit at each date with historical data only.
> 2. A **bounded LLM analyst** that suggests a probability and rationale, but whose adjustment to the anchor is **capped at ±0.03**.
> 3. A **governed adaptive memory** where hypotheses require 3 distinct confirmations before altering strategy, with every change hash-linked.
> 
> Crucially, the agent can adjust probabilities and strategy text, but **cannot** alter underlying data, features, or anchor code. No retraining happens through the agent."*

#### Slides 8, 10 & 11 — Technical Approach & Backtest Results (~60 seconds)
> *"To test this, we used **15 monthly public inputs** across **84 monthly backtest origins and 6 stress events**.
> 
> The headline finding across models? **No model beat the historical-frequency baseline (Brier score 0.0667)**.
> 
> Our bounded adaptive agent came in close at **0.0692**, while the *unbounded* LLM analyst performed poorly at **0.0979**. Why? Stress events are rare, and macro signals are largely coincident rather than leading three months out. 
> 
> I'll now hand over to [Presenter 2] to walk through how the agent behaved and what we learned."*

---

### Part 2: Presenter 2 — Guardrails, Governance & Learnings

#### Slides 13 & 14 — Guardrail Behavior & LLM Comparison (~45 seconds)
> *"Thanks [Presenter 1]. Did our safety guardrail work? Absolutely. The adaptive agent frequently *wanted* to be much more aggressive—proposing an average probability of **0.094** compared to the anchor's **0.071**.
> 
> However, our **±0.03 cap** engaged on 7 critical origins—including mid-2020 when the agent proposed up to **0.85**—pulling the final forecast back down. The guardrail successfully **limited harm**, keeping our bounded agent close to the baseline while unbounded variants faltered."*

#### Slide 15 — Governed Adaptive Memory (~40 seconds)
> *"We also tested outcome-grounded learning with strict temporal control. Outcomes stay hidden until their official release date, entering a resolution ledger only when published.
> 
> A dedicated reviewer evaluates resolved origins and updates a versioned strategy file (`skill_state.yaml`). Every single update records timestamps, tools, and before/after hashes for complete traceability."*

#### Slide 17 — Key Takeaways (~45 seconds)
> *"So, what are our main takeaways from this project?
> 
> * **One:** Always start with the base rate—for rare events, it is a fiercely demanding benchmark.
> * **Two:** Anchor and bound your LLMs; left unbounded, they tend to overreact.
> * **Three:** Signals matter more than model complexity; better leading indicators beat a bigger model.
> * **Four:** Governance can—and should—be proven *before* raw predictive accuracy is achieved."*

#### Slides 18 & 23 — Next Steps & Closing (~30 seconds)
> *"Where do we take this next? We want to run a frozen prospective test with immutable pre-outcome logging, incorporate forward-looking leading indicators like new orders or surveys, and refine explanation quality.
> 
> The ultimate value here isn't just a forecasting hack; it’s a **reusable governance pattern for regulated financial environments**—combining a statistical anchor, a bounded agent, and a complete audit trail.
> 
> Thank you, and we’d love to take your questions and feedback!"*

---

## 🧠 Q&A Preparation Cheat Sheet

### Q1: "If nothing beat the base rate, did the project fail?"
* **Answer:** No. The primary deliverable was to demonstrate **safety, evaluation rigor, and governance**. For rare events, beating a historical base rate is notoriously difficult. We successfully proved that a leakage-safe, auditable framework can bound an LLM to prevent severe overreaction while maintaining transparency.

### Q2: "Why was the guardrail cap set specifically at ±0.03?"
* **Answer:** It was chosen as a conservative parameter to keep the agent tightly tethered to the statistical anchor. Our backtest results confirmed its necessity: without the cap, the unbounded agent overreacted to noise and scored significantly worse (Brier score 0.0979 vs 0.0692).

### Q3: "Did the agent actually learn over time?"
* **Answer:** While raw forecasting performance didn't surpass the baseline, the agent proved out an **auditable learning workflow**. The review mechanism successfully executed 35 mutations across 24 reviews under strict governance controls without breaking temporal safety or code boundaries.