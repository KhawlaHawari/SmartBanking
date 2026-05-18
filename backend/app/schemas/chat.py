from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


def _example(value: Any) -> dict[str, Any]:
    return {"example": value}


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        description="User message sent to the SmartBanking chat assistant",
        json_schema_extra=_example("What is the average churn rate?"),
    )
    session_id: str = Field(
        min_length=1,
        description="Chat session identifier used to preserve conversation context",
        json_schema_extra=_example("abc123"),
    )


class ChatResponse(BaseModel):
    reply: str = Field(description="Assistant reply text")
    session_id: str = Field(
        description="Session ID used for this conversation",
        json_schema_extra=_example("abc123"),
    )
    sources: list[str] = Field(
        description="Data sources used to formulate the answer",
        json_schema_extra=_example(["dataset", "model_metrics"]),
    )


class ChatModelsResponse(BaseModel):
    model_names: list[str] = Field(
        description="Gemini model names available for the configured API key",
        json_schema_extra=_example(["models/gemini-1.5-flash-latest"]),
    )


class ChatClearResponse(BaseModel):
    cleared: bool = Field(
        description="Indicates whether the session history was cleared",
        json_schema_extra=_example(True),
    )
