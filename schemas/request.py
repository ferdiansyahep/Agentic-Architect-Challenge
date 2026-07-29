from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


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
	session_id: str = Field(..., min_length=1, description="Conversation session identifier")
	question: str = Field(..., min_length=1, description="User question")
	context: Optional[str] = Field(default=None, description="Optional explicit context override")
