"""Explainable MPLADS compliance rules."""

from typing import Any


class ComplianceEngine:
    """Evaluate category and basic progress requirements without model I/O."""

    REQUIRED_PROGRESS = 0.75
    PRIORITY_ALLOCATION = {"sc": 0.15, "st": 0.075}

    def check_compliance(self, work: Any) -> dict:
        violations: list[str] = []
        recommendations: list[str] = []
        category = getattr(getattr(work, "category", None), "value", getattr(work, "category", ""))
        if not category:
            violations.append("Work category is missing")
            recommendations.append("Classify the work before approval")

        risk_score = float(getattr(work, "risk_score", 0) or 0)
        if risk_score >= 0.7:
            violations.append("Work has a high anomaly risk score")
            recommendations.append("Complete field verification before release")

        score = max(0.0, 1.0 - min(1.0, len(violations) * 0.25))
        return {
            "status": "compliant" if not violations else "non_compliant",
            "score": round(score, 2),
            "violations": violations,
            "recommendations": recommendations,
        }