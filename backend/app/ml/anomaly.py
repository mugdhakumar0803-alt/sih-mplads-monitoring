"""
Owner: AI/ML.
Location: backend/ml/anomaly.py

Unsupervised anomaly/risk scoring for works, using Isolation Forest —
unsupervised because you don't have labeled "this was fraud" data.

The SHAP layer is what turns a bare "0.82 risk score" into the
`top_drivers` field from the API contract (e.g. "Cost 3.1x above median
for this work-type/region") — this is what section 3D/4 of the blueprint
calls the Cost Escalation Driver Analysis Module.
"""
import numpy as np
import pandas as pd
import shap
from dataclasses import dataclass
from sklearn.ensemble import IsolationForest

FEATURE_NAMES = [
    "cost_ratio_vs_category_median",
    "progress_vs_elapsed_time_ratio",
    "days_since_last_photo",
    "citizen_grievance_count",
]

# Human-readable explanation templates, one per feature, filled in with
# the actual value when SHAP flags that feature as a top driver.
_EXPLANATION_TEMPLATES = {
    "cost_ratio_vs_category_median": "Cost is {value:.1f}x the median for this work-type/region",
    "progress_vs_elapsed_time_ratio": "Physical progress ({value:.0%}) is far behind the elapsed time for this work",
    "days_since_last_photo": "No verified progress photo in {value:.0f} days",
    "citizen_grievance_count": "{value:.0f} citizen grievance(s) filed on this work",
}


@dataclass
class WorkFeatures:
    work_id: str
    cost_ratio_vs_category_median: float   # e.g. 1.0 = exactly the median, 3.0 = 3x the median
    progress_vs_elapsed_time_ratio: float  # e.g. 0.2 = only 20% as much progress as elapsed time would suggest
    days_since_last_photo: float
    citizen_grievance_count: float


def _to_dataframe(works: list[WorkFeatures]) -> pd.DataFrame:
    return pd.DataFrame([
        {name: getattr(w, name) for name in FEATURE_NAMES}
        for w in works
    ])


def train_model(historical_works: list[WorkFeatures]) -> IsolationForest:
    """
    Train on a reasonably large batch of historical/seed works (real data
    from Dataful.in, per Section 10 of the blueprint, ideally — synthetic
    is fine for a first pass). Retrain periodically as more real data
    comes in; this isn't a one-time thing.
    """
    df = _to_dataframe(historical_works)
    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(df)
    return model


def score_and_explain(model: IsolationForest, background_data: pd.DataFrame, work: WorkFeatures) -> dict:
    """
    Returns a dict matching the /works/{id}/anomaly-score response shape
    from the API contract: risk_score, risk_level, top_drivers.
    """
    work_df = pd.DataFrame([{name: getattr(work, name) for name in FEATURE_NAMES}])

    # IsolationForest's decision_function: lower/more negative = more anomalous.
    # We flip and rescale to a 0-1 "risk score" where higher = riskier,
    # which is what the API contract expects.
    raw_score = model.decision_function(work_df)[0]
    risk_score = float(np.clip(0.5 - raw_score, 0, 1))

    if risk_score >= 0.7:
        risk_level = "high"
    elif risk_score >= 0.4:
        risk_level = "medium"
    else:
        risk_level = "low"

    # SHAP explains WHICH features pushed this particular work's score up —
    # this is what makes top_drivers real instead of a guess.
    explainer = shap.Explainer(model.decision_function, background_data)
    shap_values = explainer(work_df)

    # Higher absolute SHAP value = bigger contributor to this work's score.
    contributions = list(zip(FEATURE_NAMES, shap_values.values[0]))
    contributions.sort(key=lambda x: abs(x[1]), reverse=True)

    top_drivers = []
    for feature_name, _ in contributions[:2]:  # top 2 drivers, keep it readable
        value = getattr(work, feature_name)
        top_drivers.append(_EXPLANATION_TEMPLATES[feature_name].format(value=value))

    return {
        "work_id": work.work_id,
        "risk_score": round(risk_score, 2),
        "risk_level": risk_level,
        "top_drivers": top_drivers,
    }


# --- Quick manual test ---
if __name__ == "__main__":
    # Simulate a batch of mostly-normal historical works to train the background model on
    rng = np.random.default_rng(42)
    historical = [
        WorkFeatures(
            work_id=f"HIST-{i}",
            cost_ratio_vs_category_median=rng.normal(1.0, 0.15),
            progress_vs_elapsed_time_ratio=rng.normal(1.0, 0.2),
            days_since_last_photo=rng.uniform(0, 30),
            citizen_grievance_count=rng.poisson(0.3),
        )
        for i in range(200)
    ]
    model = train_model(historical)
    background_df = _to_dataframe(historical)

    # A clearly anomalous work: costs 3x the median, barely any progress, no recent photo, 5 grievances
    suspicious_work = WorkFeatures(
        work_id="WRK-2026-00931",
        cost_ratio_vs_category_median=3.1,
        progress_vs_elapsed_time_ratio=0.15,
        days_since_last_photo=112,
        citizen_grievance_count=5,
    )
    result = score_and_explain(model, background_df, suspicious_work)
    print(result)

