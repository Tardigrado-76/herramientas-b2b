"""
Validador de Costuras Arquitectónicas mediante AST (Abstract Syntax Tree).
Verifica que las soluciones de código no rompan las costuras de la arquitectura,
no utilicen dependencias no declaradas y mantengan el principio de Módulos Profundos.
"""

import ast
from typing import Any
from pydantic import BaseModel, Field
from core.step_contract import StepContract


class ASTValidationResult(BaseModel):
    is_valid: bool
    score: int  # 0 a 100
    violations: list[str] = Field(default_factory=list)
    detected_classes: list[str] = Field(default_factory=list)
    detected_functions: list[str] = Field(default_factory=list)
    detected_imports: list[str] = Field(default_factory=list)
    depth_metric_loc_to_interface_ratio: float = 0.0


class ASTSeamValidator:
    """Motor de análisis estático basado en AST para validar costuras de diseño."""

    @classmethod
    def validate_source(cls, source_code: str, contract: StepContract) -> ASTValidationResult:
        violations: list[str] = []
        detected_classes: list[str] = []
        detected_functions: list[str] = []
        detected_imports: list[str] = []

        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            return ASTValidationResult(
                is_valid=False,
                score=0,
                violations=[f"SYNTAX_ERROR: Error de sintaxis Python en línea {e.lineno}: {e.msg}"]
            )

        # 1. Analizar nodos de importación
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    detected_imports.append(alias.name)
                    if alias.name in contract.forbidden_imports:
                        violations.append(f"FORBIDDEN_IMPORT: Importación de '{alias.name}' prohibida por contrato.")
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                detected_imports.append(mod)
                if any(mod == fi or mod.startswith(f"{fi}.") for fi in contract.forbidden_imports):
                    violations.append(f"FORBIDDEN_IMPORT: Importación from '{mod}' prohibida por contrato.")

        # 2. Analizar clases y métodos
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                detected_classes.append(node.name)
            elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                detected_functions.append(node.name)

        # 3. Comprobar cumplimiento de la interfaz permitida
        if contract.allowed_interface.class_name:
            if contract.allowed_interface.class_name not in detected_classes:
                violations.append(
                    f"MISSING_CONTRACT_CLASS: La clase '{contract.allowed_interface.class_name}' no fue implementada."
                )

        for fn in contract.allowed_interface.functions:
            if fn.name not in detected_functions:
                violations.append(
                    f"MISSING_CONTRACT_METHOD: La función/método '{fn.name}' no fue implementado en el módulo."
                )

        # 4. Cálculo de Profundidad (Loc to Interface ratio)
        lines = [line for line in source_code.splitlines() if line.strip() and not line.strip().startswith("#")]
        loc = len(lines)
        num_public_methods = max(1, len([f for f in detected_functions if not f.startswith("_")]))
        depth_ratio = round(loc / num_public_methods, 2)

        if contract.allowed_interface.is_deep_module and depth_ratio < 2.0 and loc > 0:
            violations.append(
                f"SHALLOW_MODULE_WARNING: Ratio LOC/Métodos es {depth_ratio:.1f} (<2.0). Posible envoltorio superficial sin valor añadido."
            )

        is_valid = len(violations) == 0
        score = max(0, 100 - (len(violations) * 25))

        return ASTValidationResult(
            is_valid=is_valid,
            score=score,
            violations=violations,
            detected_classes=detected_classes,
            detected_functions=detected_functions,
            detected_imports=detected_imports,
            depth_metric_loc_to_interface_ratio=depth_ratio
        )
