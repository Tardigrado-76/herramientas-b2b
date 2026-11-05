"""Módulo Human-in-the-Loop (HITL) para autorización de pagos y transacciones críticas."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class PaymentApprovalRequest(BaseModel):
    request_id: str
    vendor_name: str
    vendor_cif: str
    amount: float
    destination_iban: str
    reason_for_review: str
    risk_score: int
    status: ApprovalStatus = ApprovalStatus.PENDING
    decided_by: str | None = None
    decided_at: str | None = None
    comments: str = ""


class HITLApprovalGate:
    """Gestor de aprobaciones humanas para operaciones que superan umbrales o presentan alertas."""

    def __init__(self, high_amount_threshold: float = 3000.0):
        self.threshold = high_amount_threshold
        self.requests: dict[str, PaymentApprovalRequest] = {}

    def evaluate_transaction(
        self,
        vendor_name: str,
        vendor_cif: str,
        amount: float,
        destination_iban: str,
        fraud_risk_score: int,
        fraud_flags: list[str]
    ) -> PaymentApprovalRequest | None:
        """Determina si una transacción requiere intervención humana obligatoria."""
        needs_hitl = False
        reasons: list[str] = []

        if fraud_risk_score >= 20:
            needs_hitl = True
            reasons.extend(fraud_flags)

        if amount >= self.threshold:
            needs_hitl = True
            reasons.append(f"Importe ({amount:,.2f} €) supera el umbral de supervisión manual ({self.threshold:,.2f} €).")

        if not needs_hitl:
            return None  # Aprobado automáticamente

        req_id = f"HITL-PAY-{len(self.requests) + 1:04d}"
        req = PaymentApprovalRequest(
            request_id=req_id,
            vendor_name=vendor_name,
            vendor_cif=vendor_cif,
            amount=amount,
            destination_iban=destination_iban,
            reason_for_review="; ".join(reasons),
            risk_score=fraud_risk_score,
            status=ApprovalStatus.PENDING
        )
        self.requests[req_id] = req
        return req

    def approve(self, request_id: str, approver_name: str, comment: str = "Aprobado manualmente") -> PaymentApprovalRequest:
        req = self.requests.get(request_id)
        if not req:
            raise KeyError(f"Petición {request_id} no encontrada.")
        req.status = ApprovalStatus.APPROVED
        req.decided_by = approver_name
        req.decided_at = datetime.now(timezone.utc).isoformat()
        req.comments = comment
        return req

    def reject(self, request_id: str, approver_name: str, reason: str = "Rechazado por riesgo de fraude") -> PaymentApprovalRequest:
        req = self.requests.get(request_id)
        if not req:
            raise KeyError(f"Petición {request_id} no encontrada.")
        req.status = ApprovalStatus.REJECTED
        req.decided_by = approver_name
        req.decided_at = datetime.now(timezone.utc).isoformat()
        req.comments = reason
        return req
