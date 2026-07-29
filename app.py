from fastapi import FastAPI, HTTPException

from agents.email_triage_agent import email_triage_agent
from agents.support_agent import support_agent
from agents.web_summary_agent import web_summary_agent
from schemas.request import EmailTriageRequest, SupportChatRequest, WebSummaryRequest
from services.contact_tracker import contact_tracker
from utils.logger import get_logger


logger = get_logger(__name__)


app = FastAPI(
	title="Agentic Architect Challenge",
	description="web summary plus FAQ-based support agent with memory and tools.",
	version="1.0.0",
)


@app.get("/")
def root():
	logger.info("Root endpoint accessed")
	return {
		"message": "Agentic Architect Challenge API is running"
	}


@app.post("/web-summary")
def summarize_web(request: WebSummaryRequest):
	logger.info("Received web summary request for url=%s", request.url)
	result = web_summary_agent.summarize(
		str(request.url),
		max_output_words=request.max_output_words or 160,
	)

	if not result.get("success"):
		logger.error("Web summary request failed: %s", result.get("error", result))
		raise HTTPException(status_code=400, detail=result)

	logger.info("Web summary request completed for url=%s", request.url)
	return result


@app.post("/support-chat")
def support_chat(request: SupportChatRequest):
	logger.info("Received support chat request session_id=%s", request.session_id)
	result = support_agent.chat(
		session_id=request.session_id,
		question=request.question,
		context=request.context,
	)

	if not result.get("success"):
		logger.error("Support chat request failed: %s", result.get("error", result))
		raise HTTPException(status_code=400, detail=result)

	logger.info("Support chat request completed session_id=%s", request.session_id)
	return result

@app.post("/email")
def email_triage(request: EmailTriageRequest):
	contacts_last_7_days = contact_tracker.record_contact(request.customer_id)
	result = email_triage_agent.process(
		subject=request.subject,
		body=request.body,
		contacts_last_7_days=contacts_last_7_days,
	)
	result["contacts_last_7_days"] = contacts_last_7_days
	return result