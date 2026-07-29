from services.gemini import gemini
from services.scraper import scraper
from tools.guardrails import guardrails


class WebSummaryAgent:

	def summarize(self, url, max_output_words=160):

		scrape_result = scraper.scrape(url)

		if not scrape_result.get("success"):
			return scrape_result

		original_max_words = guardrails.max_output_words
		guardrails.max_output_words = max_output_words

		try:
			prompt_pack = guardrails.build_prompt(
				title=scrape_result.get("title", ""),
				url=scrape_result.get("url", url),
				content=scrape_result.get("content", "")
			)

			summary_result = gemini.generate(prompt_pack["prompt"])

			if not summary_result.get("success"):
				return summary_result

			summary = guardrails.validate_summary(summary_result.get("response", ""))

			return {
				"success": True,
				"url": scrape_result.get("url", url),
				"title": scrape_result.get("title", ""),
				"summary": summary,
				"source_trimmed": prompt_pack["was_trimmed"],
			}
		finally:
			guardrails.max_output_words = original_max_words


web_summary_agent = WebSummaryAgent()
