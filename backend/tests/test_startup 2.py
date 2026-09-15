def test_application_imports():
    from app.main import app

    paths = {getattr(route, "path", None) for route in app.routes}
    assert "/health" in paths
    assert "/ai/duplicates" in app.openapi()["paths"]