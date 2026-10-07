from __future__ import annotations

import hashlib
import json
from datetime import date
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from aieng.forecasting.methods.agentic import AdaptiveSkillStore
from manufacturing_stress_forecasting.adaptive_agent.state import (
    ManufacturingCalibrationCorrection,
    ManufacturingHypothesis,
    ManufacturingObservation,
    ManufacturingStrategyState,
)


def _state_hash(state: ManufacturingStrategyState) -> str:
    payload = json.dumps(state.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _audit_mutation(
    audit_path: Path,
    *,
    tool: str,
    strategy_dir: Path,
    state_before: ManufacturingStrategyState,
    state_after: ManufacturingStrategyState,
    result: str,
) -> None:
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": "strategy_mutation",
        "tool": tool,
        "strategy_path": strategy_dir.name,
        "strategy_version": _state_hash(state_after)[:12],
        "result": result,
        "state_before_sha256": _state_hash(state_before),
        "state_after_sha256": _state_hash(state_after),
    }
    with audit_path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event, separators=(",", ":")) + "\n")


def build_strategy_tools(
    strategy_dir: Path,
    *,
    confirmation_threshold: int = 3,
    audit_path: Path | None = None,
) -> list[Callable[..., str]]:
    store = AdaptiveSkillStore(strategy_dir, ManufacturingStrategyState, confirmation_threshold=confirmation_threshold)
    resolved_audit_path = audit_path or strategy_dir / ".history" / "adaptation_audit.jsonl"

    def save_mutation(
        tool: str,
        before: ManufacturingStrategyState,
        after: ManufacturingStrategyState,
        result: str,
    ) -> str:
        store.save(after)
        _audit_mutation(
            resolved_audit_path,
            tool=tool,
            strategy_dir=strategy_dir,
            state_before=before,
            state_after=after,
            result=result,
        )
        return result

    def record_observation(finding: str, linked_hypothesis: str = "") -> str:
        state = store.load()
        before = state.model_copy(deep=True)
        state.observations.append(
            ManufacturingObservation(
                date=str(date.today()), finding=finding.strip(), linked_hypothesis=linked_hypothesis.strip() or None
            )
        )
        return save_mutation("record_observation", before, state, "Manufacturing observation recorded.")

    def open_hypothesis(claim: str, initial_evidence: str) -> str:
        state = store.load()
        before = state.model_copy(deep=True)
        hypothesis_id = f"hyp-{len(state.hypotheses) + 1:03d}"
        state.hypotheses.append(ManufacturingHypothesis(id=hypothesis_id, claim=claim.strip()))
        state.observations.append(ManufacturingObservation(date=str(date.today()), finding=initial_evidence.strip(), linked_hypothesis=hypothesis_id))
        return save_mutation(
            "open_hypothesis",
            before,
            state,
            f"Opened {hypothesis_id}; {store.confirmation_threshold} confirmations are required before graduation.",
        )

    def record_hypothesis_outcome(hypothesis_id: str, outcome: str, origin: str) -> str:
        if outcome not in {"confirmed", "refuted"}:
            return "Outcome must be 'confirmed' or 'refuted'."
        state = store.load()
        before = state.model_copy(deep=True)
        hypothesis = next((item for item in state.hypotheses if item.id == hypothesis_id), None)
        if hypothesis is None or hypothesis.status != "open":
            return f"Open hypothesis {hypothesis_id!r} was not found."
        if origin in hypothesis.origins:
            return f"Origin {origin!r} has already been recorded for {hypothesis_id}."
        hypothesis.origins.append(origin)
        if outcome == "confirmed":
            hypothesis.confirmations += 1
        else:
            hypothesis.refutations += 1
        return save_mutation("record_hypothesis_outcome", before, state, f"Recorded {outcome} outcome for {hypothesis_id}.")

    def graduate_hypothesis(hypothesis_id: str, condition: str, adjustment: str) -> str:
        state = store.load()
        before = state.model_copy(deep=True)
        hypothesis = next((item for item in state.hypotheses if item.id == hypothesis_id), None)
        if hypothesis is None:
            return f"Hypothesis {hypothesis_id!r} was not found."
        if hypothesis.confirmations < store.confirmation_threshold:
            return f"Cannot graduate {hypothesis_id}: {hypothesis.confirmations}/{store.confirmation_threshold} confirmations."
        if len(set(hypothesis.origins)) < store.confirmation_threshold:
            return f"Cannot graduate {hypothesis_id}: confirmations must come from distinct origins."
        hypothesis.status = "confirmed"
        state.calibration_corrections.append(ManufacturingCalibrationCorrection(condition=condition.strip(), adjustment=adjustment.strip(), source_hypothesis=hypothesis_id, confirmed_on=str(date.today())))
        return save_mutation("graduate_hypothesis", before, state, f"Graduated {hypothesis_id} into a calibration correction.")

    def update_approach_narrative(new_text: str, rationale: str) -> str:
        state = store.load()
        before = state.model_copy(deep=True)
        state.approach_narrative = f"{new_text.strip()} Rationale: {rationale.strip()}"
        return save_mutation("update_approach_narrative", before, state, "Manufacturing approach narrative updated.")

    return [record_observation, open_hypothesis, record_hypothesis_outcome, graduate_hypothesis, update_approach_narrative]
