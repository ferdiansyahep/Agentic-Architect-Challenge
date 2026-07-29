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

## Notes

Some functionality depends on Gemini credentials. If the API key is not configured, the app will still run using built-in fallback logic for supported flows.
