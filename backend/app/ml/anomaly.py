"""
Owner: AI/ML.

Location: backend/app/ml/anomaly.py

Unsupervised anomaly/risk scoring for works using Isolation Forest.

The SHAP layer explains which features contribute most to the
anomaly/risk score.
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


# Human-readable explanation templates.
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

    # 1.0 = exactly the median, 3.0 = 3x the median
    cost_ratio_vs_category_median: float

    # Example: 0.2 = only 20% as much progress as expected
    progress_vs_elapsed_time_ratio: float

    days_since_last_photo: float

    citizen_grievance_count: float


def _to_dataframe(works: list[WorkFeatures]) -> pd.DataFrame:
    """
    Convert WorkFeatures objects into a pandas DataFrame
    containing only the ML feature columns.
    """

    return pd.DataFrame(
        [
            {
                name: getattr(work, name)
                for name in FEATURE_NAMES
            }
            for work in works
        ]
    )


def train_model(
    historical_works: list[WorkFeatures],
) -> IsolationForest:
    """
    Train an Isolation Forest model on historical works.
    """

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
    """
    Calculate anomaly risk score and explain the main contributing
    features for a single work.

    Returns:
        work_id
        risk_score
        risk_level
        top_drivers
    """

    work_df = pd.DataFrame(
        [
            {
                name: getattr(work, name)
                for name in FEATURE_NAMES
            }
        ]
    )

    # IsolationForest decision_function:
    # lower / more negative = more anomalous.
    #
    # Flip and rescale it to a 0-1 risk score.
    raw_score = model.decision_function(work_df)[0]

    risk_score = float(
        np.clip(0.5 - raw_score, 0, 1)
    )

    if risk_score >= 0.7:
        risk_level = "high"
    elif risk_score >= 0.4:
        risk_level = "medium"
    else:
        risk_level = "low"

    # SHAP explains which features contributed most
    # to the anomaly score.
    explainer = shap.Explainer(
        model.decision_function,
        background_data,
    )

    shap_values = explainer(work_df)

    # Higher absolute SHAP value means a larger contribution.
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

    # Return the top 2 drivers.
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
    Calculate anomaly/risk scores for multiple works.

    This function is used by WorkService.calculate_risk_scores().
    """

    if not works:
        return []

    # Train the Isolation Forest using the supplied works
    # as the historical/background dataset.
    model = train_model(works)

    background_data = _to_dataframe(works)

    # Score and explain every work.
    results = [
        score_and_explain(
            model,
            background_data,
            work,
        )
        for work in works
    ]

    return results


# ---------------------------------------------------------
# Quick manual test
# ---------------------------------------------------------

if __name__ == "__main__":

    # Simulate mostly-normal historical works.
    rng = np.random.default_rng(42)

    historical = [
        WorkFeatures(
            work_id=f"HIST-{i}",
            cost_ratio_vs_category_median=rng.normal(
                1.0,
                0.15,
            ),
            progress_vs_elapsed_time_ratio=rng.normal(
                1.0,
                0.2,
            ),
            days_since_last_photo=rng.uniform(
                0,
                30,
            ),
            citizen_grievance_count=rng.poisson(
                0.3,
            ),
        )
        for i in range(200)
    ]

    model = train_model(historical)

    background_df = _to_dataframe(historical)

    # A clearly anomalous work:
    # - costs 3x the median
    # - barely any progress
    # - no recent photo
    # - 5 grievances
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

