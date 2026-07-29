import re
import threading
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SessionState:
	name: str | None = None
	history: list[dict[str, str]] = field(default_factory=list)
	updated_at: float = field(default_factory=time.monotonic)


class ConversationMemory:
	def __init__(self, max_turns: int = 20, ttl_seconds: int = 3600):
		self._sessions: dict[str, SessionState] = {}
		self.max_turns = max_turns
		self.ttl_seconds = ttl_seconds
		self._lock = threading.RLock()

	def _get_state(self, session_id: str) -> SessionState:
		with self._lock:
			state = self._sessions.get(session_id)
			now = time.monotonic()
			if state is None or now - state.updated_at > self.ttl_seconds:
				state = SessionState(updated_at=now)
				self._sessions[session_id] = state
			state.updated_at = now
			return state

	def remember_turn(self, session_id: str, question: str, answer: str):
		with self._lock:
			state = self._get_state(session_id)
			state.history.append({"question": question, "answer": answer})
			state.history = state.history[-self.max_turns:]

	def try_store_name(self, session_id: str, text: str):
		state = self._get_state(session_id)
		normalized = text.strip()

		patterns = [
			r"(?:my name is|nama saya)\s+([A-Za-zÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ\s'-]{0,40})",
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

	def clear(self, session_id: str) -> None:
		with self._lock:
			self._sessions.pop(session_id, None)


memory = ConversationMemory()
