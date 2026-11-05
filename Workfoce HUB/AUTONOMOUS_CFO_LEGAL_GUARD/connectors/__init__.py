"""Conectores SDP (Semantic Discovery Protocol) para ERPs, Software Contable y Banca PSD2."""

from connectors.sdp_engine import SDPConnectorRegistry, ConnectorMetadata
from connectors.holded import HoldedConnector
from connectors.a3_innuva import A3InnuvaConnector
from connectors.sage50 import Sage50Connector
from connectors.psd2_banking import PSD2BankingGateway

__all__ = [
    "SDPConnectorRegistry",
    "ConnectorMetadata",
    "HoldedConnector",
    "A3InnuvaConnector",
    "Sage50Connector",
    "PSD2BankingGateway",
]
