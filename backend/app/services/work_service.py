# Business logic for MPLADS works
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..models.work import Work, WorkStatus
from ..models.user import User, UserRole
from ..ml.anomaly import score_works, WorkFeatures
from ..ml.risk_engine import RiskEngine
from ..ml.duplicates import find_duplicate_clusters, WorkInput
from ..ml.compliance_engine import validate_work_category
from ..ml.force_majeure import load_calamity_data, check_force_majeure

_risk_engine = RiskEngine()
_calamity_df = None  # lazy-loaded once, not on every request


def _get_calamity_data():
    global _calamity_df
    if _calamity_df is None:
        _calamity_df = load_calamity_data()
    return _calamity_df


class WorkService:
    """Service for work-related operations."""

    @staticmethod
    def get_all_works(
        db: Session,
        state: Optional[str] = None,
        status: Optional[WorkStatus] = None,
        current_user: Optional[User] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Work]:
        """Get works with optional filtering."""
        query = db.query(Work)
        if state:
            query = query.filter(Work.state == state)
        if status:
            query = query.filter(Work.status == status)
        if current_user and current_user.role == UserRole.MP:
            if current_user.constituency:
                query = query.filter(Work.constituency == current_user.constituency)
            else:
                query = query.filter(Work.mp_name == current_user.username)
        elif current_user and current_user.role == UserRole.STATE_OFFICIAL and current_user.state:
            query = query.filter(Work.state == current_user.state)
        elif current_user and current_user.role == UserRole.DISTRICT_OFFICIAL and current_user.district_id:
            query = query.filter(Work.district == current_user.district_id)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_work_by_id(db: Session, work_id: str) -> Optional[Work]:
        """Get a single work by ID."""
        return db.query(Work).filter(Work.work_id == work_id).first()

    @staticmethod
    def create_work(db: Session, work_data: dict) -> Work:
        """Create a new work record."""
        new_work = Work(**work_data)
        db.add(new_work)
        db.commit()
        db.refresh(new_work)
        return new_work

    @staticmethod
    def update_work(db: Session, work_id: str, updates: dict) -> Optional[Work]:
        """Update an existing work record."""
        work = db.query(Work).filter(Work.work_id == work_id).first()
        if work:
            for key, value in updates.items():
                setattr(work, key, value)
            db.commit()
            db.refresh(work)
        return work

    @staticmethod
    def calculate_risk_scores(db: Session, works: List[Work]) -> List[dict]:
        """
        Now combines FIVE signals through risk_engine.py, instead of just
        the anomaly model alone:
          - cost_risk, delay_risk  <- derived from the same features used for anomaly.py
          - duplicate_risk          <- from the adapted duplicates.py
          - grievance_risk          <- from citizen_grievance_count
          - compliance_risk         <- from the category validator

        force_majeure is applied BEFORE delay_risk is computed, so a
        calamity-excused delay never counts against the work at all.
        """
        if not works:
            return []

        calamity_df = _get_calamity_data()

        # --- peer medians for cost_ratio, same as before ---
        peer_allocations: dict[tuple[str, str], list[float]] = {}
        for peer in db.query(Work).all():
            category = getattr(peer.category, "value", peer.category)
            peer_allocations.setdefault((peer.state, category), []).append(peer.allocation_amount or 0.0)

        # --- duplicate detection, run once across all works ---
        work_inputs = [
            WorkInput(
                work_id=w.work_id,
                work_title=w.work_title,
                category=getattr(w.category, "value", w.category),
                constituency=w.constituency,
            )
            for w in works
        ]
        duplicate_pairs = find_duplicate_clusters(work_inputs)
        duplicate_scores: dict[str, float] = {}
        for pair in duplicate_pairs:
            duplicate_scores[pair.work_id_a] = max(duplicate_scores.get(pair.work_id_a, 0.0), pair.similarity)
            duplicate_scores[pair.work_id_b] = max(duplicate_scores.get(pair.work_id_b, 0.0), pair.similarity)

        results = []
        for w in works:
            category = getattr(w.category, "value", w.category)
            peers = peer_allocations.get((w.state, category), [w.allocation_amount or 1.0])
            median_cost = sorted(peers)[len(peers) // 2]
            cost_ratio = (w.allocation_amount or 0.0) / max(median_cost, 1.0)

            status_value = getattr(w.status, "value", w.status)
            progress_ratio = 1.0 if status_value == "Completed" else 0.5

            # --- force-majeure check before counting delay against this work ---
            fm_check = check_force_majeure(w.mp_name, datetime.utcnow(), calamity_df)
            if fm_check.is_excused:
                delay_risk = 0.0  # genuinely excused — do not penalize
            else:
                delay_risk = max(0.0, 1.0 - progress_ratio)

            cost_risk = min(1.0, max(0.0, (cost_ratio - 1.0) / 2.0))  # 1x median=0 risk, 3x median=1.0 risk
            duplicate_risk = duplicate_scores.get(w.work_id, 0.0)
            grievance_risk = min(1.0, (w.citizen_grievance_count or 0) / 5.0)

            category_check = validate_work_category(w.work_title)
            compliance_risk = 1.0 if not category_check.is_permissible else 0.0

            risk_result = _risk_engine.calculate(
                cost_risk=cost_risk,
                delay_risk=delay_risk,
                duplicate_risk=duplicate_risk,
                grievance_risk=grievance_risk,
                compliance_risk=compliance_risk,
            )

            drivers = list(risk_result.drivers)
            if fm_check.is_excused:
                drivers.append(f"Delay excused: {fm_check.reason}")
            if not category_check.is_permissible:
                drivers.append(category_check.reason)

            results.append({
                "work_id": w.work_id,
                "risk_score": risk_result.score,
                "risk_level": risk_result.level,
                "top_drivers": drivers,
            })

        return results