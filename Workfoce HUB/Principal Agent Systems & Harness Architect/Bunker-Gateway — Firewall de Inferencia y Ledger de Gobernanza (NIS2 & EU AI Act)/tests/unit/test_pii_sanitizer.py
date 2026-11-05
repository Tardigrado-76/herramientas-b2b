"""Unit tests for PIIVault bidirectional redaction and rehydration."""

from bunker_gateway.firewall.pii_sanitizer import PIIVault


def test_pii_redaction_and_rehydration():
    vault = PIIVault()
    raw_prompt = "El cliente Juan Perez con DNI 12345678Z e IBAN ES9121000418450200051332 solicita credito."
    session_id = "sess_test_101"

    redacted, token_map = vault.redact(raw_prompt, session_id=session_id)

    assert "12345678Z" not in redacted
    assert "ES9121000418450200051332" not in redacted
    assert "[REDACTED_DNI_1]" in redacted
    assert "[REDACTED_IBAN_1]" in redacted

    # Outbound Rehydration
    rehydrated = vault.rehydrate(redacted, session_id=session_id)
    assert rehydrated == raw_prompt


def test_pii_multiple_emails_and_phones():
    vault = PIIVault()
    text = "Contacto: juan.dev@empresa.com y telefono +34 612345678"
    redacted, tokens = vault.redact(text, session_id="sess_contact")

    assert "juan.dev@empresa.com" not in redacted
    assert "+34 612345678" not in redacted
    assert "[REDACTED_EMAIL_1]" in redacted
    assert "[REDACTED_PHONE_1]" in redacted

    rehydrated = vault.rehydrate(redacted, session_id="sess_contact")
    assert rehydrated == text
