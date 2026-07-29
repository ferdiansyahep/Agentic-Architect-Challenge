from dataclasses import dataclass

from utils.logger import get_logger


logger = get_logger(__name__)


@dataclass
class SummaryGuardrail:
	max_input_chars: int = 12000
	max_output_words: int = 160

	def trim_source(self, content):
		normalized = " ".join(content.split())
		if len(normalized) <= self.max_input_chars:
			return normalized, False

		trimmed = normalized[: self.max_input_chars].rsplit(" ", 1)[0]
		logger.warning("Source content trimmed from %d to %d characters", len(normalized), len(trimmed))
		return trimmed, True

	def build_prompt(self, *, title, url, content):
		trimmed_content, was_trimmed = self.trim_source(content)

		return {
			"prompt": (
				"You are a web summarization assistant. "
				"Summarize the source in a concise, factual, and professional tone. "
				"Do not invent details. If the page is long, prioritize the most important points. "
				f"Keep the response under {self.max_output_words} words.\n\n"
				f"Title: {title or 'Untitled page'}\n"
				f"URL: {url}\n"
				f"Source trimmed: {'yes' if was_trimmed else 'no'}\n\n"
				f"Source content:\n{trimmed_content}"
			),
			"was_trimmed": was_trimmed,
		}

	def validate_summary(self, summary):
		words = summary.split()
		if len(words) <= self.max_output_words:
			return summary

		logger.warning("Summary truncated from %d to %d words", len(words), self.max_output_words)
		return " ".join(words[: self.max_output_words]).rstrip() + "..."


guardrails = SummaryGuardrail()
