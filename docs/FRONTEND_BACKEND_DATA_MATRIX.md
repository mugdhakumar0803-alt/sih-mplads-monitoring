# FRONTEND_BACKEND_DATA_MATRIX - Complete API Integration Map

**Document Purpose:** Trace every frontend component to its backend API data source

**Status:** Complete data integration mapping after Phase 1-4 implementation

---

## EXECUTIVE SUMMARY

| Component | API Source | Status | Data Freshness |
|-----------|-----------|--------|-----------------|
| **Landing Page** | None (static) | ✅ | N/A |
| **Login/Register** | POST /auth/login, POST /auth/register | ✅ | Real-time |
| **Citizen Dashboard** | GET /dashboard/summary (filtered by user location) | ✅ | Real-time |
| **MP Dashboard** | GET /dashboard/summary (filtered by constituency) | ✅ | Real-time |
| **District Dashboard** | GET /api/analytics/state-stats/{state}/{district} | ✅ | Real-time |
| **State Dashboard** | GET /api/analytics/state-stats/{state} | ✅ | Real-time |
| **Ministry Dashboard** | GET /dashboard/summary (national aggregation) | ✅ | Real-time |
| **Work Detail Page** | GET /works/{id}, GET /photos/{work_id}, GET /grievances | ✅ | Real-time |
| **Map Component** | GET /reference/constituencies (GeoJSON) | ⚠️ READY | Real-time |
| **Historical Charts** | GET /reference/yearly-finance-historical | ✅ | Historical |
| **State Finance Charts** | GET /reference/state-finance-historical | ✅ | Historical |

---

## SECTION 1: DASHBOARD COMPONENTS → API MAPPING

### CitizenDashboard (Role: citizen)

| Component | Displays | API Endpoint | Data Fields | Refresh |
|-----------|----------|-------------|------------|---------|
| Summary Stats Card | Total projects, Sanctioned, In Progress, Completed | GET /dashboard/summary | total_projects, sanctioned, in_progress, completed | Real-time |
| Budget Overview | Total allocation, Total expenditure, Utilization % | GET /dashboard/summary | total_allocation, total_expenditure, utilization_percentage | Real-time |
| Risk Breakdown | High/Medium/Low risk count | GET /dashboard/summary | risk_breakdown | Real-time |
| Grievance Counter | Open grievances, Escalated | GET /dashboard/summary | open_grievances, escalated_grievances | Real-time |
| Project List | Works in citizen's region | GET /works?state={state}&district={district} | work_id, title, status, category | Real-time |
| Status Distribution Chart | Pie chart of work status | GET /dashboard/status-distribution | {status: count} | Real-time |
| Category Breakdown | Bar chart by sector | GET /dashboard/work-by-category | {category: count} | Real-time |

**Data Flow:**
```
Frontend: CitizenDashboard.jsx
  ↓
useEffect → fetch('/dashboard/summary')
  ↓
Backend: /dashboard/summary endpoint
  - Query: works table (filtered by user.state/district/constituency)
  - Query: grievances table (works linked to filtered works)
  - Query: fund_releases table
  ↓
Database: works, grievances, fund_releases tables
  ↓
Response: JSON with all stats ✅ REAL DATA
  ↓
Frontend: Update state, render charts ✅ NO HARDCODING
```

---

### MPDashboard (Role: mp)

| Component | Displays | API Endpoint | Filtering |
|-----------|----------|-------------|-----------|
| My Constituency Stats | Projects in MP's constituency | GET /dashboard/summary | constituency == user.constituency |
| Project Performance | Sanctioned vs Completed ratio | GET /api/analytics/mp-stats/{constituency} | Work.constituency |
| Financial Summary | Budget vs Expenditure | GET /api/analytics/mp-stats/{constituency} | SUM(allocation), SUM(expenditure) |
| Risk Indicators | High-risk projects | GET /dashboard/risk-analysis | constituency filter |
| Grievance Tracker | Complaints by project | GET /grievances?constituency={constituency} | Work.constituency FK |

**Backend Implementation:**
```python
@router.get("/api/analytics/mp-stats/{constituency}")
def mp_statistics(constituency: str, db: Session = Depends(get_db)):
    works = db.query(Work).filter(Work.constituency == constituency).all()
    # Returns aggregations for MP's projects ✅
```

---

### DistrictDashboard (Role: district_official)

| Component | Displays | API Endpoint | Aggregation Level |
|-----------|----------|-------------|-------------------|
| District Overview | Total projects, status breakdown | GET /api/analytics/district-stats/{state}/{district} | State + District |
| Sub-district Comparison | Stats by block/ward | GET /api/analytics/district-stats/{state}/{district} | District level detail |
| Category Utilization | Works by sector | GET /api/analytics/category-stats (filtered by district) | Sector → District |
| Financial Tracking | Fund release status | GET /fund_releases (district filtered) | FundReleaseRecord FK to works |
| Compliance Status | Compliance score | GET /compliance/summary (district filtered) | Compliance engine output |

**Backend Implementation:**
```python
@router.get("/api/analytics/district-stats/{state}/{district}")
def district_statistics(state: str, district: str, db: Session = Depends(get_db)):
    works = db.query(Work).filter(
        Work.state == state,
        Work.district == district
    ).all()
    # Full district-level aggregation ✅
```

---

### StateDashboard (Role: state_official)

| Component | Displays | API Endpoint | Aggregation |
|-----------|----------|-------------|------------|
| State Summary | Total allocation, expenditure, utilization | GET /api/analytics/state-stats/{state} | State-wide |
| District Comparison | Metrics by district | GET /api/analytics/state-stats/{state} | Districts within state |
| Sector Analysis | Work count by category | GET /api/analytics/category-stats (state filtered) | Sectors within state |
| Compliance Dashboard | Permissible category %, SC/ST allocation | GET /compliance/summary | State-level compliance |
| Trend Analysis | Historical vs Current | GET /reference/state-finance-historical + GET /dashboard/summary | Comparison |

**Backend Implementation:**
```python
@router.get("/api/analytics/state-stats/{state}")
def state_statistics_detailed(state: str, db: Session = Depends(get_db)):
    works = db.query(Work).filter(Work.state == state).all()
    # District breakdown within state ✅
    districts = {}
    for work in works:
        dist = work.district or "Unknown"
        districts[dist].append(work)
    # Returns full district comparison ✅
```

---

### MinistryDashboard (Role: ministry)

| Component | Displays | API Endpoint | Aggregation |
|-----------|----------|-------------|------------|
| National Summary | National totals, trends | GET /dashboard/summary (no filter) | Entire country |
| State Rankings | States by completion %, fund utilization | GET /api/analytics/state-stats | All states sorted |
| Category Breakdown | National sector-wise stats | GET /api/analytics/category-stats | All sectors |
| Compliance Overview | Compliance across nation | GET /compliance/summary | National aggregate |
| Historical Trends | 1993-2017 budget trends | GET /reference/yearly-finance-historical | Time series |

**Backend Implementation:**
```python
@router.get("/api/analytics/state-stats")
def state_statistics(db: Session = Depends(get_db)):
    # ALL states, no filtering → National view ✅
    return {"total_states": len(results), "states": [sorted by state]}
```

---

## SECTION 2: WORK DETAIL PAGE → API MAPPING

### WorkDetail (Route: /work/:workId)

| Section | Component | API Endpoint | Data |
|---------|-----------|-------------|------|
| **Project Info** | Title, Status, Category, Budget | GET /works/{workId} | All work fields |
| **Location** | Coordinates, Map Pin | GET /works/{workId} | latitude, longitude |
| **Financial** | Allocation, Sanctioned, Expenditure | GET /works/{workId} | allocation_amount, sanctioned_amount, expenditure_amount |
| **Timeline** | Recommended, Sanctioned, Completion dates | GET /works/{workId} | recommended_date, sanction_date, completion_date |
| **Photos** | Work progress evidence | GET /photos/{workId} | File paths, geotagged locations |
| **Grievances** | Citizen complaints | GET /grievances?work_id={workId} | grievance records with status |
| **Ratings** | Quality ratings | GET /ratings?work_id={workId} | Rating scores and comments |
| **Risk Score** | ML-calculated risk | GET /works/{workId} | risk_score, risk_level, anomaly_drivers |
| **Compliance** | Compliance check result | GET /compliance/check/{workId} | compliance_score, violations |
| **Audit Trail** | Change history | GET /audit-logs/Work/{workId} | All changes by user + timestamp |

**Data Flow for WorkDetail:**
```
Frontend: WorkDetail.jsx loads with workId param
  ↓
useEffect → fetch('/works/{workId}')
  ↓
Backend: works router
  - Query: works table by work_id
  - Returns: All work fields with ML scores
  ↓
Database: works table (35+ fields)
  ↓
Response: Complete work record ✅
  ↓
Frontend: Renders project info, then:
  - fetch('/photos/{workId}') → Gallery
  - fetch('/grievances?work_id={workId}') → Grievances
  - fetch('/ratings?work_id={workId}') → Ratings
  - fetch('/audit-logs/Work/{workId}') → Timeline
  ↓
All data real-time from database ✅
```

---

## SECTION 3: REFERENCE DATA COMPONENTS → API MAPPING

### Constituency Selector / List

| Component | Displays | API Endpoint | Data |
|-----------|----------|-------------|------|
| Constituency Dropdown | All 543 constituencies | GET /reference/constituencies | List of {name, state, reservation_status} |
| Filtered by State | Constituencies in selected state | GET /reference/constituencies?state={state} | Filtered list |
| Reservation Badge | SC/ST/OBC/General | GET /reference/constituencies | reservation_status field |
| Electors Info | 2024 electoral data | GET /reference/constituencies | electors_2024 field |

**Implementation:**
```python
@router.get("/reference/constituencies")
def list_constituencies(state: str = Query(None), ...):
    query = db.query(Constituency)
    if state:
        query = query.filter(Constituency.state == state)
    return {constituencies: [...]} ✅
```

---

### Historical Reference Data

| Component | Displays | API Endpoint | Data Source |
|-----------|----------|-------------|------------|
| Sector Breakdown | 14 categories (Drinking Water, Roads, etc.) | GET /reference/sectors | sector_reference table |
| Historical Trends | Yearly finance 1993-2017 | GET /reference/yearly-finance-historical | yearly_finance_historical table |
| State Finance Baseline | FY2016-17 by state | GET /reference/state-finance-historical | state_finance_historical table |
| State Works Baseline | 2019 work counts by state | GET /reference/state-works-historical | state_works_historical table |

**Implementation:**
```python
@router.get("/reference/yearly-finance-historical")
def get_yearly_finance_historical(db: Session = Depends(get_db)):
    results = db.query(YearlyFinanceHistorical).order_by(fiscal_year).all()
    return {data: [...]} ✅
```

---

## SECTION 4: CHART COMPONENTS DATA BINDING

### Status Distribution Chart
```javascript
Frontend: src/components/charts/StatusChart.jsx
  ↓
fetch('/dashboard/status-distribution')
  ↓
Backend: dashboard.py
  return {Sanctioned: 350, Ongoing: 100, Completed: 50, ...}
  ↓
Frontend: Render pie chart ✅ REAL DATA
```

### Risk Breakdown Chart
```javascript
Frontend: src/components/charts/RiskChart.jsx
  ↓
fetch('/dashboard/summary')
  ↓
Backend: returns risk_breakdown: {high: 10, medium: 20, low: 70}
  ↓
Frontend: Render stacked bar ✅
```

### State Comparison Chart
```javascript
Frontend: src/components/charts/StateComparison.jsx
  ↓
fetch('/api/analytics/state-stats')
  ↓
Backend: Aggregates all works by state, returns:
  [{state: "Maharashtra", total_projects: 500, ...},
   {state: "Gujarat", total_projects: 450, ...}]
  ↓
Frontend: Render state-wise comparison ✅
```

### Historical Trends Chart
```javascript
Frontend: src/components/charts/HistoricalTrends.jsx
  ↓
fetch('/reference/yearly-finance-historical')
  ↓
Backend: Returns array of yearly records
  [{fiscal_year: 1993, total_funds_released_cr: 100, ...},
   {fiscal_year: 1994, total_funds_released_cr: 120, ...}, ...]
  ↓
Frontend: Render line chart with 24-year trend ✅
```

### Map Component (GeoJSON)
```javascript
Frontend: src/components/charts/MapChart.jsx
  ↓
fetch('/reference/constituencies')
  ↓
Backend: Returns GeoJSON-ready constituency data
  (When PostGIS is ready: GET /reference/constituencies/{id}/boundary)
  ↓
Frontend: L.geoJSON() renders boundaries ✅
```

---

## SECTION 5: CRITICAL API CHARACTERISTICS

### Authentication & Authorization
All dashboard APIs require:
1. **JWT Token** in Authorization header
2. **Role-based filtering** applied automatically
3. **User context injection** from current_user dependency

**Implementation Pattern:**
```python
@router.get("/dashboard/summary")
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ← Auth gate
):
    query = db.query(Work)
    if current_user.role == UserRole.MP:
        query = query.filter(Work.constituency == current_user.constituency)  # ← Role filter
    elif current_user.role == UserRole.STATE_OFFICIAL:
        query = query.filter(Work.state == current_user.state)  # ← Role filter
    # ... return aggregated data
```

---

### Data Freshness & Caching

| Endpoint | Freshness | Caching Strategy |
|----------|-----------|------------------|
| GET /dashboard/summary | Real-time | No caching (calculated on request) |
| GET /works | Real-time | No caching |
| GET /reference/constituencies | Daily | Can cache (reference data changes rarely) |
| GET /reference/yearly-finance-historical | Annual | Can cache (historical, immutable) |
| GET /api/analytics/state-stats | Real-time | No caching (derived from live works) |

---

### Error Handling

| Scenario | Response | Code |
|----------|----------|------|
| No data for role/filter | Empty array or "No data" message | 200 OK |
| Non-existent resource | {"detail": "Not found"} | 404 |
| Unauthorized access | {"detail": "Not authenticated"} | 401 |
| Insufficient permissions | {"detail": "Forbidden"} | 403 |

---

## SECTION 6: DATA LINEAGE EXAMPLES

### Example: "500 total projects" in Ministry Dashboard

```
DB Row in works table (500 rows)
  ↓
Query: SELECT COUNT(*) FROM works
  ↓
Backend: dashboard.py → dashboard_summary()
  ↓
Response: {"total_projects": 500, ...}
  ↓
Frontend: MinistryDashboard.jsx
  ↓
Display: <StatsCard value={500} label="Total Projects" />
  ✅ Fully traceable
```

### Example: "₹250 Cr expenditure" in State Dashboard

```
DB Rows in works table (state-filtered)
  ↓
Query: SUM(expenditure_amount) WHERE state='Maharashtra'
  ↓
Backend: analytics.py → state_statistics_detailed('Maharashtra')
  ↓
Response: {"total_expenditure": 25000000000, ...}
  ↓
Frontend: StateDashboard.jsx
  ↓
Display: <FinancialCard expended={250} />
  ✅ Fully traceable, real-time
```

### Example: "14 work sectors" in Sector Chart

```
DB Rows in sector_reference table (historical 2019)
  ↓
Query: SELECT DISTINCT sector FROM sector_reference
  ↓
Backend: reference_data.py → list_sectors()
  ↓
Response: {sectors: [{sector: "Drinking Water", ...}, ...]}
  ↓
Frontend: Charts.jsx
  ↓
Display: <SectorChart data={sectors} />
  ✅ Historical reference data
```

---

## SECTION 7: NEW ENDPOINTS SUMMARY

| Endpoint | Method | Purpose | Added in Phase |
|----------|--------|---------|-----------------|
| GET /reference/constituencies | GET | List all constituencies | Phase 1 |
| GET /reference/constituencies/{id} | GET | Get constituency details | Phase 1 |
| GET /reference/sectors | GET | List work sectors | Phase 2 |
| GET /reference/state-finance-historical | GET | Historical state finance | Phase 2 |
| GET /reference/yearly-finance-historical | GET | Yearly trends 1993-2017 | Phase 2 |
| GET /reference/state-works-historical | GET | Historical state work counts | Phase 2 |
| GET /reference/states-list | GET | All states dropdown | Phase 1 |
| GET /api/analytics/state-stats | GET | All states aggregation | Phase 4 |
| GET /api/analytics/state-stats/{state} | GET | Single state detailed | Phase 4 |
| GET /api/analytics/district-stats/{state}/{district} | GET | District level stats | Phase 4 |
| GET /api/analytics/mp-stats/{constituency} | GET | MP's constituency stats | Phase 4 |
| GET /api/analytics/category-stats | GET | Sector-wise statistics | Phase 4 |

---

## SECTION 8: TESTING CHECKLIST

- [ ] Load CitizenDashboard → All stats show real database numbers
- [ ] Load MPDashboard → Shows only MP's constituency works
- [ ] Load DistrictDashboard → Shows district-level aggregation
- [ ] Load StateDashboard → Shows state + district breakdown
- [ ] Load MinistryDashboard → Shows national totals
- [ ] Click WorkDetail → All work fields + photos + grievances load
- [ ] Historical chart → Loads 24-year trend from yearly_finance_historical
- [ ] Constituency selector → All 543 constituencies appear with reservation status
- [ ] Sector breakdown → 14 sectors load from sector_reference
- [ ] No 404 or console errors on any dashboard
- [ ] JWT token required to access protected routes
- [ ] Role-based filtering works (MP sees only own constituency)
- [ ] State filter on constituency list works
- [ ] Browser DevTools → All API calls go to /api/ or /dashboard/ endpoints
- [ ] No hardcoded numbers visible in frontend source code

---

## SECTION 9: DATA COVERAGE MATRIX

✅ = Fully wired
⚠️ = Partially ready (infrastructure in place, needs frontend connection)
❌ = Not yet implemented

| Feature | Backend API | Frontend Component | Database Table | Status |
|---------|-------------|-------------------|-----------------|--------|
| **Project Summary** | GET /dashboard/summary | CitizenDashboard | works | ✅ |
| **Project CRUD** | GET/POST/PUT /works | ProjectList, WorkDetail | works | ✅ |
| **Photos/Evidence** | GET/POST /photos | PhotoGallery, PhotoUpload | photos | ✅ |
| **Grievances** | GET/POST /grievances | GrievanceList, GrievanceForm | grievances | ✅ |
| **Fund Release** | GET/POST /fund_releases | FundReleaseStatus | fund_releases | ✅ |
| **Ratings** | GET/POST /ratings | RatingCard | ratings | ✅ |
| **Compliance Check** | GET /compliance/check/{id} | ComplianceCard | (ML output) | ✅ |
| **Risk Analysis** | GET /dashboard/risk-analysis | RiskIndicator | works.risk_score | ✅ |
| **State Stats** | GET /api/analytics/state-stats | StateDashboard | works (aggregated) | ✅ |
| **District Stats** | GET /api/analytics/district-stats | DistrictDashboard | works (aggregated) | ✅ |
| **MP Stats** | GET /api/analytics/mp-stats | MPDashboard | works (aggregated) | ✅ |
| **Constituency Reference** | GET /reference/constituencies | CitySelector | constituencies | ✅ |
| **Sector Reference** | GET /reference/sectors | SectorChart | sector_reference | ✅ |
| **Historical Finance** | GET /reference/yearly-finance-historical | HistoryChart | yearly_finance_historical | ✅ |
| **Audit Trail** | GET /audit-logs | AuditTimeline | audit_logs | ✅ |
| **GIS Boundaries** | GET /reference/constituencies/boundary | MapComponent | constituency_boundaries (PostGIS) | ⚠️ |
| **MP Master** | GET /reference/mp/{id} | (Ready for future) | mp_master | ⚠️ |

---

**Document Version:** 1.0
**Status:** Complete - All Phase 1-4 endpoints documented
**Last Updated:** After Phase 4 Analytics Completion
**Next Review:** Before Phase 5 Testing
