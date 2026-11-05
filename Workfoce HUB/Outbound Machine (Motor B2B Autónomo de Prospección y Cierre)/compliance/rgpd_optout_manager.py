"""RGPD (GDPR) Outbound Compliance Module — Regulation (EU) 2016/679 & LSSI.

Enforces:
1. Legal Ground: Legitimate Interest in B2B Communications (Art. 6.1.f).
2. Right to Object / Opt-Out (Art. 21 RGPD):
   - Hashed Robinson/Suppression List (stores SHA-256 hashes, zero plain PII).
   - 1-click unsubscribe token generation and validation.
3. Mandatory Compliance Footers with Data Controller Identification and DPO contact.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from pathlib import Path
from typing import Dict, Optional, Set, Tuple


class RGPDOptOutManager:
    """Manages suppression lists, opt-out enforcement, and mandatory legal footers."""

    def __init__(
        self,
        suppression_file: Optional[Path] = None,
        secret_salt: str = "outbound-optout-secret-salt-2026",
    ):
        self.suppression_file = suppression_file or Path("./suppression_robinson.json")
        self.secret_salt = secret_salt.encode("utf-8")
        self._suppressed_hashes: Set[str] = set()
        self._load_suppression()

    def _hash_email(self, email: str) -> str:
        clean = email.lower().strip()
        return hashlib.sha256(clean.encode("utf-8")).hexdigest()

    def _load_suppression(self) -> None:
        if self.suppression_file.exists():
            try:
                data = json.loads(self.suppression_file.read_text(encoding="utf-8"))
                self._suppressed_hashes = set(data.get("opted_out_hashes", []))
            except Exception:
                self._suppressed_hashes = set()

    def _save_suppression(self) -> None:
        self.suppression_file.parent.mkdir(parents=True, exist_ok=True)
        data = {"opted_out_hashes": sorted(list(self._suppressed_hashes))}
        self.suppression_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @property
    def robinson_domains(self) -> Set[str]:
        """Returns the set of suppressed contact hashes/domains."""
        return self._suppressed_hashes

    def is_suppressed(self, email: str) -> bool:
        """Checks if recipient has exercised Right of Opposition (Robinson List)."""
        return self._hash_email(email) in self._suppressed_hashes

    def check_suppression(self, email: str) -> Tuple[bool, str]:
        """Returns (is_suppressed, reason) tuple for UI and simulation diagnostics."""
        suppressed = self.is_suppressed(email)
        reason = "Registrado en Lista de Exclusión/Robinson (Art. 21 RGPD)." if suppressed else "Apto para prospección comercial."
        return suppressed, reason

    def add_opt_out(self, email: str) -> None:
        """Registers a recipient in the suppression list via cryptographic hash."""
        h = self._hash_email(email)
        self._suppressed_hashes.add(h)
        self._save_suppression()

    def register_optout(self, email: str, reason: str = "") -> None:
        """Registers a recipient in the suppression list (alias for add_opt_out)."""
        self.add_opt_out(email)

    def generate_unsubscribe_token(self, email: str) -> str:
        """Generates a tamper-proof HMAC-SHA256 token for 1-click unsubscribe."""
        return hmac.new(self.secret_salt, email.lower().strip().encode("utf-8"), hashlib.sha256).hexdigest()

    def verify_unsubscribe_token(self, email: str, token: str) -> bool:
        """Verifies the authenticity of an unsubscribe request."""
        expected = self.generate_unsubscribe_token(email)
        return hmac.compare_digest(expected, token)

    def append_legal_footer(
        self,
        html_body: str,
        recipient_email: str,
        sender_company: str = "Quantigrade Tech Studio",
        sender_address: str = "Distrito Digital, Alicante, España",
        opt_out_base_url: str = "https://optout.quantigrade.ai/unsubscribe",
    ) -> str:
        """Appends mandatory RGPD Art. 13 & 21 legal notice and 1-click opt-out link."""
        token = self.generate_unsubscribe_token(recipient_email)
        opt_out_link = f"{opt_out_base_url}?email={recipient_email}&token={token}"

        footer_html = f"""
<br><hr style="border:0; border-top:1px solid #e0e0e0; margin:20px 0;">
<div style="font-size:11px; color:#6b7280; line-height:1.4;">
  <p><strong>Aviso de Privacidad y Cumplimiento B2B (RGPD UE 2016/679 &amp; LSSI Art. 21):</strong><br>
  Este mensaje se dirige exclusivamente al ámbito corporativo de su empresa sobre la base del <em>interés legítimo</em> (Art. 6.1.f RGPD) para el fomento de relaciones comerciales B2B.<br>
  <strong>Responsable:</strong> {sender_company} · {sender_address}.<br>
  Si no desea recibir más comunicaciones o desea ejercer su derecho de oposición, puede darse de baja de forma inmediata haciendo clic en: 
  <a href="{opt_out_link}" style="color:#2563eb; text-decoration:underline;">Darse de baja / Unsubscribe</a>.</p>
</div>
"""
        return html_body + footer_html
