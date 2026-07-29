import threading
import time
from collections import defaultdict, deque


class ContactTracker:
	def __init__(self, window_seconds: int = 7 * 24 * 60 * 60, clock=time.time):
		self.window_seconds = window_seconds
		self._clock = clock
		self._contacts: dict[str, deque[float]] = defaultdict(deque)
		self._lock = threading.RLock()

	def record_contact(self, customer_id: str) -> int:
		now = self._clock()
		cutoff = now - self.window_seconds
		with self._lock:
			contacts = self._contacts[customer_id]
			while contacts and contacts[0] < cutoff:
				contacts.popleft()
			contacts.append(now)
			return len(contacts)

	def clear(self) -> None:
		with self._lock:
			self._contacts.clear()


contact_tracker = ContactTracker()