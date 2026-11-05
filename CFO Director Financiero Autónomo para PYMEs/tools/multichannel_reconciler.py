"""Multichannel 4-Way Financial Reconciliation Engine.

Reconciles financial transactions across four enterprise channels:
1. Payment Gateways (Stripe, Adyen): Captured gross, processing fees, net payout.
2. Marketplaces & Ecommerce (Amazon SP-API, Mirakl, Shopify Plus): Merchant orders & commissions.
3. Logistics Carriers (SEUR, DHL, Correos): Delivery status, Cash-on-Delivery (COD) collections.
4. ERP General Ledger (Odoo JSON-RPC, SAP S/4HANA OData): Journal accounts 430 (Clients), 572 (Bank), 700 (Sales).
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class ChannelTransaction(BaseModel):
    tx_id: str
    channel: str  # STRIPE, MARKETPLACE, CARRIER, ERP
    order_ref: str
    gross_amount: float
    fee_amount: float = 0.0
    net_amount: float
    currency: str = "EUR"
    status: str  # CAPTURED, DELIVERED, BOOKED, PENDING
    timestamp: str = ""


class ReconciliationDiscrepancy(BaseModel):
    order_ref: str
    discrepancy_type: str  # FEE_MISMATCH, MISSING_ERP_ENTRY, CARRIER_UNCOLLECTED, TIMING_DIFFERENCE
    amount_diff: float
    affected_channels: list[str]
    description: str
    suggested_adjusting_entry: dict[str, Any]


class MultichannelReconciliationReport(BaseModel):
    batch_id: str
    total_orders_analyzed: int
    matched_count: int
    discrepancy_count: int
    total_gross_volume: float
    total_fees_audited: float
    total_discrepancy_amount: float
    discrepancies: list[ReconciliationDiscrepancy]
    reconciliation_seal: str
    reconciled_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class MultichannelReconciler:
    """Executes deterministic 4-way financial reconciliation."""

    def reconcile_batch(
        self,
        gateway_txs: list[ChannelTransaction],
        marketplace_txs: list[ChannelTransaction],
        carrier_txs: list[ChannelTransaction],
        erp_txs: list[ChannelTransaction],
    ) -> MultichannelReconciliationReport:
        """Cross-matches all four streams by order_ref."""
        orders: dict[str, dict[str, ChannelTransaction]] = {}

        for tx in gateway_txs:
            orders.setdefault(tx.order_ref, {})["GATEWAY"] = tx
        for tx in marketplace_txs:
            orders.setdefault(tx.order_ref, {})["MARKETPLACE"] = tx
        for tx in carrier_txs:
            orders.setdefault(tx.order_ref, {})["CARRIER"] = tx
        for tx in erp_txs:
            orders.setdefault(tx.order_ref, {})["ERP"] = tx

        discrepancies: list[ReconciliationDiscrepancy] = []
        matched_count = 0
        total_gross = 0.0
        total_fees = 0.0

        for order_ref, channels in orders.items():
            gtw = channels.get("GATEWAY")
            mkt = channels.get("MARKETPLACE")
            car = channels.get("CARRIER")
            erp = channels.get("ERP")

            if gtw:
                total_gross += gtw.gross_amount
                total_fees += gtw.fee_amount

            # 1. Check ERP Booking
            if (gtw or mkt) and not erp:
                diff_amt = gtw.net_amount if gtw else mkt.net_amount
                discrepancies.append(
                    ReconciliationDiscrepancy(
                        order_ref=order_ref,
                        discrepancy_type="MISSING_ERP_ENTRY",
                        amount_diff=diff_amt,
                        affected_channels=["ERP"],
                        description=f"Order '{order_ref}' captured in gateway/marketplace but absent from ERP Ledger.",
                        suggested_adjusting_entry={
                            "debit": "572000 (Bancos)",
                            "credit": "700000 (Ventas de Mercaderías)",
                            "amount": diff_amt,
                        },
                    )
                )
                continue

            # 2. Check Gateway vs Marketplace Gross
            if gtw and mkt and abs(gtw.gross_amount - mkt.gross_amount) > 0.01:
                diff_amt = round(abs(gtw.gross_amount - mkt.gross_amount), 2)
                discrepancies.append(
                    ReconciliationDiscrepancy(
                        order_ref=order_ref,
                        discrepancy_type="FEE_MISMATCH",
                        amount_diff=diff_amt,
                        affected_channels=["GATEWAY", "MARKETPLACE"],
                        description=f"Gross mismatch for order '{order_ref}': Gateway={gtw.gross_amount} vs Marketplace={mkt.gross_amount}",
                        suggested_adjusting_entry={
                            "debit": "669000 (Otros Gastos Financieros)",
                            "credit": "430000 (Clientes)",
                            "amount": diff_amt,
                        },
                    )
                )
                continue

            # 3. Check COD Carrier Settlement
            if car and car.status == "DELIVERED" and not gtw and not erp:
                discrepancies.append(
                    ReconciliationDiscrepancy(
                        order_ref=order_ref,
                        discrepancy_type="CARRIER_UNCOLLECTED",
                        amount_diff=car.gross_amount,
                        affected_channels=["CARRIER", "GATEWAY"],
                        description=f"Carrier delivered COD order '{order_ref}' but funds not yet remitted to bank.",
                        suggested_adjusting_entry={
                            "debit": "440000 (Deudores Varios - Carrier)",
                            "credit": "700000 (Ventas)",
                            "amount": car.gross_amount,
                        },
                    )
                )
                continue

            matched_count += 1

        total_disc_amt = sum(d.amount_diff for d in discrepancies)
        batch_id = f"REC-BATCH-{hashlib.sha256(str(orders.keys()).encode()).hexdigest()[:10].upper()}"
        seal = hashlib.sha256(f"{batch_id}:{matched_count}:{len(discrepancies)}:{total_gross}".encode()).hexdigest()

        return MultichannelReconciliationReport(
            batch_id=batch_id,
            total_orders_analyzed=len(orders),
            matched_count=matched_count,
            discrepancy_count=len(discrepancies),
            total_gross_volume=round(total_gross, 2),
            total_fees_audited=round(total_fees, 2),
            total_discrepancy_amount=round(total_disc_amt, 2),
            discrepancies=discrepancies,
            reconciliation_seal=seal,
        )
