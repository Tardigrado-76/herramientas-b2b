"""
Podador de Contexto y Optimizador de Tokens para Agentes de Codificación.
Mantiene el prompt y las evidencias por debajo de 4,000 tokens para prevenir sobrecostos.
"""

class ContextTrimmer:
    """Optimiza y trunca historiales verbosos antes de enviarlos al modelo LLM."""

    @staticmethod
    def trim_code_diff(diff_content: str, max_lines: int = 80) -> str:
        lines = diff_content.splitlines()
        if len(lines) <= max_lines:
            return diff_content
        kept = lines[:max_lines]
        kept.append(f"... [Truncado por ContextTrimmer: {len(lines) - max_lines} líneas adicionales omitidas] ...")
        return "\n".join(kept)

    @staticmethod
    def extract_relevant_ast_summary(classes: list[str], functions: list[str]) -> str:
        cls_str = ", ".join(classes) if classes else "Ninguna"
        fn_str = ", ".join(functions) if functions else "Ninguna"
        return f"Clases públicas: [{cls_str}] | Métodos/Funciones: [{fn_str}]"
