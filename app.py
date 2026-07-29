from fastapi import FastAPI, HTTPException

from agents.web_summary_agent import web_summary_agent
from schemas.request import WebSummaryRequest
from utils.logger import get_logger


logger = get_logger(__name__)


app = FastAPI(
	title="Agentic Architect Challenge",
	description="Part 2: scrape a website, summarize it, and apply a concise guardrail.",
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
