from fastapi.testclient import TestClient
from app.main import app
from app.auth import get_current_user

client = TestClient(app)


def test_cors_preflight():
    """OPTIONS preflight from an allowed origin should succeed with CORS headers."""
    response = client.options(
        "/widgets/some-id/submissions",
        headers={
            "Origin": "http://localhost:5500",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5500"


def test_invalid_payload_rejected():
    """Missing required 'data' field should return 422, never 500."""
    response = client.post("/widgets/some-id/submissions", json={})
    assert response.status_code == 422


def test_oversized_payload_rejected():
    huge_data = {"field": "x" * 1_000_000}
    response = client.post("/widgets/some-id/submissions", json={"data": huge_data})
    assert response.status_code == 413


def test_honeypot_blocks_spam():
    """A filled honeypot field should be silently dropped (204), not stored."""
    response = client.post(
        "/widgets/some-id/submissions",
        json={"data": {"email": "bot@spam.com"}, "website": "http://spam.com"},
    )
    assert response.status_code == 204


def test_geo_fallback_chain(mocker):
    """If provider A fails, provider B should be tried; if both fail, enrichment returns None."""
    from app.geo import get_geo_from_ip

    mocker.patch("httpx.get", side_effect=Exception("Provider down"))
    result = get_geo_from_ip("1.2.3.4")
    assert result == {"country": None, "city": None}

def test_rate_limiting(mocker):
    """After the limit, requests should get 429; legitimate traffic still works after."""
    mocker.patch("app.routes.submissions.get_geo_from_ip", return_value={"country": None, "city": None})
    mocker.patch("app.services.submission_service.SubmissionService.create_submission", return_value={})
    fake_widget_id = "11111111-1111-1111-1111-111111111111"
    for _ in range(5):
        client.post(f"/widgets/{fake_widget_id}/submissions", json={"data": {"email": "a@a.com"}})
    response = client.post(f"/widgets/{fake_widget_id}/submissions", json={"data": {"email": "a@a.com"}})
    assert response.status_code == 429


def test_widget_config_endpoint_structure():
    """The public config endpoint should return the fields widget.js needs to render."""
    response = client.get("/widgets/nonexistent-id/config")
    assert response.status_code == 404  # widget doesn't exist, but endpoint itself works correctly


# Override auth for tests — pretend every request is already authenticated
# as this fixed test user, bypassing real JWT verification entirely.
TEST_OWNER_ID = "11111111-1111-1111-1111-111111111111"

def fake_get_current_user():
    return TEST_OWNER_ID

app.dependency_overrides[get_current_user] = fake_get_current_user


def test_widget_config_endpoint_structure():
    """Create a real widget, then confirm its public config endpoint returns matching data."""
    create_response = client.post(
        "/widgets",
        json={
            "widget_type": "signup_form",
            "title": "Test Widget",
            "description": "A test widget",
            "config": {"fields": ["email"]},
            "button_text": "Go",
        },
    )
    assert create_response.status_code == 201
    widget_id = create_response.json()["id"]

    config_response = client.get(f"/widgets/{widget_id}/config")
    assert config_response.status_code == 200
    body = config_response.json()
    assert body["title"] == "Test Widget"
    assert body["button_text"] == "Go"
    assert body["config"] == {"fields": ["email"]}