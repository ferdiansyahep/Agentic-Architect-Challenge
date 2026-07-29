from google import genai
from config import GEMINI_API_KEY, MODEL_NAME


class GeminiService:
    def __init__(self):
        self.client = genai.Client(
            api_key=GEMINI_API_KEY
        )

    def generate(self, prompt: str):

        try:
            if not GEMINI_API_KEY:
                return {
                    "success": False,
                    "error": "GEMINI_API_KEY is not configured."
                }

            response = self.client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            return {
                "success": True,
                "response": response.text
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


gemini = GeminiService()