# Data Lineage

## MPLADS source lineage

Digital CSV source
→ import pipeline in `backend/app/data_pipeline.py`
→ database table `works`
→ API `GET /works`
→ frontend work registry and project detail views

## User-generated evidence lineage

Citizen upload
→ photo verification service
→ `photos` table and hash checks
→ API `/photos/verify`
→ evidence panel in project detail pages

## Grievance lineage

Citizen grievance
→ `grievances` table
→ SLA escalation logic
→ alert record creation
→ district/state/MP dashboards

## Risk lineage

Work metadata + duplicate logic + grievances + compliance data
→ `ai_detection` or risk engine
→ `risk_score`, `risk_level`, `anomaly_drivers`
→ risk panel and dashboard alerts

## Missing lineage

The following are not yet available in the repository and therefore remain intentionally unavailable:
- MP master from Digital Sansad
- PostGIS constituency geometry
- state/district boundary hierarchy
- financial payment logs
- disaster event feed
- satellite imagery integration

This project must preserve an explicit unavailable state for any lineage step with no source.
