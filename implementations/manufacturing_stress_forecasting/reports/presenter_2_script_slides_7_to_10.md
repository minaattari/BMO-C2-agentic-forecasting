# Presenter 2 Script: Slides 7–10

**Presentation:** Manufacturing Stress Forecasting Final Showcase  
**Speaking time:** Approximately 5 minutes  
**Slides:** 7 through 10

## Opening and recap

Thanks, **[presenter’s name]**.

Before getting into the results, let me quickly explain the different approaches we explored.

We started with a very simple baseline. It looks at how frequently manufacturing stress occurred in the past and uses that historical frequency as the forecast probability.

We then tested two traditional machine-learning models: logistic regression and XGBoost. These models used our manufacturing, economic, credit, and market indicators.

Next, we introduced an LLM analyst. The LLM reviewed the available indicators, produced a probability, and explained the evidence behind its view.

We also tested a hybrid approach. In that version, the statistical model produced the starting probability, and the LLM could make only a small, controlled adjustment.

Finally, we created an adaptive version of the agent. This agent had a governed memory, allowing it to review past forecasts after their outcomes became known and potentially improve its future reasoning.

With that context, let’s look at what we found.

## Slide 7: The Base Rate Still Leads

This slide shows the results for the traditional numerical models over our longer evaluation period.

We tested 264 monthly forecasts covering 2003 to 2024. There were only 20 manufacturing stress outcomes, so this was a highly imbalanced forecasting problem.

We measured performance using the Brier score. In simple terms, it measures how close the predicted probabilities were to the actual outcomes. Lower is better.

The historical-frequency baseline scored 0.0710.

Logistic regression scored slightly worse at 0.0728, and XGBoost scored 0.0778.

This means that neither machine-learning model beat the simple baseline. Logistic regression was about 2.6% worse, while XGBoost was about 9.6% worse.

This does not necessarily mean the models were built incorrectly. Manufacturing stress is rare, and many of our indicators may react at the same time as the slowdown rather than providing a sufficiently early warning.

Our takeaway was that adding model complexity did not automatically create better forecasting information.

## Slide 8: Outcome-grounded Adaptive Learning

We then explored whether an LLM agent could learn from its forecasting experience.

A normal LLM forecast is essentially a one-time analysis. It reads the information, produces a probability and rationale, and finishes.

Our adaptive agent adds a controlled learning process.

First, the system saves the forecast and its probability. The forecast cannot be changed later.

The outcome then remains hidden until it would actually have become available.

Once the outcome is published, it enters what we call the resolution ledger. A separate reviewer can then compare the forecast with what actually happened.

Any lesson is recorded in `skill_state.yaml`, which works like a versioned strategy notebook. The next forecast can read those lessons.

We added some important controls around this process.

The agent cannot learn from an unresolved forecast. One result is also not enough to create a new rule. A rule needs confirmation from three separate resolved forecasts.

Every change is logged, including the evidence used and what changed in the strategy.

The goal was to let the agent learn while preventing it from accidentally using future information.

## Slide 9: Governance Improved, Forecast Skill Did Not

The next question was whether this memory actually improved the forecasts.

We tested three related versions.

The anchor was the original statistical forecast. The no-review agent used the LLM but did not update its strategy. The reviewed adaptive agent received periodic strategy updates based on resolved outcomes.

We evaluated 76 resolved forecasts containing six stress events.

The historical baseline again performed best, with a Brier score of 0.0744.

The adaptive agent scored 0.0756, while the same agent without strategy reviews scored 0.0755. Those results are almost identical.

The adaptive agent was slightly better than its own statistical anchor, but the difference was too small to distinguish confidently from chance.

The reviewer ran 24 times and made 35 controlled changes to the strategy. However, making changes is not the same as learning something useful. Those changes did not produce a clear improvement in future forecasts.

So our conclusion is balanced: we successfully built a governed and auditable learning process, but we have not yet demonstrated that the agent’s memory improves predictive performance.

## Slide 10: Next Steps and Opportunities

Our results also give us a clear path forward.

First, we should run a prospective test. We would freeze the system and save forecasts before any outcomes are known.

Second, we should run the adaptive agent beside an identical agent without memory. That would help isolate the value of memory.

Third, we need stronger leading indicators, such as manufacturing new orders or business surveys that may change before production declines.

We also need to improve the quality of the LLM explanations by checking every quoted number against the actual data provided to the agent.

The broader value is the framework we created: a statistical forecast, a controlled LLM analyst, and a complete audit trail.

This pattern could support early-warning monitoring in other sectors as well.

The project did not show that greater complexity automatically improves accuracy. It showed us how to test agentic forecasting honestly, safely, and in a way that we can continue improving.

## Optional closing transition

With that, I’ll hand it over to **[next presenter’s name]** for the closing.
