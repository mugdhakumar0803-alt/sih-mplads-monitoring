# ML Pipeline

## Current ML status

The repository contains basic ML-related modules for:
- anomaly detection
- compliance logic
- duplicate detection
- multilingual support
- classification of work categories

## What is real

The duplicate detection utility is implemented and tested to compare similar work descriptions and proximity signals.

## What is not real yet

No production-grade ML pipeline exists for:
- cost anomaly detection using real expenditure data
- delay prediction using actual milestones
- force-majeure determination based on real disaster signals
- documentation of model training provenance
- explicit feature provenance for every score

## Rule

Any ML result must be a risk indicator or anomaly candidate, not definitive proof of wrongdoing. The platform must never claim fraud based solely on a model.
