from app.data_pipeline import _amount, _category, _date, _status
from app.models.work import WorkCategory, WorkStatus


def test_pipeline_normalizes_amount_and_date():
    assert _amount("₹1,25,000") == 125000
    assert _date("2024-03-04").year == 2024


def test_pipeline_derives_category_and_status():
    assert _category("Installing drinking water hand pump") == WorkCategory.DRINKING_WATER
    assert _status("Completed") == WorkStatus.COMPLETED


def test_pipeline_rejects_missing_amount():
    assert _amount("not available") is None