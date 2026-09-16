# Demo Flow

## Realistic flow for the platform

1. User logs in through the app.
2. User is scoped to their role and state/district/constituency.
3. A real work list is loaded from the MPLADS dataset.
4. The user views work details, risk summary, and evidence status.
5. If GPS is available, the project is mapped spatially. If not, the app shows `GPS_UNAVAILABLE`.
6. If a citizen grievance is raised, it becomes a real record and enters the escalation workflow.
7. If evidence is absent, the app displays a transparent unavailable state.

## Not allowed

- random project lists
- static mock arrays for KPIs
- fabricated expenditures or coordinates
- fake MP dashboards
- static grievance or rating records

The end-to-end demo is valid only when database, backend, API, frontend, data, and tests are connected to a real source or honest unavailable state.
