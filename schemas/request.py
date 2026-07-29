from typing import Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator


class WebSummaryRequest(BaseModel):
	url: HttpUrl = Field(..., description="Website URL to scrape and summarize")
	max_output_words: Optional[int] = Field(
		default=160,
		ge=50,
		le=300,
		description="Upper bound for the summary length"
	)


class DocumentQuestionRequest(BaseModel):
	question: str = Field(..., min_length=1)
	context: Optional[str] = None


class SupportChatRequest(BaseModel):
	session_id: str = Field(..., min_length=1, max_length=100, description="Conversation session identifier")
	question: str = Field(..., min_length=1, max_length=2000, description="User question")
	context: Optional[str] = Field(default=None, max_length=12000, description="Optional explicit context override")

	@field_validator("session_id", "question")
	@classmethod
	def reject_blank_values(cls, value: str) -> str:
		value = value.strip()
		if not value:
			raise ValueError("must not be blank")
		return value
class EmailTriageRequest(BaseModel):
	subject: str = Field(default="", max_length=300)
	body: str = Field(..., min_length=1, max_length=12000)
	contacts_last_7_days: int = Field(default=0, ge=0, le=1000)

	@field_validator("body")
	@classmethod
	def reject_blank_body(cls, value: str) -> str:
		if not value.strip():
			raise ValueError("must not be blank")
		return value.strip()