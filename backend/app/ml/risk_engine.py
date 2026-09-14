"""
Owner: AI/ML.
Location: backend/app/ml/risk_engine.py

Single source of truth for a work's overall risk. Combines the outputs
of anomaly.py, delay.py, duplicates.py, compliance_engine.py, and the
grievance count into ONE score with clear, human-readable reasons —
this is what the frontend's risk badges and the "Why flagged?" section
on a project detail page should read from, instead of each page
independently calling five different modules.

IMPORTANT: this file does not itself run any model — it takes already-
computed sub-scores (each 0.0 to 1.0) as input. The router/service layer
is responsible for calling anomaly.py, delay.py, etc. first, then
passing their outputs in here to combine.
"""
from dataclasses import dataclass


@dataclass
class RiskResult:
    score: float
    level: str
    drivers: list[str]


class RiskEngine:
    """
    Weights are a starting point, not gospel — cost anomalies are weighted
    highest (0.30) because that's the clearest fraud signal per the real
    Gujarat CAG case; adjust these once you see how real flagged works
    behave in your own data.
    """

    WEIGHTS = {
        "cost_risk": 0.30,
        "delay_risk": 0.20,
        "duplicate_risk": 0.20,
        "grievance_risk": 0.10,
        "compliance_risk": 0.20,
    }

    HIGH_THRESHOLD = 0.75
    MEDIUM_THRESHOLD = 0.45
    DRIVER_THRESHOLD = 0.7  # a sub-score above this gets named as a reason

    def calculate(
        self,
        cost_risk: float,
        delay_risk: float,
        duplicate_risk: float,
        grievance_risk: float,
        compliance_risk: float,
    ) -> RiskResult:
        score = (
            cost_risk * self.WEIGHTS["cost_risk"]
            + delay_risk * self.WEIGHTS["delay_risk"]
            + duplicate_risk * self.WEIGHTS["duplicate_risk"]
            + grievance_risk * self.WEIGHTS["grievance_risk"]
            + compliance_risk * self.WEIGHTS["compliance_risk"]
        )
        score = max(0.0, min(1.0, score))

        if score >= self.HIGH_THRESHOLD:
            level = "high"
        elif score >= self.MEDIUM_THRESHOLD:
            level = "medium"
        else:
            level = "low"

        drivers = []
        if cost_risk >= self.DRIVER_THRESHOLD:
            drivers.append("Unusual expenditure pattern")
        if delay_risk >= self.DRIVER_THRESHOLD:
            drivers.append("Project significantly behind schedule")
        if duplicate_risk >= self.DRIVER_THRESHOLD:
            drivers.append("Possible duplicate work nearby")
        if grievance_risk >= self.DRIVER_THRESHOLD:
            drivers.append("Multiple unresolved citizen grievances")
        if compliance_risk >= self.DRIVER_THRESHOLD:
            drivers.append("Statutory compliance violation")

        return RiskResult(score=round(score, 3), level=level, drivers=drivers)


# --- Quick manual test ---
if __name__ == "__main__":
    engine = RiskEngine()
    result = engine.calculate(
        cost_risk=0.9,
        delay_risk=0.8,
        duplicate_risk=0.3,
        grievance_risk=0.6,
        compliance_risk=0.2,
    )
    print(result)