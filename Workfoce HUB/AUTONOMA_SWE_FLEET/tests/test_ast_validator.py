import pytest
from core.step_contract import StepContract, AllowedInterface, PublicMethodSignature
from core.ast_seam_validator import ASTSeamValidator

def test_ast_validator_detects_forbidden_imports():
    contract = StepContract(
        contract_id="SC-02",
        bead_id="bead-test-02",
        title="Check forbidden imports",
        target_file="services/calc.py",
        test_file="tests/test_calc.py",
        allowed_interface=AllowedInterface(
            class_name="Calculator",
            functions=[PublicMethodSignature(name="compute", args=["a", "b"], return_type="int")]
        ),
        forbidden_imports=["os", "subprocess"]
    )

    bad_source = (
        "import os\n"
        "class Calculator:\n"
        "    def compute(self, a, b):\n"
        "        os.system('dir')\n"
        "        return a + b\n"
    )
    res = ASTSeamValidator.validate_source(bad_source, contract)
    assert res.is_valid is False
    assert any("FORBIDDEN_IMPORT" in v for v in res.violations)
    assert res.score < 100

def test_ast_validator_passes_compliant_deep_module():
    contract = StepContract(
        contract_id="SC-03",
        bead_id="bead-test-03",
        title="Check compliant module",
        target_file="services/secure_calc.py",
        test_file="tests/test_secure_calc.py",
        allowed_interface=AllowedInterface(
            class_name="SecureCalculator",
            functions=[PublicMethodSignature(name="compute", args=["a", "b"], return_type="int")],
            is_deep_module=True
        ),
        forbidden_imports=["pickle"]
    )

    good_source = (
        "class SecureCalculator:\n"
        "    def __init__(self):\n"
        "        self.base_offset = 10\n"
        "    def compute(self, a: int, b: int) -> int:\n"
        "        # Deep logic with verification\n"
        "        if a < 0 or b < 0:\n"
        "            raise ValueError('Must be positive')\n"
        "        return a + b + self.base_offset\n"
    )
    res = ASTSeamValidator.validate_source(good_source, contract)
    assert res.is_valid is True
    assert res.score == 100
    assert len(res.violations) == 0
