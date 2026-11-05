"""
Base Tool implementation conforming to Agency Swarm BaseTool pattern and Pydantic validation.
"""
from typing import Any

from pydantic import BaseModel, ConfigDict


class BaseTool(BaseModel):
    """
    Agency-Swarm compatible BaseTool with automated OpenAI JSON Schema generation.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def run(self) -> Any:
        raise NotImplementedError("run() must be implemented by subclasses.")

    @classmethod
    def openai_schema(cls) -> dict[str, Any]:
        schema = cls.model_json_schema()
        doc = cls.__doc__ or cls.__name__
        parameters = {
            "type": "object",
            "properties": schema.get("properties", {}),
            "required": schema.get("required", [])
        }
        return {
            "type": "function",
            "function": {
                "name": cls.__name__,
                "description": doc.strip().split("\n")[0],
                "parameters": parameters
            }
        }
