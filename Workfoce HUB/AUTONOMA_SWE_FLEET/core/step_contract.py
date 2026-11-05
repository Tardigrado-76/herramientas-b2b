"""
StepContract - Contrato Formal de Paso Inmutable para Agentes de Codificación.
Basado en los principios de White Coding y Codebase Design (Matt Pocock).
Fija la superficie de prueba (Interface is Test Surface), dependencias permitidas y criterios Gherkin.
"""

from typing import Any
from pydantic import BaseModel, Field


class PublicMethodSignature(BaseModel):
    name: str
    args: list[str] = Field(default_factory=list)
    return_type: str = "Any"
    docstring: str = ""


class AllowedInterface(BaseModel):
    class_name: str | None = None
    functions: list[PublicMethodSignature] = Field(default_factory=list)
    is_deep_module: bool = True


class GherkinScenario(BaseModel):
    title: str
    given: str
    when: str
    then: str


class StepContract(BaseModel):
    contract_id: str
    bead_id: str
    title: str
    target_file: str
    test_file: str
    allowed_interface: AllowedInterface
    forbidden_imports: list[str] = Field(default_factory=list)
    scenarios: list[GherkinScenario] = Field(default_factory=list)
    max_tokens_budget: int = 40000
    is_locked: bool = True
    created_at: str = ""

    def validate_code_conformance(self, code: str) -> tuple[bool, list[str]]:
        """Valida que el código cumpla con las restricciones básicas del contrato."""
        violations = []
        for fi in self.forbidden_imports:
            if f"import {fi}" in code or f"from {fi}" in code:
                violations.append(f"FORBIDDEN_IMPORT: Se detectó importación prohibida de '{fi}'.")
        
        # Comprobar presencia de la clase o funciones requeridas
        if self.allowed_interface.class_name:
            if f"class {self.allowed_interface.class_name}" not in code:
                violations.append(f"MISSING_INTERFACE: No se encontró la clase requerida '{self.allowed_interface.class_name}'.")
        
        for fn in self.allowed_interface.functions:
            if f"def {fn.name}" not in code:
                violations.append(f"MISSING_METHOD: No se encontró la función/método requerido '{fn.name}'.")

        return len(violations) == 0, violations
