from fastapi import FastAPI

app = FastAPI(
    title="Agentic Architect Challenge"
)

@app.get("/")
def home():
    return {
        "message": "API Running"
    }