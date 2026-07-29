from fastapi import FastAPI, HTTPException

from agents.web_summary_agent import web_summary_agent
from schemas.request import WebSummaryRequest


app = FastAPI(
	title="Agentic Architect Challenge",
	description="Part 2: scrape a website, summarize it, and apply a concise guardrail.",
	version="1.0.0",
)


@app.get("/")
def root():
	return {
		"message": "Agentic Architect Challenge API is running"
	}


@app.post("/web-summary")
def summarize_web(request: WebSummaryRequest):
	result = web_summary_agent.summarize(
		str(request.url),
		max_output_words=request.max_output_words or 160,
	)

	if not result.get("success"):
		raise HTTPException(status_code=400, detail=result)

	return result
