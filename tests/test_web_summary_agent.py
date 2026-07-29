import agents.web_summary_agent as agent_module


def test_web_summary_agent_success(monkeypatch):
    monkeypatch.setattr(
        agent_module.scraper,
        "scrape",
        lambda url: {
            "success": True,
            "content": "hello world",
            "title": "My Page",
            "url": url,
        },
    )
    monkeypatch.setattr(
        agent_module.gemini,
        "generate",
        lambda prompt: {"success": True, "response": "concise summary"},
    )

    result = agent_module.web_summary_agent.summarize("https://id.wikipedia.org/wiki/John_F._Kennedy", max_output_words=50)

    assert result["success"] is True
    assert result["title"] == "My Page"
    assert result["summary"] == "concise summary"


def test_web_summary_agent_propagates_scrape_failure(monkeypatch):
    monkeypatch.setattr(
        agent_module.scraper,
        "scrape",
        lambda url: {"success": False, "error": "boom"},
    )

    result = agent_module.web_summary_agent.summarize("https://id.wikipedia.org/wiki/John_F._Kennedym")

    assert result["success"] is False
    assert result["error"] == "boom"