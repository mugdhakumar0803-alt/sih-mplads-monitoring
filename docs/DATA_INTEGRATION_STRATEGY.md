# DATA INTEGRATION STRATEGY - Phase-by-Phase Implementation

**Status:** Ready to begin Phase 1 (Reference Data)
**Prerequisite:** FINAL_SYSTEM_AUDIT.md completed ✅

---

## PHASE 1: REFERENCE DATA INTEGRATION (Week 1)
**Goal:** Load MP master and constituency reference data to enable proper data relationships

### Step 1a: Create MP Master Table & Load Data

**Why:** Currently works.mp_name is a string; need proper foreign key relationship

**File to modify:** `backend/app/models/mp.py` (CREATE NEW)
```python
from sqlalchemy import Column, String, Integer, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from ..database import Base

class MPMaster(Base):
    """Master reference of 544 Members of Parliament (18th Lok Sabha)"""
    __tablename__ = "mp_master"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mp_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False, index=True)
    party = Column(String(100), nullable=True)
    state = Column(String(100), index=True, nullable=False)
    constituency = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    term = Column(Integer, default=18)  # Lok Sabha term number
    data_source = Column(String(100), default='MP_MASTER_18_SABHA')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**File to create:** `backend/app/seeds/load_mp_master.py`
```python
import pandas as pd
from sqlalchemy.orm import Session
from app.models.mp import MPMaster

def load_mp_master_from_csv(db: Session, csv_path: str, dry_run: bool = False):
    """Load MP master data from CSV"""
    df = pd.read_csv(csv_path)
    
    loaded = 0
    errors = []
    
    for _, row in df.iterrows():
        try:
            existing = db.query(MPMaster).filter(
                MPMaster.mp_id == row['mp_id']
            ).first()
            
            if not existing:
                mp = MPMaster(
                    mp_id=row['mp_id'],
                    name=row['name'],
                    party=row.get('party'),
                    state=row['state'],
                    constituency=row.get('constituency'),
                    email=row.get('email'),
                    phone=row.get('phone')
                )
                if not dry_run:
                    db.add(mp)
                loaded += 1
        except Exception as e:
            errors.append(f"Row {row['mp_id']}: {str(e)}")
    
    if not dry_run:
        db.commit()
    
    return {"loaded": loaded, "errors": errors}
```

**Call from main.py startup:**
```python
# In main.py @app.on_event("startup")
try:
    mp_count = db.query(MPMaster).count()
    if mp_count == 0:
        print("Loading MP master data...")
        from app.seeds.load_mp_master import load_mp_master_from_csv
        result = load_mp_master_from_csv(db, "data/raw/mp_master_18th_lok_sabha.csv")
        print(f"Loaded {result['loaded']} MPs")
except Exception as e:
    print(f"MP master load failed: {e}")
```

### Step 1b: Create Constituencies Reference Table & Load Data

**File to create:** `backend/app/models/constituency.py`
```python
from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from ..database import Base

class Constituency(Base):
    """Constituency reference with reservation status (543 constituencies)"""
    __tablename__ = "constituencies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    constituency_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False, index=True)
    state = Column(String(100), index=True, nullable=False)
    reservation_type = Column(String(50), nullable=True)  # SC, ST, OBC, General
    data_source = Column(String(100), default='CONSTITUENCY_REFERENCE')
    created_at = Column(DateTime, default=datetime.utcnow)
```

**Load from:** `constituency_reservation_status.csv` (543 rows)

### Step 1c: Update Works Model to Link to MP Master

**File to modify:** `backend/app/models/work.py`
```python
# Add this import
from sqlalchemy import ForeignKey

# Modify the Work class to add:
mp_id = Column(UUID(as_uuid=True), ForeignKey("mp_master.id"), nullable=True)

# Keep existing mp_name for backward compatibility
mp_name = Column(String(255), nullable=False)  # PRESERVED - do not remove
```

### Step 1d: Create MP Details Endpoint

**File to modify:** `backend/app/routers/works.py` OR create `backend/app/routers/reference_data.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.mp import MPMaster

router = APIRouter(prefix="/reference", tags=["Reference Data"])

@router.get("/mp/{mp_id}")
def get_mp_details(mp_id: str, db: Session = Depends(get_db)):
    """Get MP details by ID or name"""
    mp = db.query(MPMaster).filter(
        (MPMaster.mp_id == mp_id) | (MPMaster.name.ilike(f"%{mp_id}%"))
    ).first()
    
    if not mp:
        raise HTTPException(status_code=404, detail="MP not found")
    
    return {
        "id": str(mp.id),
        "mp_id": mp.mp_id,
        "name": mp.name,
        "party": mp.party,
        "state": mp.state,
        "constituency": mp.constituency,
        "email": mp.email,
        "phone": mp.phone
    }

@router.get("/mp/{mp_id}/works")
def get_mp_works(mp_id: str, db: Session = Depends(get_db)):
    """Get all works assigned to an MP"""
    mp = db.query(MPMaster).filter(MPMaster.mp_id == mp_id).first()
    if not mp:
        raise HTTPException(status_code=404, detail="MP not found")
    
    works = db.query(Work).filter(Work.mp_id == mp.id).all()
    return [{"id": w.work_id, "title": w.work_title, "status": w.status} for w in works]
```

### Step 1e: Test Phase 1 Completion

**Verification Checklist:**
- [ ] `mp_master` table created with 544 records
- [ ] `constituencies` table created with 543 records
- [ ] `works.mp_id` foreign key added
- [ ] GET /reference/mp/{mp_id} returns correct data
- [ ] MP Dashboard still loads (regression test)
- [ ] No errors in backend logs during startup

**Expected Outcome:** MP data now searchable and linked to works; foundation for analytics

---

## PHASE 2: HISTORICAL DATA INTEGRATION (Week 2)
**Goal:** Load historical datasets to enable "2019 vs Now" comparisons

### Step 2a: Create Historical Works Table

**File to create:** `backend/app/models/work_historical.py`
```python
from sqlalchemy import Column, String, Float, DateTime, Integer, Enum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from ..database import Base
from .work import WorkStatus, WorkCategory

class WorkHistorical(Base):
    """Historical MPLADS works (2019 and earlier years)"""
    __tablename__ = "works_historical"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    work_id = Column(String(50), index=True)
    mp_name = Column(String(255))
    state = Column(String(100), index=True)
    constituency = Column(String(255))
    category = Column(String(100))
    status = Column(String(50), default='Completed')
    allocation_amount = Column(Float)
    expenditure_amount = Column(Float)
    historical_year = Column(Integer)  # 2019, 2018, etc.
    data_source = Column(String(100), default='HISTORICAL_2019')
    created_at = Column(DateTime, default=datetime.utcnow)
```

### Step 2b: Load Historical Datasets

**Files to load:**
1. `historical_mplads_sector_works.csv` → reference table
2. `historical_mplads_state_works.csv` → `works_historical`
3. `historical_mplads_state_finance.csv` → separate analytics table
4. `historical_mplads_yearly_finance.csv` → separate analytics table

**Loader function:** `backend/app/seeds/load_historical_data.py`
```python
import pandas as pd
from sqlalchemy.orm import Session
from app.models.work_historical import WorkHistorical

def load_historical_works(db: Session, csv_path: str, year: int):
    """Load historical works data"""
    df = pd.read_csv(csv_path)
    
    for _, row in df.iterrows():
        work = WorkHistorical(
            work_id=row.get('work_id', f"HIST_{year}_{uuid.uuid4()}"),
            mp_name=row['mp_name'],
            state=row['state'],
            constituency=row.get('constituency', ''),
            category=row.get('category', 'Other'),
            allocation_amount=float(row.get('allocation_amount', 0)),
            expenditure_amount=float(row.get('expenditure_amount', 0)),
            historical_year=year,
            data_source=f'HISTORICAL_{year}'
        )
        db.add(work)
    
    db.commit()
    return {"loaded": len(df)}
```

### Step 2c: Create Historical Analytics API

**File to modify:** `backend/app/routers/analytics.py`

```python
@router.get("/historical/comparison")
def historical_comparison(state: str = None, year_from: int = 2019, year_to: int = 2024):
    """Compare metrics between historical year and current"""
    
    # Query historical
    hist = db.query(WorkHistorical).filter(
        WorkHistorical.historical_year == year_from
    )
    if state:
        hist = hist.filter(WorkHistorical.state == state)
    hist_data = hist.all()
    
    # Query current
    current = db.query(Work)
    if state:
        current = current.filter(Work.state == state)
    current_data = current.all()
    
    return {
        "historical_year": year_from,
        "historical_count": len(hist_data),
        "historical_allocation": sum(w.allocation_amount for w in hist_data),
        "current_year": year_to,
        "current_count": len(current_data),
        "current_allocation": sum(w.allocation_amount for w in current_data),
        "growth_percentage": calculate_growth(hist_data, current_data)
    }
```

### Step 2d: Test Phase 2 Completion

**Verification Checklist:**
- [ ] `works_historical` table created with records
- [ ] Historical CSVs loaded (verify row counts match)
- [ ] GET /analytics/historical/comparison returns correct data
- [ ] Frontend can fetch historical data via new API
- [ ] No data loss from current works table
- [ ] Data source field correctly set to 'HISTORICAL_2019'

---

## PHASE 3: GIS/MAP DATA INTEGRATION (Week 2)
**Goal:** Load constituency boundaries for map visualization

### Step 3a: Create PostGIS Table for Boundaries

**File to create:** `backend/app/models/constituency_boundary.py`
```python
from geoalchemy2 import Geometry
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from ..database import Base

class ConstituencyBoundary(Base):
    """GIS: Constituency boundaries (2019) from DataMeet"""
    __tablename__ = "constituency_boundaries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    constituency_id = Column(String(50), unique=True, index=True)
    name = Column(String(255), nullable=False)
    state = Column(String(100), index=True)
    
    # PostGIS geometry column
    geometry = Column(Geometry(geometry_type='MULTIPOLYGON', srid=4326))
    
    data_source = Column(String(100), default='DATAMEET_2019')
    created_at = Column(DateTime, default=datetime.utcnow)
```

### Step 3b: Load GIS Data from GeoJSON

**Implementation approach:**
1. Download DataMeet 2019 parliamentary constituencies GeoJSON
2. Parse and insert into PostGIS table
3. Create geospatial queries

**File to create:** `backend/app/seeds/load_gis_data.py`
```python
import json
from geoalchemy2 import shape
from sqlalchemy.orm import Session

def load_constituency_boundaries(db: Session, geojson_path: str):
    """Load constituency boundaries from GeoJSON"""
    with open(geojson_path) as f:
        geojson = json.load(f)
    
    for feature in geojson['features']:
        props = feature['properties']
        geom = shape.from_shape(feature['geometry'])
        
        boundary = ConstituencyBoundary(
            constituency_id=props.get('ac_id', props.get('id')),
            name=props.get('ac_name', props.get('name')),
            state=props.get('state'),
            geometry=geom
        )
        db.add(boundary)
    
    db.commit()
```

### Step 3c: Create GIS Endpoints

**File to modify:** `backend/app/routers/reference_data.py`

```python
@router.get("/constituencies/{id}/boundary", response_model=dict)
def get_constituency_boundary(id: str, db: Session = Depends(get_db)):
    """Get constituency boundary as GeoJSON"""
    boundary = db.query(ConstituencyBoundary).filter(
        ConstituencyBoundary.constituency_id == id
    ).first()
    
    if not boundary:
        raise HTTPException(status_code=404, detail="Boundary not found")
    
    # Return as GeoJSON
    return {
        "type": "Feature",
        "properties": {
            "id": boundary.constituency_id,
            "name": boundary.name,
            "state": boundary.state
        },
        "geometry": json.loads(db.scalar(
            func.ST_AsGeoJSON(boundary.geometry)
        ))
    }

@router.get("/constituencies/within/{state}")
def get_state_constituencies(state: str, db: Session = Depends(get_db)):
    """Get all constituencies in a state (for map rendering)"""
    boundaries = db.query(ConstituencyBoundary).filter(
        ConstituencyBoundary.state == state
    ).all()
    
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"id": b.constituency_id, "name": b.name},
                "geometry": json.loads(db.scalar(func.ST_AsGeoJSON(b.geometry)))
            }
            for b in boundaries
        ]
    }
```

### Step 3d: Connect Frontend Maps

**File to modify:** `frontend/src/components/charts/MapChart.jsx` OR create new component

```javascript
useEffect(() => {
    async function fetchBoundaries() {
        const response = await fetch(`/api/reference/constituencies/within/${state}`);
        const geojson = await response.json();
        setGeoData(geojson);
        
        // Add to Leaflet map
        L.geoJSON(geojson, {style: {...}}).addTo(map);
    }
    fetchBoundaries();
}, [state, map]);
```

---

## PHASE 4: ANALYTICS COMPLETION (Week 3)
**Goal:** Complete state/district/mp-level aggregation endpoints

### Step 4a: Audit Current Dashboard APIs

**Action:** Read `backend/app/routers/dashboard.py` to find incomplete endpoints

**Expected format for state stats:**
```python
@router.get("/dashboard/state-stats")
def state_statistics(db: Session = Depends(get_db)):
    """Get stats aggregated by state"""
    states = db.query(Work.state).distinct()
    results = []
    
    for state_name in states:
        works = db.query(Work).filter(Work.state == state_name).all()
        results.append({
            "state": state_name,
            "total_projects": len(works),
            "sanctioned": sum(1 for w in works if w.status == WorkStatus.SANCTIONED),
            "completed": sum(1 for w in works if w.status == WorkStatus.COMPLETED),
            "total_allocation": sum(w.allocation_amount for w in works),
            "total_expenditure": sum(w.expenditure_amount or 0 for w in works)
        })
    
    return {"states": results}
```

### Step 4b: Create District-Level APIs

```python
@router.get("/dashboard/district-stats/{state}")
def district_statistics(state: str, db: Session = Depends(get_db)):
    """Get stats by district within a state"""
    # Similar pattern to state_stats but grouped by district
```

### Step 4c: Create MP-Level APIs

```python
@router.get("/dashboard/mp-stats/{constituency}")
def mp_statistics(constituency: str, db: Session = Depends(get_db)):
    """Get stats for an MP's constituency"""
    # Aggregated by MP through constituency filter
```

---

## PHASE 5: COMPREHENSIVE TESTING (Week 4)
**Goal:** Verify all features work without regressions

### Test Matrix

| Test Case | Expected Result | Status |
|-----------|-----------------|--------|
| Load landing page | Display without errors | TBD |
| Login as citizen | Access citizen dashboard | TBD |
| View citizen dashboard | See real aggregated data | TBD |
| View MP dashboard | See MP's works only | TBD |
| View district dashboard | See district-level stats | TBD |
| View state dashboard | See state-level stats | TBD |
| View ministry dashboard | See national stats | TBD |
| Click work detail | Show full project + photos + grievances | TBD |
| Check compliance status | Show real compliance score | TBD |
| View historical comparison | Show 2019 vs current | TBD |
| View map | Render constituency boundaries | TBD |
| Search MP | Find by name, email, phone | TBD |

### Regression Test Suite

Run through all existing features:
- Authentication flow
- CRUD operations on works
- Grievance submission
- Photo upload
- Fund release tracking
- Rating system
- Audit log recording

---

## SUCCESS CRITERIA (53-Point Acceptance)

By end of Phase 5, verify:

1. **Data Integration** (15 items)
   - [ ] All 9 datasets loaded without breaking existing code
   - [ ] Data source field populated for all historical records
   - [ ] No hardcoded numbers in frontend dashboards
   - [ ] All dashboard metrics traceable to database

2. **API Completeness** (12 items)
   - [ ] State-level stats API returning correct aggregations
   - [ ] District-level stats API working
   - [ ] MP-level stats API working
   - [ ] Historical comparison API working
   - [ ] Boundary GeoJSON endpoints responding

3. **Frontend Integration** (12 items)
   - [ ] All 5 dashboards loading real data
   - [ ] No console errors in browser
   - [ ] Charts rendering with correct data
   - [ ] Maps showing constituency boundaries

4. **Database** (8 items)
   - [ ] Schema extensions applied without breaking existing
   - [ ] Foreign keys properly indexed
   - [ ] Query performance acceptable
   - [ ] Data integrity maintained

5. **Documentation** (6 items)
   - [ ] FINAL_SYSTEM_AUDIT.md created
   - [ ] FRONTEND_BACKEND_DATA_MATRIX.md created
   - [ ] DASHBOARD_DATA_COVERAGE.md created
   - [ ] DATA_LINEAGE.md updated
   - [ ] DATASET_INVENTORY.md updated
   - [ ] Migration scripts documented

---

## IMPLEMENTATION GUARDRAILS

**DO NOT:**
- ❌ Remove any existing tables or fields
- ❌ Change API response field names (extend, don't rename)
- ❌ Delete seed data or test records
- ❌ Hardcode any numbers in frontend
- ❌ Break authentication or authorization flow

**DO:**
- ✅ Add new fields to existing models
- ✅ Create new tables for historical/reference data
- ✅ Test after every change
- ✅ Run full application before committing
- ✅ Document all data lineage

---

## TIMELINE & MILESTONES

| Week | Phase | Deliverables |
|------|-------|--------------|
| Week 1 | Phase 1 | MP master + constituency reference tables loaded |
| Week 2 | Phases 2 & 3 | Historical datasets + GIS boundaries loaded |
| Week 3 | Phase 4 | Analytics APIs completed |
| Week 4 | Phase 5 | Full testing + UAT complete |
| Week 5 | Documentation | Final audit report + deployment ready |

---

**Document Version:** 1.0
**Status:** Ready for Phase 1 Kickoff
**Next Action:** Begin Step 1a (Create MP Master Table)
