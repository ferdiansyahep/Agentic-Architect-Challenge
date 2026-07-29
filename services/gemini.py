from google import genai
from config import GEMINI_API_KEY, MODEL_NAME
from utils.logger import get_logger


logger = get_logger(__name__)


class GeminiService:
    def __init__(self):
        self.client = genai.Client(
            api_key=GEMINI_API_KEY
        )

    def generate(self, prompt: str):

        try:
            if not GEMINI_API_KEY:
                logger.error("GEMINI_API_KEY is not configured")
                return {
                    "success": False,
                    "error": "GEMINI_API_KEY is not configured."
                }

            logger.info("Generating Gemini response with model=%s", MODEL_NAME)
            response = self.client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            logger.info("Gemini response generated successfully")

            return {
                "success": True,
                "response": response.text
            }

        except Exception as e:
            logger.exception("Gemini generation failed")
            return {
                "success": False,
                "error": str(e)
            }


gemini = GeminiService()