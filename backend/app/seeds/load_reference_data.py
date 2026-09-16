# Data loaders for CSV files
import pandas as pd
from sqlalchemy.orm import Session
from pathlib import Path
import uuid


def load_constituencies(db: Session, csv_path: str, dry_run: bool = False):
    """Load constituency reference data from CSV"""
    from ..models.constituency import Constituency
    
    try:
        df = pd.read_csv(csv_path)
        loaded = 0
        errors = []
        
        for _, row in df.iterrows():
            try:
                # Create unique ID from state + constituency number + name
                const_id = f"{row['state'].replace(' ', '_')}_{row['constituency_no_in_state']}"
                
                existing = db.query(Constituency).filter(
                    Constituency.constituency_id == const_id
                ).first()
                
                if not existing:
                    constituency = Constituency(
                        constituency_id=const_id,
                        name=row['constituency_name'],
                        state=row['state'],
                        constituency_no_in_state=int(row['constituency_no_in_state']),
                        reservation_status=row.get('reservation_status'),
                        electors_2024=int(row.get('electors_2024', 0)) if pd.notna(row.get('electors_2024')) else None
                    )
                    if not dry_run:
                        db.add(constituency)
                    loaded += 1
            except Exception as e:
                errors.append(f"Row {row.get('constituency_name', '?')}: {str(e)}")
        
        if not dry_run and loaded > 0:
            db.commit()
        
        return {"loaded": loaded, "errors": errors, "total": len(df)}
    except Exception as e:
        return {"error": str(e), "loaded": 0}


def load_sector_reference(db: Session, csv_path: str, dry_run: bool = False):
    """Load sector reference data from CSV"""
    from ..models.reference_data import SectorReference
    
    try:
        df = pd.read_csv(csv_path)
        loaded = 0
        errors = []
        
        for _, row in df.iterrows():
            try:
                existing = db.query(SectorReference).filter(
                    SectorReference.sector == row['sector']
                ).first()
                
                if not existing:
                    sector = SectorReference(
                        sector=row['sector'],
                        total_sanctioned_cost_lakh=float(row.get('total_sanctioned_cost_lakh', 0)),
                        total_works_sanctioned=int(row.get('total_works_sanctioned', 0)),
                        historical_year=2019
                    )
                    if not dry_run:
                        db.add(sector)
                    loaded += 1
            except Exception as e:
                errors.append(f"Row {row.get('sector', '?')}: {str(e)}")
        
        if not dry_run and loaded > 0:
            db.commit()
        
        return {"loaded": loaded, "errors": errors, "total": len(df)}
    except Exception as e:
        return {"error": str(e), "loaded": 0}


def load_state_finance_historical(db: Session, csv_path: str, dry_run: bool = False):
    """Load state finance historical data from CSV"""
    from ..models.reference_data import StateFinanceHistorical
    
    try:
        df = pd.read_csv(csv_path)
        loaded = 0
        errors = []
        
        for _, row in df.iterrows():
            try:
                state = row['state_ut'].strip()
                existing = db.query(StateFinanceHistorical).filter(
                    StateFinanceHistorical.state == state
                ).first()
                
                if not existing:
                    record = StateFinanceHistorical(
                        state=state,
                        fiscal_year=2016,  # FY2016-17 baseline
                        total_funds_released_cr=float(row.get('total_funds_released_cr', 0)),
                        amount_available_with_interest_cr=float(row.get('amount_available_with_interest_cr', 0)) if pd.notna(row.get('amount_available_with_interest_cr')) else None,
                        cumulative_amount_recommended_cr=float(row.get('cumulative_amount_recommended_cr', 0)) if pd.notna(row.get('cumulative_amount_recommended_cr')) else None,
                        cumulative_amount_sanctioned_cr=float(row.get('cumulative_amount_sanctioned_cr', 0)) if pd.notna(row.get('cumulative_amount_sanctioned_cr')) else None,
                        pct_sanctioned_over_release=float(row.get('pct_sanctioned_over_release', 0)) if pd.notna(row.get('pct_sanctioned_over_release')) else None,
                        expenditure_incurred_cr=float(row.get('expenditure_incurred_cr', 0)) if pd.notna(row.get('expenditure_incurred_cr')) else None,
                        pct_utilisation_over_release=float(row.get('pct_utilisation_over_release', 0)) if pd.notna(row.get('pct_utilisation_over_release')) else None,
                        unspent_balance_cr=float(row.get('unspent_balance_cr', 0)) if pd.notna(row.get('unspent_balance_cr')) else None
                    )
                    if not dry_run:
                        db.add(record)
                    loaded += 1
            except Exception as e:
                errors.append(f"Row {row.get('state_ut', '?')}: {str(e)}")
        
        if not dry_run and loaded > 0:
            db.commit()
        
        return {"loaded": loaded, "errors": errors, "total": len(df)}
    except Exception as e:
        return {"error": str(e), "loaded": 0}


def load_yearly_finance_historical(db: Session, csv_path: str, dry_run: bool = False):
    """Load yearly finance historical data from CSV"""
    from ..models.reference_data import YearlyFinanceHistorical
    
    try:
        df = pd.read_csv(csv_path)
        loaded = 0
        errors = []
        
        for _, row in df.iterrows():
            try:
                # Parse fiscal year - handle formats like "1993-94"
                fiscal_year_str = row.get('financial_year', row.get('fiscal_year', row.get('Fiscal Year')))
                if pd.isna(fiscal_year_str):
                    continue
                    
                # Extract start year from "YYYY-YY" format
                fiscal_year = int(str(fiscal_year_str).split('-')[0])
                
                existing = db.query(YearlyFinanceHistorical).filter(
                    YearlyFinanceHistorical.fiscal_year == fiscal_year
                ).first()
                
                if not existing:
                    # Map CSV columns to model fields
                    funds_released = row.get('funds_released_cr', row.get('total_funds_released_cr', row.get('Total Fund Released (Cr)', 0)))
                    
                    record = YearlyFinanceHistorical(
                        fiscal_year=fiscal_year,
                        total_funds_released_cr=float(funds_released) if pd.notna(funds_released) else 0,
                        total_expenditure_cr=None,  # Not available in CSV
                        unspent_balance_cr=None     # Not available in CSV
                    )
                    if not dry_run:
                        db.add(record)
                    loaded += 1
            except Exception as e:
                errors.append(f"Row {row.get('financial_year', '?')}: {str(e)}")
        
        if not dry_run and loaded > 0:
            db.commit()
        
        return {"loaded": loaded, "errors": errors, "total": len(df)}
    except Exception as e:
        return {"error": str(e), "loaded": 0}


def load_state_works_historical(db: Session, csv_path: str, dry_run: bool = False):
    """Load state works historical data from CSV"""
    from ..models.reference_data import StateWorksHistorical
    
    try:
        df = pd.read_csv(csv_path)
        loaded = 0
        errors = []
        
        for _, row in df.iterrows():
            try:
                # Map CSV columns
                state = row.get('state_ut', row.get('state', '')).strip()
                if not state:
                    continue
                    
                existing = db.query(StateWorksHistorical).filter(
                    StateWorksHistorical.state == state
                ).first()
                
                if not existing:
                    # Calculate avg project cost if both values exist
                    work_count = row.get('total_works_sanctioned', row.get('work_count', row.get('total_works')))
                    total_cost = row.get('total_sanctioned_cost_lakh', 0)
                    
                    work_count_val = int(work_count) if pd.notna(work_count) else None
                    total_cost_val = float(total_cost) if pd.notna(total_cost) else None
                    
                    avg_cost = (total_cost_val / work_count_val) if (work_count_val and work_count_val > 0 and total_cost_val) else None
                    
                    record = StateWorksHistorical(
                        state=state,
                        work_count=work_count_val,
                        total_sanctioned_cost_lakh=total_cost_val,
                        avg_project_cost_lakh=avg_cost,
                        historical_year=2019
                    )
                    if not dry_run:
                        db.add(record)
                    loaded += 1
            except Exception as e:
                errors.append(f"Row {row.get('state_ut', row.get('state', '?'))}: {str(e)}")
        
        if not dry_run and loaded > 0:
            db.commit()
        
        return {"loaded": loaded, "errors": errors, "total": len(df)}
    except Exception as e:
        return {"error": str(e), "loaded": 0}
