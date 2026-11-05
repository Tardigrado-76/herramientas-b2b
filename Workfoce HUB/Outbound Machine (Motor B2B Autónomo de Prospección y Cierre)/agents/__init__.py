"""Agents package exports for OUTBOUND MACHINE."""

from .outbound_swarm import OutboundSwarmEngine
from .personas import (
    OBJECTION_HANDLER_PROMPT,
    RESEARCHER_PROMPT,
    SALES_COPYWRITER_PROMPT,
    SDR_DIRECTOR_PROMPT,
)

__all__ = [
    "OutboundSwarmEngine",
    "SDR_DIRECTOR_PROMPT",
    "RESEARCHER_PROMPT",
    "SALES_COPYWRITER_PROMPT",
    "OBJECTION_HANDLER_PROMPT",
]
