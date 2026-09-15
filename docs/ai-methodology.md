# AI and Analytics Methodology

Risk is an explainable peer-rule score (`peer-rules-v1`) composed of cost deviation, age/status delay, duplicate-candidate similarity, unresolved grievances, and deterministic compliance violations. Peer cost uses the median allocation for works in the same state and category. A risk result is a potential irregularity signal, never a fraud determination.

Photo verification uses uploaded-image SHA-256 hashes, EXIF GPS extraction, and haversine distance. Missing GPS or missing project coordinates produces an unverifiable result.

Duplicate candidates use normalized work descriptions and same-state/category peer comparisons. They require human verification.

Synthetic training features in `ml/training/seed_from_dataful.py` are training conveniences only and must not be shown as government measurements.