from __future__ import annotations

from fastapi import APIRouter

from app.schemas.chat import ChatClearResponse, ChatModelsResponse, ChatRequest, ChatResponse
from app.schemas.customer import ErrorResponse
from app.utils.chat_engine import clear_session_history, generate_chat_reply, list_available_models

router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Chat With SmartBanking Assistant",
    description="Returns an assistant answer using dataset, EDA, and model training metrics context.",
    tags=["chat"],
    responses={503: {"model": ErrorResponse}},
)
def chat(payload: ChatRequest) -> ChatResponse:
    result = generate_chat_reply(message=payload.message, session_id=payload.session_id)
    return ChatResponse(**result)


@router.get(
    "/chat/models",
    response_model=ChatModelsResponse,
    summary="List Available Gemini Models",
    description="Returns model names visible to the configured Gemini API key.",
    tags=["chat"],
    responses={503: {"model": ErrorResponse}},
)
def get_chat_models() -> ChatModelsResponse:
    return ChatModelsResponse(model_names=list_available_models())


@router.delete(
    "/chat/{session_id}",
    response_model=ChatClearResponse,
    summary="Clear Chat Session",
    description="Clears stored in-memory conversation history for the specified session.",
    tags=["chat"],
)
def clear_chat_session(session_id: str) -> ChatClearResponse:
    return ChatClearResponse(cleared=clear_session_history(session_id))
