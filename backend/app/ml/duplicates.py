"""
Owner: AI/ML (NLP).
Location: backend/app/ml/duplicates.py

ADAPTED VERSION — your real Work model has NO latitude/longitude columns
(the "location" field is free text, not GPS). So this version uses
"same constituency" as the proximity signal instead of GPS distance.

This is a real, honest limitation worth saying in your demo: "we flag
duplicates using semantic similarity plus same constituency — full GPS-
based distance is a planned upgrade once we add geocoding" (the
fetch_combined_data.py script from earlier already does real geocoding
via Nominatim, if you want to add lat/long columns and wire that in later).
"""
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer, util

_model = SentenceTransformer("all-MiniLM-L6-v2")

SIMILARITY_THRESHOLD = 0.80


@dataclass
class WorkInput:
    """What the router/service passes in — matches your real Work model's
    field names (work_id, work_title, category, constituency)."""
    work_id: str
    work_title: str
    category: str
    constituency: str


@dataclass
class DuplicatePair:
    work_id_a: str
    work_id_b: str
    similarity: float
    reason: str


def find_duplicate_clusters(works: list[WorkInput]) -> list[DuplicatePair]:
    results: list[DuplicatePair] = []

    # Group by category AND constituency first — a hand pump in Pune and
    # an identically-worded hand pump in Nagpur are not duplicates, they're
    # just the same common work type in two different places.
    groups: dict[tuple[str, str], list[WorkInput]] = {}
    for w in works:
        key = (w.category, w.constituency)
        groups.setdefault(key, []).append(w)

    for (category, constituency), group in groups.items():
        if len(group) < 2:
            continue

        titles = [w.work_title for w in group]
        embeddings = _model.encode(titles, convert_to_tensor=True)

        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                sim_score = util.cos_sim(embeddings[i], embeddings[j]).item()
                if sim_score >= SIMILARITY_THRESHOLD:
                    results.append(DuplicatePair(
                        work_id_a=group[i].work_id,
                        work_id_b=group[j].work_id,
                        similarity=round(sim_score, 3),
                        reason=(
                            f"{sim_score:.0%} title similarity, same constituency "
                            f"({constituency}), same category ({category})"
                        ),
                    ))

    return results


# --- Quick manual test ---
if __name__ == "__main__":
    sample_works = [
        WorkInput("WRK-001", "Construction of drinking water hand pump, Rampur", "drinking_water", "Amritsar"),
        WorkInput("WRK-002", "Installation of hand pump for drinking water - Rampur village", "drinking_water", "Amritsar"),
        WorkInput("WRK-003", "Construction of drinking water hand pump, Shivpur", "drinking_water", "Nagpur"),
    ]
    pairs = find_duplicate_clusters(sample_works)
    for p in pairs:
        print(p)
    # Expect: WRK-001/WRK-002 flagged (same constituency, similar text).
    # WRK-003 NOT flagged — different constituency, even with similar text.