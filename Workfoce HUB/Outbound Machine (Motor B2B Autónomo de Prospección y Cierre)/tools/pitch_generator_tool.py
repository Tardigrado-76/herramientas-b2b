"""Personalized Cold Outreach Copywriter Tool.
Generates compliant, conversion-optimized B2B sales copy following PAS (Problem-Agitate-Solve) and AIDA models.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import Field

from .base import BaseTool


class PitchGeneratorTool(BaseTool):
    """Generates hyper-personalized cold outreach emails tailored to target sector and decision maker."""

    company_name: str = Field(..., description="Clean name of target company")
    sector: str = Field(default="tecnológico", description="Sector of activity")
    decision_maker_role: str = Field(default="CTO", description="Target role (e.g. CTO, CISO, CEO)")
    contact_name: Optional[str] = Field(None, description="Contact person first name if known")
    specific_trigger_or_gap: Optional[str] = Field(None, description="Identified technical gap or business milestone")
    sender_name: str = Field(default="José Luis Rodríguez Casal", description="Outbound sender representative")
    sender_title: str = Field(default="Arquitecto de Soluciones IA & GRC Advisor", description="Sender title")

    def run(self) -> Dict[str, Any]:
        salutation = f"Hola {self.contact_name}," if self.contact_name else f"Hola equipo de {self.company_name},"

        # 1. Subject generation (strictly no spam triggers, authentic B2B style)
        subject_templates = {
            "CTO": f"Pipelines de IA y Automatización para {self.company_name} | {self.sender_name}",
            "CISO": f"Adecuación NIS2, DORA y Seguridad de IA en {self.company_name}",
            "CEO": f"Eficiencia operativa con agentes autónomos en {self.company_name}",
            "DEFAULT": f"Implementación de IA y Cumplimiento Normativo en {self.company_name}",
        }
        subject = subject_templates.get(self.decision_maker_role.upper(), subject_templates["DEFAULT"])

        # 2. Body construction
        trigger_sentence = (
            f"He estado analizando los procesos de {self.company_name} en el sector {self.sector} "
            f"y veo una oportunidad directa: {self.specific_trigger_or_gap}."
            if self.specific_trigger_or_gap
            else f"Sigo con gran interés el crecimiento de {self.company_name} dentro del sector {self.sector}."
        )

        value_points = [
            "🤖 <strong>Automatización de flujos con Agentes Autónomos:</strong> integración de RAG corporativo, atención técnica y tareas repetitivas de backoffice.",
            "🛡️ <strong>Seguridad normativa desde el diseño:</strong> cumplimiento estricto con EU AI Act, RGPD, NIS2 y DORA con evidencias auditables.",
            "⚡ <strong>Despliegue local y soberanía de datos:</strong> cero fugas de datos confidenciales hacia APIs públicas no reguladas.",
        ]

        html_body = f"""<p>{salutation}</p>
<p>{trigger_sentence} Me pongo en contacto porque ayudamos a empresas a <strong>implementar pipelines de Inteligencia Artificial aplicada</strong> con un retorno de inversión cuantificable desde el primer mes.</p>

<p><strong>Lo que podemos desplegar en {self.company_name}:</strong></p>
<ul>
  <li>{value_points[0]}</li>
  <li>{value_points[1]}</li>
  <li>{value_points[2]}</li>
</ul>

<p>¿Tendrías disponibilidad para una breve llamada de 10 minutos este jueves o viernes para explorar si tiene sentido para vuestro roadmap?</p>

<p>Un cordial saludo,<br>
<strong>{self.sender_name}</strong><br>
{self.sender_title}</p>
"""

        plain_body = f"""{salutation}

{trigger_sentence} Me pongo en contacto porque ayudamos a empresas a implementar pipelines de Inteligencia Artificial aplicada con retorno de inversión cuantificable desde el primer mes.

Lo que podemos desplegar en {self.company_name}:
- Automatización de flujos con Agentes Autónomos y RAG corporativo.
- Seguridad normativa desde el diseño (EU AI Act, RGPD, NIS2, DORA).
- Despliegue soberano sin fuga de datos confidenciales.

¿Tendrías disponibilidad para una breve llamada de 10 minutos este jueves o viernes para explorar si tiene sentido para vuestro roadmap?

Un cordial saludo,
{self.sender_name}
{self.sender_title}
"""

        return {
            "subject": subject,
            "html_body": html_body,
            "plain_body": plain_body,
            "target_company": self.company_name,
            "target_role": self.decision_maker_role,
        }
