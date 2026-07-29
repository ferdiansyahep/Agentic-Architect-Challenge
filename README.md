# Agentic Architect Challenge

This project is a FastAPI-based agentic application that combines several customer-support workflows into one API service.

## What it does

The app provides three main capabilities:

- Web summarization: scrape a webpage and generate a concise summary
- Support chat: answer support questions using a grounded FAQ-style knowledge base
- Email triage: classify incoming customer emails and generate a draft response when possible

## Main features

- FastAPI-based REST API
- Session-based support chat with memory
- Optional Gemini integration for smarter routing and drafting
- Deterministic fallback behavior when AI services are unavailable
- Contact tracking for email escalation handling

## Project structure

- app.py: FastAPI application entry point
- agents/: agent implementations for support, web summary, and email triage
- services/: integrations for Gemini, scraping, retrieval, and contact tracking
- tools/: helper tools such as calculator and guardrails
- schemas/: request models for API payloads
- tests/: unit tests for the app and its agents

## Requirements

- Python 3.10+
- Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment variables

Create a `.env` file in the project root with:

```env
GEMINI_API_KEY=your_api_key_here
MODEL_NAME=gemini-2.5-flash
```

The `MODEL_NAME` variable is optional and defaults to `gemini-2.5-flash`.

## Run the application

Start the server locally with:

```bash
uvicorn app:app --reload
```

Then open the API docs at:

- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/redoc

## API endpoints

### Health check

- GET `/`

### Web summary

- POST `/web-summary`

Example body:

```json
{
  "url": "https://example.com",
  "max_output_words": 160
}
```

### Support chat

- POST `/support-chat`

Example body:

```json
{
  "session_id": "user-1",
  "question": "How do I reset my password?"
}
```

### Email triage

- POST `/email`

Example body:

```json
{
  "customer_id": "customer@example.com",
  "subject": "I need help with billing",
  "body": "I was charged twice for my subscription."
}
```

## Testing

Run the test suite with:

```bash
pytest
```
# Architecture Overview


## Architecture Part 1 — Email Triage

Email request → Validate request → Classify category → Check critical keywords and seven-day contact frequency → **Critical: yes** → Route to human support → **Critical: no** → Retrieve relevant FAQ context → Gemini classification and grounded drafting → Deterministic fallback when Gemini is unavailable → Return automated draft

## Architecture Part 2 — Web Summarization

URL request → Validate URL → Fetch and parse webpage → Remove scripts, styles, and boilerplate → Normalize and limit source content → Build guarded summarization prompt → Gemini summary → Validate maximum output length → Return title, source URL, summary, and trimming status

## Architecture Part 3 — Support Agent

User question → Validate request → Load session memory and FAQ document → Gemini selects `calculator`, `answer`, or `refuse` → Optional calculator tool → Ground answer in FAQ content → Deterministic local router when Gemini is unavailable or malformed → Save latest conversation turn → Return answer and tool metadata

| Part | Trade-off | Pros and Cons | Potential Failure |
| --- | --- | --- | --- |
| 1 | A safety-first hybrid router applies deterministic escalation rules before AI classification and drafting. | **Pros:** Critical incidents and frequent contacts are reliably routed to a person. Drafts are grounded in retrieved FAQ content, and a deterministic fallback keeps the flow available without Gemini. **Cons:** Keyword rules can miss unusual phrasing or flag benign messages. Retrieval thresholds may reject relevant questions. | A critical issue expressed without a known phrase may not be escalated. Missing FAQ context routes the request to a human. An unavailable or malformed Gemini response reduces classification quality but does not stop the fallback draft. |
| 2 | The system cleans and trims webpage text before sending it to Gemini instead of forwarding the complete page. | **Pros:** Reduces HTML noise, prompt size, and irrelevant content. Guardrails constrain input and output length. **Cons:** Cleaning can remove meaningful structure; trimming can omit relevant details from long pages. | Invalid, private, or unreachable URLs are rejected. Pages that require JavaScript may yield little content. Network or Gemini failures return an error rather than a summary. |
| 3 | A tool-aware support agent combines session memory, FAQ retrieval, model routing, and deterministic fallbacks. | **Pros:** Answers remain grounded, arithmetic is delegated to a restricted calculator, and recent context supports follow-up questions. The service remains useful without AI credentials. **Cons:** In-memory state is process-local and expires. Lexical retrieval may miss paraphrases. Model routing adds latency and API cost. | Restarting or scaling the service can lose or split session history. Only the latest 20 turns are retained. Ambiguous arithmetic can be parsed incorrectly, while unsupported factual questions are safely refused. |

## Notes

Some functionality depends on Gemini credentials. If the API key is not configured, the app will still run using built-in fallback logic for supported flows.
