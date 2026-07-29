import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SessionState:
	name: str | None = None
	history: list[dict[str, str]] = field(default_factory=list)


class ConversationMemory:
	def __init__(self):
		self._sessions: dict[str, SessionState] = {}

	def _get_state(self, session_id: str) -> SessionState:
		if session_id not in self._sessions:
			self._sessions[session_id] = SessionState()
		return self._sessions[session_id]

	def remember_turn(self, session_id: str, question: str, answer: str):
		state = self._get_state(session_id)
		state.history.append({"question": question, "answer": answer})

		# Keep memory bounded for a lightweight in-process store.
		if len(state.history) > 20:
			state.history = state.history[-20:]

	def try_store_name(self, session_id: str, text: str):
		state = self._get_state(session_id)
		normalized = text.strip()

		patterns = [
			r"(?:my name is|i am)\s+([A-Za-z][A-Za-z\s'-]{1,40})",
		]

		for pattern in patterns:
			match = re.search(pattern, normalized, flags=re.IGNORECASE)
			if match:
				state.name = match.group(1).strip(" .,!?")
				return state.name

		return None

	def get_name(self, session_id: str) -> str | None:
		return self._get_state(session_id).name

	def get_history(self, session_id: str) -> list[dict[str, Any]]:
		return list(self._get_state(session_id).history)


memory = ConversationMemory()
