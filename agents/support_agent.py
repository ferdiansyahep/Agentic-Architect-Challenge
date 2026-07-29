import json
import re

from memory.memory import memory
from services.gemini import gemini
from services.retriever import retriever
from tools.calculator import calculator
from utils.logger import get_logger


logger = get_logger(__name__)

NOT_FOUND_ANSWER = (
	"I'm sorry, I don't have enough information in the provided document to "
	"answer that. Please contact a support agent."
)


class SupportAgent:
	"""A grounded Gemini agent with deterministic, testable fallbacks."""

	def _build_gemini_prompt(
		self,
		question: str,
		document: str,
		history: list[dict[str, str]],
		name: str | None,
	) -> str:
		recent_history = json.dumps(history[-6:], ensure_ascii=False)
		return f"""You are a document Q&A agent. Decide whether to call the calculator tool.

Rules:
1. Answer factual questions ONLY from DOCUMENT. Never invent facts.
2. Use action \"calculator\" only when arithmetic is required.
3. For calculator, return the arithmetic expression using digits and operators only.
4. Use action \"answer\" when DOCUMENT contains the answer.
5. Use action \"refuse\" when DOCUMENT does not contain enough information.
6. Use conversation history only to resolve follow-up references, never as a new factual source.
7. Return valid JSON only; do not use Markdown.

JSON schema:
{{"action":"calculator|answer|refuse","answer":"string","expression":"string"}}

KNOWN USER NAME: {name or 'unknown'}
RECENT HISTORY: {recent_history}
DOCUMENT:
{document}

USER QUESTION: {question}
"""

	def _parse_gemini_decision(self, response: str) -> dict:
		cleaned = response.strip()
		if cleaned.startswith("```"):
			cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.IGNORECASE)
		decision = json.loads(cleaned)
		if decision.get("action") not in {"calculator", "answer", "refuse"}:
			raise ValueError("Gemini returned an unsupported action")
		return decision

	def _chat_with_gemini(self, session_id: str, question: str, document: str):
		prompt = self._build_gemini_prompt(
			question=question,
			document=document,
			history=memory.get_history(session_id),
			name=memory.get_name(session_id),
		)
		generation = gemini.generate(prompt)
		if not generation.get("success"):
			logger.warning("Gemini routing failed; using local fallback: %s", generation.get("error"))
			return None

		try:
			return self._parse_gemini_decision(generation.get("response", ""))
		except (json.JSONDecodeError, TypeError, ValueError) as exc:
			logger.warning("Invalid Gemini routing response; using local fallback: %s", exc)
			return None

	def _extract_expression(self, question: str) -> str:
		expression = re.sub(r"[^0-9\+\-\*\/\%\(\)\s\.]", " ", question)
		return " ".join(expression.split()).strip(" .")

	def _should_use_calculator(self, question: str) -> bool:
		expression = self._extract_expression(question)
		if not expression or not re.search(r"\d", expression):
			return False
		has_operator = bool(re.search(r"[+*/%]", expression)) or bool(
			re.search(r"\d\s*-\s*\d", expression)
		)
		keywords = ("calculate", "result", "sum", "total", "hitung", "hasil", "berapa")
		return has_operator or any(word in question.lower() for word in keywords)

	def _answer_from_context(self, context: str) -> str:
		if not context:
			return NOT_FOUND_ANSWER
		for line in context.splitlines():
			if line.startswith("A:"):
				return line[2:].strip()
		return context.strip()

	def _is_follow_up(self, question: str) -> bool:
		words = set(re.findall(r"[a-z]+", question.lower()))
		return bool(words & {"that", "this", "it", "there", "tersebut", "itu"})

	def chat(self, session_id: str, question: str, context: str | None = None):
		logger.info("Support agent request session_id=%s", session_id)
		question = question.strip()

		stored_name = memory.try_store_name(session_id, question)
		if stored_name:
			answer = f"Got it. I will remember your name: {stored_name}."
			return self._remembered_response(session_id, question, answer, "memory")

		name_questions = ("what is my name", "who am i", "siapa nama saya")
		if any(phrase in question.lower() for phrase in name_questions):
			name = memory.get_name(session_id)
			answer = f"Your name is {name}." if name else (
				"I do not know your name yet. You can say: my name is ..."
			)
			return self._remembered_response(session_id, question, answer, "memory")

		document = context.strip() if context else retriever.get_document_content()
		if gemini.is_configured:
			decision = self._chat_with_gemini(session_id, question, document)
			if decision:
				action = decision["action"]
				if action == "calculator":
					expression = str(decision.get("expression", "")).strip()
					calc_result = calculator.calculate(expression)
					if calc_result.get("success"):
						answer = f"The calculation result is {calc_result['result']}."
						return self._remembered_response(
							session_id, question, answer, "calculator",
							tool_input={"expression": expression},
							decision_source="gemini",
						)
					answer = f"I could not calculate that expression: {calc_result.get('error')}"
					return self._remembered_response(
						session_id, question, answer, "calculator", decision_source="gemini",
					)
				if action == "answer" and document:
					answer = str(decision.get("answer", "")).strip() or NOT_FOUND_ANSWER
					return self._remembered_response(
						session_id, question, answer, "retriever", decision_source="gemini",
					)
				return self._remembered_response(
					session_id, question, NOT_FOUND_ANSWER, None, decision_source="gemini",
				)

		# The local router keeps Part 3 usable without credentials and is also a
		# safety fallback for unavailable or malformed model responses.
		if self._should_use_calculator(question):
			expression = self._extract_expression(question)
			calc_result = calculator.calculate(expression)
			if calc_result.get("success"):
				answer = f"The calculation result is {calc_result['result']}."
				return self._remembered_response(
					session_id, question, answer, "calculator",
					tool_input={"expression": expression},
				)
			logger.warning("Calculator failed session_id=%s: %s", session_id, calc_result.get("error"))
			answer = f"I could not calculate that expression: {calc_result.get('error', 'invalid expression')}."
			return self._remembered_response(session_id, question, answer, "calculator")

		resolved_context = context.strip() if context else retriever.get_relevant_context(question)
		if not resolved_context and self._is_follow_up(question):
			history = memory.get_history(session_id)
			if history:
				answer = history[-1]["answer"]
				return self._remembered_response(session_id, question, answer, "memory")

		answer = self._answer_from_context(resolved_context)
		return self._remembered_response(
			session_id,
			question,
			answer,
			"retriever" if resolved_context else None,
			context_used=resolved_context,
		)

	def _remembered_response(
		self,
		session_id: str,
		question: str,
		answer: str,
		used_tool: str | None,
		**metadata,
	):
		memory.remember_turn(session_id, question, answer)
		return {
			"success": True,
			"session_id": session_id,
			"answer": answer,
			"used_tool": used_tool,
			**metadata,
		}


support_agent = SupportAgent()