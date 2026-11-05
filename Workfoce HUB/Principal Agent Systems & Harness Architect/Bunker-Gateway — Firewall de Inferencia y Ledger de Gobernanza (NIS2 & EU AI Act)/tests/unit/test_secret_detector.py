"""Unit tests for SecretDetector."""

from bunker_gateway.firewall.secret_detector import SecretDetector


def test_secret_detector_detects_api_keys():
    detector = SecretDetector()

    # OpenAI API Key leak
    text_with_openai = "Mi clave de OpenAI es sk-abC1234567890defghijklmnopqrstuvwxYz"
    res1 = detector.scan_text(text_with_openai)
    assert res1.has_leak is True
    assert res1.secret_type == "OPENAI_API_KEY"
    assert "sk-abC1234567890" not in res1.redacted_text
    assert "[BLOCK_DATA_LEAK:OPENAI_API_KEY]" in res1.redacted_text

    # AWS Key
    text_with_aws = "Deploy using AKIAIOSFODNN7EXAMPLE credentials"
    res2 = detector.scan_text(text_with_aws)
    assert res2.has_leak is True
    assert res2.secret_type == "AWS_ACCESS_KEY"


def test_secret_detector_private_key():
    detector = SecretDetector()
    pem = "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA0...\n-----END RSA PRIVATE KEY-----"
    res = detector.scan_text(f"Aquí está la clave:\n{pem}")
    assert res.has_leak is True
    assert res.secret_type == "PRIVATE_CRYPTOGRAPHIC_KEY"


def test_clean_text_no_leak():
    detector = SecretDetector()
    clean = "Este es un texto normal sin secretos ni credenciales."
    res = detector.scan_text(clean)
    assert res.has_leak is False
    assert res.redacted_text == clean
