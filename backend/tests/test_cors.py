from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def ask_permission(origin):
    """What a browser does before a cross-house request: 'am I allowed in?'"""
    return client.options(
        "/ask",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )


def test_allows_the_react_dev_page():
    response = ask_permission("http://localhost:5173")
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_blocks_unknown_websites():
    response = ask_permission("http://evil.example.com")
    assert "access-control-allow-origin" not in response.headers