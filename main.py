from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(title="Chat Bot API")


class HealthResponse(BaseModel):
    status: str
    app: str


@app.get("/", response_model=HealthResponse)
def root() -> HealthResponse:
    return HealthResponse(status="ok", app="chat-bot")
