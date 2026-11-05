"""
Parser y Descompositor de Épicas de Jira / Linear / PRD en StepContracts Atómicos.
"""

from typing import Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from core.step_contract import StepContract, AllowedInterface, PublicMethodSignature, GherkinScenario


class ProductEpic(BaseModel):
    epic_id: str
    title: str
    description: str
    business_value: str
    target_microservice: str
    raw_requirements: list[str] = Field(default_factory=list)


class EpicParser:
    """Transformador de requerimientos de producto en contratos formales ejecutables."""

    @classmethod
    def decompose_into_step_contracts(cls, epic: ProductEpic) -> list[StepContract]:
        """Descompone una épica en 5 StepContracts ortogonales sin solapamiento de archivos."""
        now_iso = datetime.now(timezone.utc).isoformat()
        contracts: list[StepContract] = []

        # Contrato 1: Módulo de Autenticación y Tokens Criptográficos
        contracts.append(StepContract(
            contract_id=f"{epic.epic_id}-SC-01",
            bead_id=f"bead-{epic.epic_id.lower()}-01-auth",
            title="Implementar AuthTokenProvider con firma HMAC y rotación",
            target_file="services/auth_provider.py",
            test_file="tests/test_auth_provider.py",
            allowed_interface=AllowedInterface(
                class_name="AuthTokenProvider",
                functions=[
                    PublicMethodSignature(name="generate_token", args=["user_id", "scopes", "ttl_seconds"], return_type="str"),
                    PublicMethodSignature(name="verify_token", args=["token"], return_type="dict[str, Any]"),
                    PublicMethodSignature(name="revoke_token", args=["token"], return_type="bool")
                ],
                is_deep_module=True
            ),
            forbidden_imports=["pickle", "telnetlib", "ftplib"],
            scenarios=[
                GherkinScenario(
                    title="Emisión de token válido",
                    given="Un user_id autenticado con scope 'read:billing'",
                    when="Se invoca generate_token con TTL de 3600s",
                    then="Retorna un token firmado que verify_token valida exitosamente"
                )
            ],
            max_tokens_budget=40000,
            created_at=now_iso
        ))

        # Contrato 2: Módulo de Rate Limiting (Token Bucket)
        contracts.append(StepContract(
            contract_id=f"{epic.epic_id}-SC-02",
            bead_id=f"bead-{epic.epic_id.lower()}-02-ratelimit",
            title="Implementar SlidingWindowRateLimiter contra ataques DoS",
            target_file="middleware/rate_limiter.py",
            test_file="tests/test_rate_limiter.py",
            allowed_interface=AllowedInterface(
                class_name="SlidingWindowRateLimiter",
                functions=[
                    PublicMethodSignature(name="allow_request", args=["client_ip", "cost"], return_type="bool"),
                    PublicMethodSignature(name="get_remaining_budget", args=["client_ip"], return_type="int"),
                    PublicMethodSignature(name="reset_limits", args=["client_ip"], return_type="None")
                ],
                is_deep_module=True
            ),
            forbidden_imports=["pickle", "subprocess"],
            scenarios=[
                GherkinScenario(
                    title="Bloqueo tras superar umbral de peticiones",
                    given="Un cliente con límite de 60 req/minuto",
                    when="Realiza la petición número 61 en el mismo minuto",
                    then="allow_request retorna False con remaining_budget = 0"
                )
            ],
            max_tokens_budget=35000,
            created_at=now_iso
        ))

        # Contrato 3: Módulo de Suscripción y Facturación Recurrente
        contracts.append(StepContract(
            contract_id=f"{epic.epic_id}-SC-03",
            bead_id=f"bead-{epic.epic_id.lower()}-03-billing",
            title="Implementar SubscriptionLifecycleManager con gestión de estados",
            target_file="domain/subscription_manager.py",
            test_file="tests/test_subscription_manager.py",
            allowed_interface=AllowedInterface(
                class_name="SubscriptionLifecycleManager",
                functions=[
                    PublicMethodSignature(name="create_subscription", args=["customer_id", "plan_id", "amount"], return_type="dict[str, Any]"),
                    PublicMethodSignature(name="cancel_subscription", args=["subscription_id", "immediate"], return_type="bool"),
                    PublicMethodSignature(name="get_subscription_status", args=["subscription_id"], return_type="str")
                ],
                is_deep_module=True
            ),
            forbidden_imports=["sqlite3", "pickle"],
            scenarios=[
                GherkinScenario(
                    title="Creación y transición de estado de suscripción",
                    given="Un cliente con medio de pago válido registrado",
                    when="Se solicita suscripción al plan 'enterprise'",
                    then="El estado pasa a 'ACTIVE' con próxima fecha de renovación calculada"
                )
            ],
            max_tokens_budget=45000,
            created_at=now_iso
        ))

        # Contrato 4: Módulo de Bóveda y Trazabilidad de Auditoría
        contracts.append(StepContract(
            contract_id=f"{epic.epic_id}-SC-04",
            bead_id=f"bead-{epic.epic_id.lower()}-04-audit",
            title="Implementar ImmutableAuditLedger con encadenamiento SHA-256",
            target_file="security/audit_ledger.py",
            test_file="tests/test_audit_ledger.py",
            allowed_interface=AllowedInterface(
                class_name="ImmutableAuditLedger",
                functions=[
                    PublicMethodSignature(name="record_event", args=["event_type", "actor", "payload"], return_type="str"),
                    PublicMethodSignature(name="verify_integrity", args=[], return_type="tuple[bool, int]"),
                    PublicMethodSignature(name="export_audit_trail", args=["since_iso"], return_type="list[dict[str, Any]]")
                ],
                is_deep_module=True
            ),
            forbidden_imports=["pickle", "telnetlib"],
            scenarios=[
                GherkinScenario(
                    title="Inalterabilidad del registro de eventos",
                    given="Tres eventos de auditoría registrados secuencialmente",
                    when="Se verifica la integridad de la cadena",
                    then="verify_integrity retorna (True, 3)"
                )
            ],
            max_tokens_budget=35000,
            created_at=now_iso
        ))

        # Contrato 5: Módulo de Despachador de Webhooks Resiliente
        contracts.append(StepContract(
            contract_id=f"{epic.epic_id}-SC-05",
            bead_id=f"bead-{epic.epic_id.lower()}-05-webhook",
            title="Implementar ResilientWebhookDispatcher con reintentos exponenciales",
            target_file="integrations/webhook_dispatcher.py",
            test_file="tests/test_webhook_dispatcher.py",
            allowed_interface=AllowedInterface(
                class_name="ResilientWebhookDispatcher",
                functions=[
                    PublicMethodSignature(name="enqueue_event", args=["endpoint_url", "event_type", "data"], return_type="str"),
                    PublicMethodSignature(name="process_queue", args=["max_retries"], return_type="int"),
                    PublicMethodSignature(name="get_dead_letter_queue", args=[], return_type="list[dict[str, Any]]")
                ],
                is_deep_module=True
            ),
            forbidden_imports=["pickle", "ftplib"],
            scenarios=[
                GherkinScenario(
                    title="Reintento exponencial tras fallo transitorio HTTP 503",
                    given="Un webhook en cola con endpoint destino no disponible",
                    when="Falla el envío inicial",
                    then="El evento permanece en cola con backoff exponencial sin perderse"
                )
            ],
            max_tokens_budget=40000,
            created_at=now_iso
        ))

        return contracts
