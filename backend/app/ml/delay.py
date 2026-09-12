# Project delay analysis
from typing import List, Dict
from dataclasses import dataclass
from datetime import datetime


@dataclass
class DelayAnalysis:
    """Work delay analysis result."""
    work_id: str
    expected_completion: datetime
    current_date: datetime
    days_delayed: float
    delay_percentage: float
    risk_level: str  # low, medium, high, critical


class DelayPredictor:
    """Analyze and predict project delays."""
    
    @staticmethod
    def analyze_work_delay(
        work_id: str,
        recommended_date: datetime,
        expected_duration_days: int,
        progress_ratio: float,
    ) -> DelayAnalysis:
        """Analyze delay for a work based on progress."""
        current_date = datetime.utcnow()
        expected_completion = recommended_date.replace(
            day=recommended_date.day + expected_duration_days
        )
        
        # Calculate days delayed
        days_delayed = max(0, (current_date - expected_completion).days)
        delay_percentage = (days_delayed / expected_duration_days * 100) if expected_duration_days > 0 else 0
        
        # Determine risk level based on delay
        if delay_percentage < 10:
            risk_level = "low"
        elif delay_percentage < 30:
            risk_level = "medium"
        elif delay_percentage < 60:
            risk_level = "high"
        else:
            risk_level = "critical"
        
        return DelayAnalysis(
            work_id=work_id,
            expected_completion=expected_completion,
            current_date=current_date,
            days_delayed=float(days_delayed),
            delay_percentage=delay_percentage,
            risk_level=risk_level,
        )
    
    @staticmethod
    def batch_analyze_delays(works_data: List[Dict]) -> List[DelayAnalysis]:
        """Analyze delays for multiple works."""
        results = []
        for work_data in works_data:
            analysis = DelayPredictor.analyze_work_delay(
                work_id=work_data.get("work_id"),
                recommended_date=work_data.get("recommended_date"),
                expected_duration_days=work_data.get("expected_duration_days", 180),
                progress_ratio=work_data.get("progress_ratio", 0),
            )
            results.append(analysis)
        return results
