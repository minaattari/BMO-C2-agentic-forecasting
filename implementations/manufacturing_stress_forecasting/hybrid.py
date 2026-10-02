"""Opt-in hybrid manufacturing-stress forecasting components."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import pandas as pd
from aieng.forecasting.data.context import ForecastContext
from aieng.forecasting.evaluation.prediction import BinaryForecast, Prediction
from aieng.forecasting.evaluation.predictor import Predictor
from aieng.forecasting.evaluation.task import ForecastingTask
from aieng.forecasting.methods.agentic import AgentPredictor, DiscreteAgentForecastOutput
from aieng.forecasting.methods.agentic.agent_factory import AgentConfig
from manufacturing_stress_forecasting.analyst_agent import (
    ManufacturingStressPromptBuilder,
    build_manufacturing_stress_agent_config,
)
from manufacturing_stress_forecasting.analyst_agent.json_runner import ManufacturingStressJsonRunner
from manufacturing_stress_forecasting.predictors import (
    ManufacturingStressLogisticPredictor,
    ManufacturingStressXGBoostPredictor,
)

MAX_AGENT_ADJUSTMENT = 0.03
MIN_PROBABILITY = 0.01
MAX_PROBABILITY = 0.99
LOGISTIC_CANDIDATE = "logistic_c_0_001"
XGBOOST_CANDIDATE = "xgb_50_depth2_lr0_03"


@dataclass(frozen=True)
class NumericalAnchor:
    """The two fixed statistical candidates and their transparent anchor."""

    logistic_probability: float
    xgboost_probability: float

    @property
    def probability(self) -> float:
        return 0.5 * (self.logistic_probability + self.xgboost_probability)

    def as_dict(self) -> dict[str, float | str]:
        return {
            "logistic_probability": self.logistic_probability,
            "xgboost_probability": self.xgboost_probability,
            "anchor_probability": self.probability,
            "anchor_method": "mean_logistic_xgboost",
        }


def build_numerical_anchor(task: ForecastingTask, context: ForecastContext) -> NumericalAnchor:
    """Run the two fixed full-feature candidates and average their probabilities."""
    logistic = ManufacturingStressLogisticPredictor(regularization_c=0.001)
    xgboost = ManufacturingStressXGBoostPredictor(
        n_estimators=50,
        max_depth=2,
        learning_rate=0.03,
    )
    logistic_prediction = logistic.predict(task, context)[0]
    xgboost_prediction = xgboost.predict(task, context)[0]
    return NumericalAnchor(
        logistic_probability=logistic_prediction.payload.probability,
        xgboost_probability=xgboost_prediction.payload.probability,
    )


def validate_agent_adjustment(
    anchor_probability: float,
    proposed_probability: float,
    *,
    max_adjustment: float = MAX_AGENT_ADJUSTMENT,
) -> dict[str, Any]:
    """Clamp an agent probability to the configured shadow adjustment range."""
    if not 0.0 <= anchor_probability <= 1.0:
        raise ValueError(f"anchor_probability must be in [0, 1]; got {anchor_probability}.")
    if not 0.0 <= proposed_probability <= 1.0:
        raise ValueError(f"proposed_probability must be in [0, 1]; got {proposed_probability}.")
    raw_adjustment = proposed_probability - anchor_probability
    adjustment = max(-max_adjustment, min(max_adjustment, raw_adjustment))
    shadow_probability = min(MAX_PROBABILITY, max(MIN_PROBABILITY, anchor_probability + adjustment))
    return {
        "raw_agent_adjustment": raw_adjustment,
        "agent_adjustment": adjustment,
        "shadow_probability": shadow_probability,
        "official_probability": anchor_probability,
        "validation_status": "passed" if abs(raw_adjustment) <= max_adjustment else "clamped",
    }


class HybridManufacturingStressPromptBuilder:
    """Add the numerical anchor to the existing cutoff-safe agent payload."""

    def __init__(self, *, anonymize_dates: bool = False) -> None:
        self._base = ManufacturingStressPromptBuilder(anonymize_dates=anonymize_dates)

    def __call__(self, *, task: ForecastingTask, context: ForecastContext) -> str:
        payload = json.loads(self._base(task=task, context=context))
        payload["statistical_anchor"] = build_numerical_anchor(task, context).as_dict()
        payload["hybrid_mode"] = "shadow"
        return json.dumps(payload, separators=(",", ":"))


def build_hybrid_agent_config(model: str | None = None) -> AgentConfig:
    """Build an opt-in agent config using the repository's existing ADK path."""
    base = build_manufacturing_stress_agent_config(model=model) if model else build_manufacturing_stress_agent_config()
    schema = DiscreteAgentForecastOutput.prompt_schema_json()
    base.instruction = (
        base.instruction
        + "\n\nThe payload includes a statistical_anchor. Return a proposed probability that starts from "
        "that anchor. The Python wrapper will enforce the maximum adjustment and will keep the "
        "anchor as the official probability during shadow mode.\n"
        + schema
    )
    base.name = "manufacturing_stress_hybrid_analyst"
    return base


def build_hybrid_agent_predictor(
    *,
    config: AgentConfig | None = None,
    anonymize_dates: bool = False,
) -> AgentPredictor:
    """Build the hybrid agent through the standard AgentPredictor and runner APIs."""
    from aieng.forecasting.methods.agentic import AdkTextRunnerConfig, build_adk_agent

    resolved = config or build_hybrid_agent_config()
    agent = build_adk_agent(resolved, output_schema=DiscreteAgentForecastOutput)
    runner = ManufacturingStressJsonRunner(
        agent,
        config=AdkTextRunnerConfig(
            app_name="manufacturing_stress_hybrid_predictor",
            default_user_id="forecasting_agent",
            fresh_session_per_message=True,
        ),
    )
    return AgentPredictor(
        agent_config=resolved,
        prompt_builder=HybridManufacturingStressPromptBuilder(anonymize_dates=anonymize_dates),
        output_schema=DiscreteAgentForecastOutput,
        enable_langfuse_tracing=False,
        runner=runner,
    )


class HybridShadowPredictor(Predictor):
    """Return the anchor officially and preserve the agent result as shadow metadata."""

    def __init__(self, agent_predictor: AgentPredictor) -> None:
        self._agent_predictor = agent_predictor

    @property
    def predictor_id(self) -> str:
        return "manufacturing_stress_hybrid_shadow_v1"

    def predict(self, task: ForecastingTask, context: ForecastContext) -> list[Prediction]:
        anchor = build_numerical_anchor(task, context)
        agent_prediction = self._agent_predictor.predict(task, context)[0]
        proposed = agent_prediction.payload.probability
        validation = validate_agent_adjustment(anchor.probability, proposed)
        return [
            Prediction(
                predictor_id=self.predictor_id,
                task_id=task.task_id,
                issued_at=datetime.now(tz=timezone.utc).replace(tzinfo=None),
                as_of=context.as_of,
                forecast_date=agent_prediction.forecast_date,
                payload=BinaryForecast(probability=anchor.probability),
                metadata={
                    **anchor.as_dict(),
                    **validation,
                    "agent_probability": proposed,
                    "agent_metadata": agent_prediction.metadata,
                },
            )
        ]


__all__ = [
    "HybridShadowPredictor",
    "LOGISTIC_CANDIDATE",
    "MAX_AGENT_ADJUSTMENT",
    "NumericalAnchor",
    "XGBOOST_CANDIDATE",
    "build_hybrid_agent_config",
    "build_hybrid_agent_predictor",
    "build_numerical_anchor",
    "validate_agent_adjustment",
]
