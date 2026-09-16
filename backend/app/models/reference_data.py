# Historical and Reference data models
from sqlalchemy import Column, String, Float, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from ..database import Base


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
    data_source = Column(String(100), default='HISTORICAL_DATA')
    created_at = Column(DateTime, default=datetime.utcnow)


class SectorReference(Base):
    """Work sector/category reference data"""
    __tablename__ = "sector_reference"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sector = Column(String(100), unique=True, index=True, nullable=False)
    total_sanctioned_cost_lakh = Column(Float, nullable=True)
    total_works_sanctioned = Column(Integer, nullable=True)
    historical_year = Column(Integer, default=2019)
    data_source = Column(String(100), default='SECTOR_REFERENCE')
    created_at = Column(DateTime, default=datetime.utcnow)


class StateFinanceHistorical(Base):
    """State-wise historical finance data"""
    __tablename__ = "state_finance_historical"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    state = Column(String(100), unique=True, index=True, nullable=False)
    fiscal_year = Column(Integer, nullable=True)
    total_funds_released_cr = Column(Float)
    amount_available_with_interest_cr = Column(Float, nullable=True)
    cumulative_amount_recommended_cr = Column(Float, nullable=True)
    cumulative_amount_sanctioned_cr = Column(Float, nullable=True)
    pct_sanctioned_over_release = Column(Float, nullable=True)
    expenditure_incurred_cr = Column(Float, nullable=True)
    pct_utilisation_over_release = Column(Float, nullable=True)
    unspent_balance_cr = Column(Float, nullable=True)
    data_source = Column(String(100), default='STATE_FINANCE_HISTORICAL')
    created_at = Column(DateTime, default=datetime.utcnow)


class YearlyFinanceHistorical(Base):
    """Yearly national finance trends"""
    __tablename__ = "yearly_finance_historical"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fiscal_year = Column(Integer, unique=True, index=True, nullable=False)
    total_funds_released_cr = Column(Float)
    total_expenditure_cr = Column(Float, nullable=True)
    unspent_balance_cr = Column(Float, nullable=True)
    data_source = Column(String(100), default='YEARLY_FINANCE_HISTORICAL')
    created_at = Column(DateTime, default=datetime.utcnow)


class StateWorksHistorical(Base):
    """State-wise historical work counts and costs"""
    __tablename__ = "state_works_historical"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    state = Column(String(100), unique=True, index=True, nullable=False)
    work_count = Column(Integer, nullable=True)
    total_sanctioned_cost_lakh = Column(Float, nullable=True)
    avg_project_cost_lakh = Column(Float, nullable=True)
    historical_year = Column(Integer, default=2019)
    data_source = Column(String(100), default='STATE_WORKS_HISTORICAL')
    created_at = Column(DateTime, default=datetime.utcnow)
