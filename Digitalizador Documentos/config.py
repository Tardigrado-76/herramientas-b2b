"""Configuration module for LALA Desktop Application.

Manages application constants and paths.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    """Application configuration container."""

    APP_NAME: str = "LALA — OCR For All Extractor"
    APP_VERSION: str = "3.0.0"
    FUZZY_MATCH_THRESHOLD: float = 72.0
    REQUEST_TIMEOUT_SECONDS: int = 60
    MAX_IMAGE_DIMENSION: int = 2048
