"""
Owner: AI/ML (NLP).
Location: backend/app/ml/category_classifier.py

The MPLADS.csv file's own CATEGORY column is nearly useless (98.8% of
rows just say "Normal/Others"). The REAL category is hiding inside the
WORK text field instead — e.g. "Installing community drinking water
plants" should become category = drinking_water.

Two-step approach:
  1. Fast keyword matching first — catches the vast majority of cases,
     explainable, no model needed.
  2. Semantic fallback (same zero-shot trick as grievance_triage.py) for
     anything the keywords miss — compares the WORK text against a short
     description of each category and picks the closest match.
"""
from __future__ import annotations

from sentence_transformers import SentenceTransformer, util

_model = SentenceTransformer("all-MiniLM-L6-v2")  # same model used everywhere else in ml/

# Keyword lists — lowercase, checked as substrings against the WORK text.
# Add more keywords here any time you spot a WORK description that isn't
# matching correctly; this list will never be "complete," and that's fine.
CATEGORY_KEYWORDS = {
    "drinking_water": ["drinking water", "hand pump", "tubewell", "tube well", "water plant", "water supply", "borewell", "bore well"],
    "road": ["road", "pathway", "link road", "bridge", "culvert", "drainage"],
    "street_lighting": ["street light", "streetlight", "solar light", "lighting"],
    "sanitation": ["toilet", "sanitation", "sewerage", "waste management", "drainage system"],
    "education": ["school", "classroom", "education", "library", "anganwadi"],
    "health": ["hospital", "dispensary", "health center", "health centre", "primary health"],
    "community_infrastructure": ["community hall", "community center", "community centre", "panchayat bhawan", "cremation", "burial"],
    "electrification": ["electrification", "electric", "power supply", "transformer"],
    "sports": ["playground", "stadium", "sports", "gymnasium"],
    "irrigation": ["irrigation", "canal", "check dam", "pond", "water harvesting"],
}

# Short description of each category, used ONLY for the semantic fallback —
# these are compared against the WORK text with embeddings, not keywords.
_CATEGORY_DESCRIPTIONS = {
    "drinking_water": "Providing clean drinking water access to a village or area",
    "road": "Building or repairing roads, pathways, or bridges",
    "street_lighting": "Installing lights along streets or public areas",
    "sanitation": "Toilets, sewerage, or waste management facilities",
    "education": "School buildings, classrooms, or educational facilities",
    "health": "Hospitals, dispensaries, or health centers",
    "community_infrastructure": "Community halls or public gathering spaces",
    "electrification": "Electric power supply infrastructure",
    "sports": "Playgrounds, stadiums, or sports facilities",
    "irrigation": "Irrigation canals, check dams, or water harvesting for farming",
    "other": "A public work that does not clearly fit any specific category above",
}
_category_names = list(_CATEGORY_DESCRIPTIONS.keys())
_category_embeddings = _model.encode(list(_CATEGORY_DESCRIPTIONS.values()), convert_to_tensor=True)


def _classify_by_keywords(work_text: str) -> str | None:
    text_lower = work_text.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in text_lower for keyword in keywords):
            return category
    return None


def _classify_by_semantic_fallback(work_text: str) -> str:
    text_embedding = _model.encode(work_text, convert_to_tensor=True)
    scores = util.cos_sim(text_embedding, _category_embeddings)[0]
    best_idx = int(scores.argmax())
    return _category_names[best_idx]


def classify_work_category(work_text: str) -> str:
    """Main entry point — try fast keywords first, fall back to semantic matching."""
    keyword_result = _classify_by_keywords(work_text)
    if keyword_result:
        return keyword_result
    return _classify_by_semantic_fallback(work_text)


# --- Quick manual test ---
if __name__ == "__main__":
    examples = [
        "NA - Installing community drinking water plants",
        "NA - Street lights",
        "NA - Construction of roads, link roads, pathways or any other road with or without drainage system",
        "Construction of a community hall for village gatherings",
        "Setting up a new primary health sub-center",
    ]
    for text in examples:
        print(f"{classify_work_category(text):25s} <- {text}")