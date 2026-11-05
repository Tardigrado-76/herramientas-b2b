"""Multi-Touch Outbound Cadence Manager.
Orchestrates automated follow-up sequences across days with state tracking and reply detection.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CadenceStep:
    step_number: int
    delay_days: int
    step_name: str
    description: str
    focus_angle: str


@dataclass
class ProspectCadenceState:
    prospect_id: str
    recipient_email: str
    company_name: str
    current_step: int  # 1 to 4
    status: str  # ACTIVE, PAUSED_REPLIED, CONVERTED_HANDOFF, OPTED_OUT, COMPLETED
    history: List[Dict[str, Any]] = field(default_factory=list)
    next_action_due: float = 0.0


class OutboundCadenceManager:
    """Manages multi-day sales sequences with state transitions and compliance halting."""

    DEFAULT_STEPS = [
        CadenceStep(
            step_number=1,
            delay_days=0,
            step_name="Initial Value Pitch",
            description="Personalized cold approach with specific technical gap observation.",
            focus_angle="Value Hook & Executive Introduction",
        ),
        CadenceStep(
            step_number=2,
            delay_days=4,
            step_name="Case Study Proof Point",
            description="Demonstrated metric-driven case study in their industry.",
            focus_angle="Social Proof & Quantitative ROI",
        ),
        CadenceStep(
            step_number=3,
            delay_days=5,  # 4 + 5 = Day 9
            step_name="Regulatory & Urgent Trigger",
            description="EU Regulatory timeline (NIS2/DORA/AI Act) or competitor benchmark.",
            focus_angle="Compliance Deadline & Risk Mitigation",
        ),
        CadenceStep(
            step_number=4,
            delay_days=6,  # 9 + 6 = Day 15
            step_name="Polite Break-Up",
            description="Graceful release of outreach with open door for future quarter.",
            focus_angle="Permission to Close File & Respect for Time",
        ),
    ]

    def __init__(self):
        self._prospects: Dict[str, ProspectCadenceState] = {}

    def enroll_prospect(self, prospect_id: str, email: str, company: str) -> ProspectCadenceState:
        """Enrolls a new prospect into the outbound cadence at Step 1."""
        now = time.time()
        state = ProspectCadenceState(
            prospect_id=prospect_id,
            recipient_email=email,
            company_name=company,
            current_step=1,
            status="ACTIVE",
            next_action_due=now,
            history=[{"step": 1, "enrolled_at": now}],
        )
        self._prospects[prospect_id] = state
        return state

    def record_reply_or_interest(self, prospect_id: str) -> Optional[ProspectCadenceState]:
        """Pauses the cadence immediately when prospect responds or shows interest."""
        state = self._prospects.get(prospect_id)
        if state:
            state.status = "CONVERTED_HANDOFF"
            state.history.append({"action": "REPLY_RECEIVED", "timestamp": time.time()})
        return state

    def record_opt_out(self, prospect_id: str) -> Optional[ProspectCadenceState]:
        """Halts cadence permanently upon opt-out request."""
        state = self._prospects.get(prospect_id)
        if state:
            state.status = "OPTED_OUT"
            state.history.append({"action": "OPTED_OUT", "timestamp": time.time()})
        return state

    def advance_step(self, prospect_id: str) -> Optional[ProspectCadenceState]:
        """Advances an active prospect to the next cadence step."""
        state = self._prospects.get(prospect_id)
        if not state or state.status != "ACTIVE":
            return state

        if state.current_step >= len(self.DEFAULT_STEPS):
            state.status = "COMPLETED"
            return state

        state.current_step += 1
        step_config = self.DEFAULT_STEPS[state.current_step - 1]
        state.next_action_due = time.time() + (step_config.delay_days * 86400)
        state.history.append({"step": state.current_step, "scheduled_at": state.next_action_due})
        return state

    def get_prospect_state(self, prospect_id: str) -> Optional[ProspectCadenceState]:
        return self._prospects.get(prospect_id)
