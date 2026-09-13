# Duplicate MPLADS work detection
"""
Owner: AI/ML (NLP).
Location: backend/ml/duplicates.py

Detects likely-duplicate MPLADS works by combining:
1. Semantic similarity of the work DESCRIPTION (this is the NLP piece —
   catches "hand pump installation, Rampur" vs "drinking water hand pump,
   Rampur village" as the same thing, which exact-text matching would miss)
2. Geographic proximity (GPS distance) — two similar-sounding works far
   apart are probably NOT duplicates, they're just the same common
   work-type happening in different places

Imported and called from backend/routers/ai_detection.py — this file has
no FastAPI code in it, it's pure logic, easy to test on its own.
"""
from dataclasses import dataclass
from math import radians, sin, cos, sqrt, atan2
from sentence_transformers import SentenceTransformer, util

# Loaded once at startup, reused for every request — loading this model
# per-request would be far too slow.
_model = SentenceTransformer("all-MiniLM-L6-v2")  # small, fast, good enough for this task

# Tune these two thresholds based on what you see in your real/seed data —
# start here and adjust after looking at a few flagged pairs.
SIMILARITY_THRESHOLD = 0.80      # 0 to 1, cosine similarity of description embeddings
MAX_DISTANCE_METERS = 500        # works farther apart than this are not flagged, even if text matches


@dataclass
class Work:
    work_id: str
    description: str
    latitude: float
    longitude: float
    category: str


@dataclass
class DuplicatePair:
    work_id_a: str
    work_id_b: str
    similarity_score: float
    distance_meters: float
    reason: str


def _haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Straight-line distance between two GPS points, in meters."""
    R = 6371000  # Earth radius in meters
    phi1, phi2 = radians(lat1), radians(lat2)
    d_phi = radians(lat2 - lat1)
    d_lambda = radians(lon2 - lon1)
    a = sin(d_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(d_lambda / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def find_duplicate_clusters(works: list[Work]) -> list[DuplicatePair]:
    """
    Compares every work against every other work in the SAME category
    (comparing a hand pump to a road is pointless — narrowing to same
    category first also makes this much faster on a large dataset).

    Returns pairs that are both textually similar AND geographically close.
    """
    results: list[DuplicatePair] = []

    # Group by category first — cuts down comparisons a lot, and two works
    # in different categories are never duplicates of each other regardless
    # of how similar their descriptions sound.
    by_category: dict[str, list[Work]] = {}
    for w in works:
        by_category.setdefault(w.category, []).append(w)

    for category, group in by_category.items():
        if len(group) < 2:
            continue

        descriptions = [w.description for w in group]
        embeddings = _model.encode(descriptions, convert_to_tensor=True)

        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                sim_score = util.cos_sim(embeddings[i], embeddings[j]).item()
                if sim_score < SIMILARITY_THRESHOLD:
                    continue

                dist_m = _haversine_distance_m(
                    group[i].latitude, group[i].longitude,
                    group[j].latitude, group[j].longitude,
                )
                if dist_m > MAX_DISTANCE_METERS:
                    continue

                results.append(DuplicatePair(
                    work_id_a=group[i].work_id,
                    work_id_b=group[j].work_id,
                    similarity_score=round(sim_score, 3),
                    distance_meters=round(dist_m, 1),
                    reason=(
                        f"Description similarity {sim_score:.0%}, "
                        f"{dist_m:.0f}m apart, same category '{category}'"
                    ),
                ))

    return results


# --- Quick manual test — run this file directly to sanity-check it works ---
if __name__ == "__main__":
    sample_works = [
        Work("WRK-001", "Construction of drinking water hand pump, Rampur village", 18.5204, 73.8567, "drinking_water"),
        Work("WRK-002", "Installation of hand pump for drinking water - Rampur", 18.5203, 73.8569, "drinking_water"),
        Work("WRK-003", "Construction of drinking water hand pump, Shivpur village", 19.1000, 74.2000, "drinking_water"),
    ]
    pairs = find_duplicate_clusters(sample_works)
    for p in pairs:
        print(p)
    # Expect: WRK-001 and WRK-002 flagged (similar text, ~12m apart).
    # WRK-003 should NOT be flagged — far away, even though category matches.