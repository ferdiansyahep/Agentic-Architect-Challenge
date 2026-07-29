from types import SimpleNamespace

import services.scraper as scraper_module


def test_scrape_rejects_invalid_url():
    result = scraper_module.scraper.scrape("not-a-url")

    assert result["success"] is False
    assert "Invalid URL" in result["error"]


def test_scrape_extracts_main_content(monkeypatch):
    html = """
    <html>
      <head><title>Sample Page</title></head>
      <body>
        <script>ignore me</script>
        <main>
          <h1>Heading</h1>
          <p>First paragraph.</p>
          <li>Item one</li>
        </main>
      </body>
    </html>
    """

    class FakeResponse:
        text = html

        def raise_for_status(self):
            return None

    def fake_get(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(scraper_module.requests, "get", fake_get)

    result = scraper_module.scraper.scrape("https://example.com")

    assert result["success"] is True
    assert result["title"] == "Sample Page"
    assert "Heading" in result["content"]
    assert "First paragraph." in result["content"]
    assert "Item one" in result["content"]