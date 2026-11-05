import pytest
from core.step_contract import StepContract, AllowedInterface, PublicMethodSignature, GherkinScenario

def test_step_contract_conformance_check():
    contract = StepContract(
        contract_id="SC-01",
        bead_id="bead-test-01",
        title="Validar Token Provider",
        target_file="services/auth.py",
        test_file="tests/test_auth.py",
        allowed_interface=AllowedInterface(
            class_name="TokenProvider",
            functions=[
                PublicMethodSignature(name="issue_token", args=["user_id"], return_type="str")
            ]
        ),
        forbidden_imports=["pickle"]
    )

    valid_code = (
        "class TokenProvider:\n"
        "    def issue_token(self, user_id: str) -> str:\n"
        "        return 'valid_token'\n"
    )
    is_valid, violations = contract.validate_code_conformance(valid_code)
    assert is_valid is True
    assert len(violations) == 0

    invalid_code = (
        "import pickle\n"
        "class WrongClass:\n"
        "    pass\n"
    )
    is_valid, violations = contract.validate_code_conformance(invalid_code)
    assert is_valid is False
    assert any("FORBIDDEN_IMPORT" in v for v in violations)
    assert any("MISSING_INTERFACE" in v for v in violations)
