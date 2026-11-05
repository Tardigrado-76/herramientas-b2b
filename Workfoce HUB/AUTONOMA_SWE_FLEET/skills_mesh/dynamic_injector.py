"""
Inyector Dinámico de Habilidades de Ingeniería en los Git Worktrees de los Polecats.
"""

import os
from pathlib import Path


class DynamicSkillInjector:
    """Inyecta instrucciones de habilidades especializadas en el espacio de trabajo del agente."""

    SKILLS_LIBRARY = {
        "codebase-design": (
            "# Codebase Design Directives (Matt Pocock)\n"
            "- Diseñar módulos profundos: Interfaz pública mínima, funcionalidad potente oculta.\n"
            "- The Deletion Test: Reescribir la implementación nunca debe obligar a cambiar a los llamadores.\n"
            "- Interface is the Test Surface: Prohibido acoplar tests a variables o métodos privados '_'.\n"
        ),
        "test-driven-development": (
            "# Test-Driven Development (TDD)\n"
            "- Escribir el test antes de la implementación.\n"
            "- Cobertura 100% de escenarios Gherkin.\n"
            "- Cada test debe fallar inicialmente por la razón correcta.\n"
        ),
        "systematic-debugging": (
            "# Systematic Debugging Guide\n"
            "- Reproducir el fallo con una prueba mínima aislada.\n"
            "- No intentar adivinar: Inspeccionar la causa raíz con aserciones precisas.\n"
            "- Evitar bucles de reintento ciegos.\n"
        )
    }

    @classmethod
    def inject_skills_into_worktree(cls, worktree_path: str, skill_names: list[str]) -> list[str]:
        injected = []
        target_dir = os.path.join(worktree_path, ".agents", "skills")
        os.makedirs(target_dir, exist_ok=True)

        for name in skill_names:
            content = cls.SKILLS_LIBRARY.get(name)
            if content:
                s_path = os.path.join(target_dir, f"{name}.md")
                with open(s_path, "w", encoding="utf-8") as f:
                    f.write(content)
                injected.append(s_path)

        return injected
