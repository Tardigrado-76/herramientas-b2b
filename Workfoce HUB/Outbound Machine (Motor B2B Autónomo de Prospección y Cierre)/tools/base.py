"""BaseTool for OUTBOUND MACHINE.
Provides Pydantic schema generation compatible with Agency-Swarm and Swarms.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict
from pydantic import BaseModel


class BaseTool(BaseModel, ABC):
    """Abstract base class for all Outbound tools with automated schema generation."""

    model_config = {"arbitrary_types_allowed": True}

    @classmethod
    def openai_schema(cls) -> Dict[str, Any]:
        """Returns JSON schema in OpenAI function calling format."""
        schema = cls.model_json_schema()
        properties = {k: v for k, v in schema.get("properties", {}).items()}
        required = [k for k, v in schema.get("properties", {}).items() if "default" not in v]

        return {
            "name": cls.__name__,
            "description": cls.__doc__ or f"Tool {cls.__name__}",
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": sorted(required),
            },
        }

    @abstractmethod
    def run(self) -> Any:
        """Executes tool logic and returns structured result."""
        pass
