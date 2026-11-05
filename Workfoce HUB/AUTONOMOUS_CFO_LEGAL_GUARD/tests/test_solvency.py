import pytest
from cfo_core.solvency import AltmanZScoreCalculator, SolvencyZone

def test_altman_z_score_safe_zone():
    result = AltmanZScoreCalculator.calculate(
        working_capital=200000.0,
        retained_earnings=300000.0,
        ebit=150000.0,
        equity=500000.0,
        total_liabilities=200000.0,
        sales=1500000.0,
        total_assets=800000.0
    )
    assert result.altman_z_prime > 2.90
    assert result.zone == SolvencyZone.SAFE_ZONE
    assert result.bankruptcy_risk_pct < 10.0

def test_altman_z_score_distress_zone():
    result = AltmanZScoreCalculator.calculate(
        working_capital=-50000.0,
        retained_earnings=-100000.0,
        ebit=-30000.0,
        equity=20000.0,
        total_liabilities=400000.0,
        sales=300000.0,
        total_assets=350000.0
    )
    assert result.altman_z_prime < 1.23
    assert result.zone == SolvencyZone.DISTRESS_ZONE
    assert result.bankruptcy_risk_pct > 70.0
