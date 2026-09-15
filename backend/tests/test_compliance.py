from types import SimpleNamespace

from app.ml.compliance_engine import ComplianceEngine


def test_compliant_work_passes():
    result = ComplianceEngine().check_compliance(SimpleNamespace(category="road", risk_score=0))
    assert result["status"] == "compliant"
    assert result["score"] == 1.0


def test_high_risk_work_is_flagged():
    result = ComplianceEngine().check_compliance(SimpleNamespace(category="road", risk_score=0.9))
    assert result["status"] == "non_compliant"
    assert result["violations"]