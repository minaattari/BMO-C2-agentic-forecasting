from __future__ import annotations

import json
from pathlib import Path

from aieng.forecasting.data.context import ForecastContext
from aieng.forecasting.evaluation.task import ForecastingTask
from aieng.forecasting.methods.agentic import AgentPredictor, AdkTextRunnerConfig, build_adk_agent
from aieng.forecasting.methods.agentic.agent_factory import AgentConfig
from manufacturing_stress_forecasting.hybrid_agent import (
    HybridManufacturingStressOutput,
    HybridManufacturingStressPromptBuilder,
)
from manufacturing_stress_forecasting.analyst_agent.json_runner import ManufacturingStressJsonRunner
from manufacturing_stress_forecasting.adaptive_agent.state import ManufacturingStrategyState
from manufacturing_stress_forecasting.adaptive_agent.tools import build_strategy_tools
from aieng.forecasting.methods.agentic import AdaptiveSkillStore
from aieng.forecasting.models import LITE_MODEL


DEFAULT_STRATEGY_DIR = Path(__file__).parent / "skills" / "manufacturing-strategy"


class ManufacturingAdaptivePromptBuilder(HybridManufacturingStressPromptBuilder):
    def __init__(self, strategy_dir: Path, *, anonymize_dates: bool = False) -> None:
        super().__init__(anonymize_dates=anonymize_dates)
        self._store = AdaptiveSkillStore(strategy_dir, ManufacturingStrategyState)

    def __call__(self, *, task: ForecastingTask, context: ForecastContext) -> str:
        payload = json.loads(super().__call__(task=task, context=context))
        payload["adaptive_strategy"] = self._store.load().model_dump(mode="json")
        payload["adaptive_rules"] = "Use strategy observations as context; never change model parameters or the numerical anchor."
        return json.dumps(payload, separators=(",", ":"))


def build_manufacturing_adaptive_agent_predictor(
    *,
    strategy_dir: Path = DEFAULT_STRATEGY_DIR,
    config: AgentConfig | None = None,
    model: str = LITE_MODEL,
    anonymize_dates: bool = False,
) -> AgentPredictor:
    if config is None:
        resolved = AgentConfig(
            name="manufacturing_stress_adaptive_analyst",
            model=model,
            instruction=(
                "You are a manufacturing stress forecasting analyst. Use the numerical anchor "
                "as the starting point and make only bounded, evidence-backed adjustments."
            ),
        )
    else:
        resolved = config.model_copy(deep=True)
    resolved.name = f"manufacturing_stress_adaptive_analyst_{model.replace('.', '_').replace('-', '_')}"
    resolved.instruction += (
        "\n\nYou are a stateful adaptive manufacturing analyst. Read adaptive_strategy before forecasting. "
        "Use the numerical anchor as the starting point, apply only bounded adjustments, and use the "
        "strategy mutation tools only for durable patterns supported by distinct forecast origins."
    )
    resolved.extra_tools = build_strategy_tools(strategy_dir)
    agent = build_adk_agent(resolved, output_schema=HybridManufacturingStressOutput)
    runner = ManufacturingStressJsonRunner(
        agent,
        config=AdkTextRunnerConfig(
            app_name="manufacturing_stress_adaptive_predictor",
            default_user_id="forecasting_agent",
            fresh_session_per_message=True,
            enable_langfuse_tracing=True,
            langfuse_tags=["manufacturing-stress", "adaptive-agent", "prediction"],
            langfuse_trace_name="manufacturing_stress_adaptive_predictor",
            langfuse_version="manufacturing-adaptive-v1",
            langfuse_propagate_metadata={
                "task_family": "manufacturing_stress",
                "agent_variant": "adaptive",
                "strategy_name": strategy_dir.name,
            },
        ),
    )
    return AgentPredictor(
        agent_config=resolved,
        prompt_builder=ManufacturingAdaptivePromptBuilder(strategy_dir, anonymize_dates=anonymize_dates),
        output_schema=HybridManufacturingStressOutput,
        enable_langfuse_tracing=False,
        runner=runner,
    )
