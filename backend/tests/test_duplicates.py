from types import SimpleNamespace

from app.ml.duplicates import find_duplicate_clusters


def test_nearby_matching_works_are_detected():
    works = [
        SimpleNamespace(work_id="A", description="Construction of rural road and bridge", latitude=28.0, longitude=77.0),
        SimpleNamespace(work_id="B", description="Construction of rural road and bridge", latitude=28.001, longitude=77.001),
    ]
    result = find_duplicate_clusters(works)
    assert len(result) == 1
    assert result[0].work_id_a == "A"


def test_distant_works_are_not_duplicates():
    works = [
        SimpleNamespace(work_id="A", description="Construction of rural road", latitude=28.0, longitude=77.0),
        SimpleNamespace(work_id="B", description="Construction of rural road", latitude=29.0, longitude=78.0),
    ]
    assert find_duplicate_clusters(works) == []