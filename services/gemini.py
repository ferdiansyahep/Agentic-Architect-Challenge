from google import genai

from config import GEMINI_API_KEY, MODEL_NAME
from utils.logger import get_logger


logger = get_logger(__name__)


class GeminiService:
	def __init__(self, client=None):
		self.client = client

	@property
	def is_configured(self) -> bool:
		return bool(GEMINI_API_KEY or self.client is not None)

	def _get_client(self):
		if self.client is None:
			if not GEMINI_API_KEY:
				raise ValueError("GEMINI_API_KEY is not configured.")
			self.client = genai.Client(api_key=GEMINI_API_KEY)
		return self.client

	def generate(self, prompt: str):
		try:
			if not GEMINI_API_KEY and self.client is None:
				logger.error("GEMINI_API_KEY is not configured")
				return {
					"success": False,
					"error": "GEMINI_API_KEY is not configured.",
				}

			logger.info("Generating Gemini response with model=%s", MODEL_NAME)
			response = self._get_client().models.generate_content(
				model=MODEL_NAME,
				contents=prompt,
			)
			logger.info("Gemini response generated successfully")
			return {"success": True, "response": response.text}
		except Exception as exc:
			logger.exception("Gemini generation failed")
			return {"success": False, "error": str(exc)}


gemini = GeminiService()