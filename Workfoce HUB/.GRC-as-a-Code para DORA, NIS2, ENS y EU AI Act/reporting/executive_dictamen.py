"""Executive Compliance Dictamen & Audit Certification Generator.
Produces formal CISO/CTO board reports and cryptographic compliance certificates.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sealer.merkle_bunker import EvidenceSeal


class ExecutiveDictamenGenerator:
    """Produces board-level GRC executive dictamens with cryptographic certification."""

    @classmethod
    def generate_markdown_dictamen(
        cls,
        company_name: str,
        nis2_score: float,
        rgpd_score: float,
        cra_score: float,
        global_score: float,
        global_status: str,
        total_gaps: int,
        critical_gaps: int,
        remediation_sprints: float,
        seal: Optional[EvidenceSeal] = None,
    ) -> str:
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        badge = {
            "GREEN": "🟢 CONFORME (Apto para Certificación / Riesgo Bajo)",
            "AMBER": "🟡 CONFORME CONDICIONAL (Plan de Remediación Obligatorio)",
            "RED": "🔴 NO CONFORME (Bloqueo Regulatorio / Riesgo Crítico)",
        }.get(global_status, "⚪ EN REVISIÓN")

        seal_section = ""
        if seal:
            seal_section = f"""
## 5. 🔐 SELLO CRIPTOGRÁFICO DE EVIDENCIAS (SLSA L3+)
- **Identificador de Custodia:** `{seal.seal_id}`
- **Raíz del Árbol de Merkle (SHA-256):** `{seal.merkle_root}`
- **Total de Evidencias Selladas:** {seal.leaf_count} artefactos
- **Firma Digital HMAC:** `{seal.hmac_signature[:32]}...`
- **Validez Legal:** Cadena de custodia inmutable verificable por auditores externos.
"""

        return f"""# 🛡️ DICTAMEN EJECUTIVO DE CUMPLIMIENTO REGULATORIO
**Entidad Auditada:** {company_name.upper()}  
**Autor:** COMPLIANCE SENTINEL (Autonomous GRC Council)  
**Fecha de Expedición:** {now_str}  
**Alcance:** Directiva NIS2 (UE 2022/2555), RGPD (UE 2016/679) y CRA (UE 2024/2847)

---

## 1. 📊 DICTAMEN GLOBAL Y CALIFICACIÓN
| Marco Regulatorio Europeo | Nivel de Conformidad | Estado RAG |
| :--- | :--- | :--- |
| **Directiva NIS2 (Art. 21 & 23)** | **{nis2_score:.1f}%** | {"🟢 Conforme" if nis2_score >= 85 else ("🟡 Parcial" if nis2_score >= 60 else "🔴 Crítico")} |
| **Reglamento RGPD (Art. 32 & 35)** | **{rgpd_score:.1f}%** | {"🟢 Conforme" if rgpd_score >= 85 else ("🟡 Parcial" if rgpd_score >= 60 else "🔴 Crítico")} |
| **Cyber Resilience Act (CRA Art. 10 & 11)** | **{cra_score:.1f}%** | {"🟢 Conforme" if cra_score >= 85 else ("🟡 Parcial" if cra_score >= 60 else "🔴 Crítico")} |
| **ÍNDICE GLOBAL DE CUMPLIMIENTO** | **{global_score:.1f}%** | **{badge}** |

---

## 2. 📋 RESUMEN EJECUTIVO PARA EL CONSEJO DE ADMINISTRACIÓN
- **Brechas Identificadas Totales:** **{total_gaps}** hallazgos.
- **Bloqueadores Críticos de Seguridad:** **{critical_gaps}** controles no superados.
- **Esfuerzo de Remediación Estimado:** **{remediation_sprints}** sprints técnicos para alcanzar 100% GREEN.

---

## 3. ⚖️ ANÁLISIS DE EXPOSICIÓN LEGAL Y SANCIONES
- **Régimen Sancionador NIS2:** Hasta 10M€ o el 2% del volumen de negocio mundial por incumplimiento de medidas de gestión de riesgos (Art. 34).
- **Régimen Sancionador RGPD:** Hasta 20M€ o el 4% del volumen de negocio anual por brechas de seguridad o ausencia de TOMs (Art. 83).
- **Responsabilidad Directa de la Dirección:** Tanto NIS2 como CRA establecen la obligación del equipo directivo de supervisar y validar activamente las medidas de ciberseguridad.

---

## 4. 🚀 PLAN DE ACCIÓN RECOMENDADO
1. Priorizar la resolución inmediata de los {critical_gaps} bloqueadores críticos (MFA, backups inmutables y cifrado de PII).
2. Generar y registrar el SBOM CycloneDX v1.5 en cada ciclo de compilación.
3. Realizar un simulacro de notificación de incidentes en menos de 24h/72h con el CSIRT de referencia.
{seal_section}
---
*Dictamen formal generado de forma autónoma con rigor criptográfico por COMPLIANCE SENTINEL.*
"""
