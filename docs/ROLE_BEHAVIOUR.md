# Role Behaviour

- Citizen: public projects, scoped by profile state/district when present, project details, grievances, eligible completed-project ratings, grounded chatbot.
- MP: only works matching authenticated normalized constituency/source identity; constituency KPIs, risks, grievances, evidence, compliance, fund gates, separate citizen ratings.
- District authority: works matching district assignment, risk/evidence/grievance escalation and fund workflows.
- State official: works matching state assignment, state analytics, escalation, compliance, and leaderboards.
- Ministry: national aggregate and systemic views.
- Admin: provisioning and operational controls.

Backend authorization is authoritative. Frontend role selection never grants access.
