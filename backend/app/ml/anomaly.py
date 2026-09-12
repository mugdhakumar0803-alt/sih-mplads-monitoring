"""
Owner: AI/ML.
Location: backend/ml/anomaly.py

Unsupervised anomaly/risk scoring for works, using Isolation Forest.
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


_EXPLANATION_TEMPLATES = {
    "cost_ratio_vs_category_median":
        "Cost is {value:.1f}x the median for this work-type/region",

    "progress_vs_elapsed_time_ratio":
        "Physical progress ({value:.0%}) is far behind the elapsed time for this work",

    "days_since_last_photo":
        "No verified progress photo in {value:.0f} days",

    "citizen_grievance_count":
        "{value:.0f} citizen grievance(s) filed on this work",
}


@dataclass
class WorkFeatures:
    work_id: str
    cost_ratio_vs_category_median: float
    progress_vs_elapsed_time_ratio: float
    days_since_last_photo: float
    citizen_grievance_count: float


def _to_dataframe(works: list[WorkFeatures]) -> pd.DataFrame:
    return pd.DataFrame([
        {name: getattr(work, name) for name in FEATURE_NAMES}
        for work in works
    ])


def train_model(
    historical_works: list[WorkFeatures],
) -> IsolationForest:

    df = _to_dataframe(historical_works)

    model = IsolationForest(
        contamination=0.1,
        random_state=42,
    )

    model.fit(df)

    return model


def score_and_explain(
    model: IsolationForest,
    background_data: pd.DataFrame,
    work: WorkFeatures,
) -> dict:

    work_df = pd.DataFrame([
        {
            name: getattr(work, name)
            for name in FEATURE_NAMES
        }
    ])

    # Lower Isolation Forest score = more anomalous.
    raw_score = model.decision_function(work_df)[0]

    # Convert to 0-1 risk score.
    risk_score = float(
        np.clip(0.5 - raw_score, 0, 1)
    )

    if risk_score >= 0.7:
        risk_level = "high"
    elif risk_score >= 0.4:
        risk_level = "medium"
    else:
        risk_level = "low"

    # SHAP explanation
    explainer = shap.Explainer(
        model.decision_function,
        background_data,
    )

    shap_values = explainer(work_df)

    contributions = list(
        zip(
            FEATURE_NAMES,
            shap_values.values[0],
        )
    )

    contributions.sort(
        key=lambda x: abs(x[1]),
        reverse=True,
    )

    top_drivers = []

    for feature_name, _ in contributions[:2]:
        value = getattr(work, feature_name)

        top_drivers.append(
            _EXPLANATION_TEMPLATES[feature_name].format(
                value=value
            )
        )

    return {
        "work_id": work.work_id,
        "risk_score": round(risk_score, 2),
        "risk_level": risk_level,
        "top_drivers": top_drivers,
    }


def score_works(
    works: list[WorkFeatures],
) -> list[dict]:
    """
    Train an Isolation Forest model on the supplied works
    and return risk scores with explanations.
    """

    if not works:
        return []

    model = train_model(works)

    background_data = _to_dataframe(works)

    return [
        score_and_explain(
            model,
            background_data,
            work,
        )
        for work in works
    ]


# --- Quick manual test ---

if __name__ == "__main__":

    rng = np.random.default_rng(42)

    historical = [
        WorkFeatures(
            work_id=f"HIST-{i}",
            cost_ratio_vs_category_median=rng.normal(
                1.0, 0.15
            ),
            progress_vs_elapsed_time_ratio=rng.normal(
                1.0, 0.2
            ),
            days_since_last_photo=rng.uniform(
                0, 30
            ),
            citizen_grievance_count=rng.poisson(
                0.3
            ),
        )
        for i in range(200)
    ]

    model = train_model(historical)

    background_df = _to_dataframe(historical)

    suspicious_work = WorkFeatures(
        work_id="WRK-2026-00931",
        cost_ratio_vs_category_median=3.1,
        progress_vs_elapsed_time_ratio=0.15,
        days_since_last_photo=112,
        citizen_grievance_count=5,
    )

    result = score_and_explain(
        model,
        background_df,
        suspicious_work,
    )

    print(result)