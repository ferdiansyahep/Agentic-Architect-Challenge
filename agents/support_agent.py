import re

from memory.memory import memory
from services.retriever import retriever
from tools.calculator import calculator
from utils.logger import get_logger


logger = get_logger(__name__)


class SupportAgent:
	def _should_use_calculator(self, question: str) -> bool:
		has_math_keyword = any(
			keyword in question.lower()
			for keyword in ["calculate", "what is", "result", "sum", "total"]
		)
		has_math_symbols = bool(re.search(r"[0-9][0-9\s\+\-\*\/\%\(\)\.]*", question))
		return has_math_keyword and has_math_symbols

	def _extract_expression(self, question: str) -> str:
		expression = re.sub(r"[^0-9\+\-\*\/\%\(\)\s\.]", " ", question)
		return " ".join(expression.split())

	def _answer_from_context(self, question: str, context: str) -> str:
		if not context:
			return (
				"I'm sorry, I couldn't find an answer in the available document. "
				"Please share more details or update the source document."
			)

		for line in context.splitlines():
			if line.startswith("A:"):
				return line[2:].strip()

		return context.strip()

	def chat(self, session_id: str, question: str, context: str | None = None):
		logger.info("Support agent request session_id=%s question=%s", session_id, question)

		stored_name = memory.try_store_name(session_id, question)
		if stored_name:
			answer = f"Got it. I will remember your name: {stored_name}."
			memory.remember_turn(session_id, question, answer)
			return {
				"success": True,
				"session_id": session_id,
				"answer": answer,
				"used_tool": "memory",
			}

		if "what is my name" in question.lower() or "who am i" in question.lower():
			name = memory.get_name(session_id)
			if name:
				answer = f"Your name is {name}."
			else:
				answer = "I do not know your name yet. You can say: my name is ..."

			memory.remember_turn(session_id, question, answer)
			return {
				"success": True,
				"session_id": session_id,
				"answer": answer,
				"used_tool": "memory",
			}

		if self._should_use_calculator(question):
			expression = self._extract_expression(question)
			calc_result = calculator.calculate(expression)

			if calc_result.get("success"):
				answer = f"The calculation result is {calc_result['result']}."
				memory.remember_turn(session_id, question, answer)
				return {
					"success": True,
					"session_id": session_id,
					"answer": answer,
					"used_tool": "calculator",
				}

			logger.warning("Calculator tool failed session_id=%s error=%s", session_id, calc_result.get("error"))

		resolved_context = context or retriever.get_relevant_context(question)
		answer = self._answer_from_context(question, resolved_context)

		memory.remember_turn(session_id, question, answer)

		return {
			"success": True,
			"session_id": session_id,
			"answer": answer,
			"used_tool": "retriever",
			"context_used": resolved_context,
		}


support_agent = SupportAgent()
