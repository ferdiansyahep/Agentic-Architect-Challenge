import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RetrievalResult:
	question: str
	answer: str
	score: float
	source: str

	@property
	def context(self) -> str:
		return f"Q: {self.question}\nA: {self.answer}"


class RetrieverService:
	def __init__(self, faq_path: str = "knowledge/faq.txt", min_score: float = 0.2):
		self.faq_path = Path(faq_path)
		self.min_score = min_score
		self._stopwords = {
			"the", "and", "for", "are", "how", "what", "can", "you", "your",
			"saya", "yang", "dan", "apa", "bagaimana", "untuk", "dengan",
		}

	def _tokenize(self, text: str) -> set[str]:
		words = re.findall(r"[a-zA-Z0-9']+", text.lower())
		return {w for w in words if len(w) > 2 and w not in self._stopwords}

	def _parse_faq_pairs(self) -> list[tuple[str, str]]:
		if not self.faq_path.exists():
			return []

		content = self.faq_path.read_text(encoding="utf-8")
		lines = [line.strip() for line in content.splitlines() if line.strip()]

		pairs: list[tuple[str, str]] = []
		question = None
		for line in lines:
			if line.startswith("Q:"):
				question = line[2:].strip()
			elif line.startswith("A:") and question:
				answer = line[2:].strip()
				pairs.append((question, answer))
				question = None

		return pairs

	def get_document_content(self) -> str:
		if not self.faq_path.exists():
			return ""
		return self.faq_path.read_text(encoding="utf-8").strip()

	def search(self, question: str) -> RetrievalResult | None:
		faq_pairs = self._parse_faq_pairs()
		if not faq_pairs:
			return None

		question_tokens = self._tokenize(question)

		best_score = 0.0
		best_pair = None
		for faq_question, faq_answer in faq_pairs:
			faq_tokens = self._tokenize(faq_question)
			if not question_tokens or not faq_tokens:
				continue
			intersection = len(question_tokens & faq_tokens)
			score = intersection / len(question_tokens | faq_tokens)
			if score > best_score:
				best_score = score
				best_pair = (faq_question, faq_answer)

		if best_pair is None or best_score < self.min_score:
			return None

		return RetrievalResult(
			question=best_pair[0],
			answer=best_pair[1],
			score=round(best_score, 3),
			source=str(self.faq_path),
		)

	def get_relevant_context(self, question: str) -> str:
		result = self.search(question)
		return result.context if result else ""


retriever = RetrieverService()