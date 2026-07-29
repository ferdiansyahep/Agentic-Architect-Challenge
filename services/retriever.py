import re
from pathlib import Path


class RetrieverService:
	def __init__(self, faq_path: str = "knowledge/faq.txt"):
		self.faq_path = Path(faq_path)

	def _tokenize(self, text: str) -> set[str]:
		words = re.findall(r"[a-zA-Z0-9']+", text.lower())
		return {w for w in words if len(w) > 2}

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

	def get_relevant_context(self, question: str) -> str:
		faq_pairs = self._parse_faq_pairs()
		if not faq_pairs:
			return ""

		question_tokens = self._tokenize(question)

		best_score = -1
		best_pair = None
		for faq_question, faq_answer in faq_pairs:
			faq_tokens = self._tokenize(faq_question)
			score = len(question_tokens & faq_tokens)
			if score > best_score:
				best_score = score
				best_pair = (faq_question, faq_answer)

		if best_pair is None:
			return ""

		return f"Q: {best_pair[0]}\nA: {best_pair[1]}"


retriever = RetrieverService()
