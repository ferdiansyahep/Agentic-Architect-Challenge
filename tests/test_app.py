from fastapi.testclient import TestClient

import app as app_module


client = TestClient(app_module.app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "Agentic Architect Challenge API is running"


def test_web_summary_endpoint(monkeypatch):
    monkeypatch.setattr(
        app_module.web_summary_agent,
        "summarize",
        lambda url, max_output_words=160: {
            "success": True,
            "url": url,
            "title": "Sample",
            "summary": "ok",
            "source_trimmed": False,
        },
    )

    response = client.post(
        "/web-summary",
        json={"url": "https://example.com", "max_output_words": 120},
    )

    assert response.status_code == 200
    assert response.json()["summary"] == "ok"


def test_web_summary_endpoint_rejects_failure(monkeypatch):
    monkeypatch.setattr(
        app_module.web_summary_agent,
        "summarize",
        lambda url, max_output_words=160: {"success": False, "error": "bad url"},
    )

    response = client.post(
        "/web-summary",
        json={"url": "https://example.com", "max_output_words": 120},
    )

    assert response.status_code == 400
    assert response.json()["detail"]["error"] == "bad url"