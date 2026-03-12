from __future__ import annotations

import json
import os
from threading import Lock
from typing import Any

import pandas as pd
from fastapi import HTTPException, status
from groq import Groq, APIError, AuthenticationError, RateLimitError

from app.load_data import get_dataset, get_eda_stats, get_models
from app.utils.logging import get_logger

logger = get_logger(__name__)

_SESSION_MESSAGES: dict[str, list[dict[str, str]]] = {}
_SESSION_LOCK = Lock()
_MAX_SESSION_MESSAGES = 6  # Reduced to avoid token overflow

_CANDIDATE_MODELS = (
    "llama-3.3-70b-versatile",
)


def _chat_unavailable_error(detail: str = "Chat unavailable: API key not configured") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=detail,
    )


def _get_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise _chat_unavailable_error()
    try:
        return Groq(api_key=api_key)
    except Exception as exc:
        logger.exception("Failed to initialize Groq client")
        raise _chat_unavailable_error(f"Chat unavailable: {str(exc)}")


def _map_chat_exception(exc: Exception) -> HTTPException:
    if isinstance(exc, HTTPException):
        return exc
    if isinstance(exc, RateLimitError):
        return _chat_unavailable_error("Chat unavailable: quota exceeded")
    if isinstance(exc, AuthenticationError):
        return _chat_unavailable_error("Chat unavailable: invalid API key")
    if isinstance(exc, APIError):
        return _chat_unavailable_error(f"Chat unavailable: {str(exc)}")
    return _chat_unavailable_error(f"Chat unavailable: {str(exc)}")


def _compute_churn_rate(df: pd.DataFrame | None) -> float:
    if df is None or df.empty:
        return 0.0
    if "churn_probability" in df.columns:
        values = pd.to_numeric(df["churn_probability"], errors="coerce").dropna()
        return round(float(values.mean()), 4) if not values.empty else 0.0
    if "churn" in df.columns:
        values = pd.to_numeric(df["churn"], errors="coerce").dropna()
        return round(float(values.mean()), 4) if not values.empty else 0.0
    return 0.0


def _distribution_map(distribution: list[dict[str, Any]], key: str = "name") -> dict[str, int]:
    result: dict[str, int] = {}
    for item in distribution:
        label = str(item.get(key, "unknown"))
        count = int(item.get("count", 0))
        result[label] = count
    return result


def build_system_prompt() -> tuple[str, list[str]]:
    dataset = get_dataset()
    eda = get_eda_stats()
    models = get_models()

    row_count = int(len(dataset)) if dataset is not None else 0
    churn_rate = _compute_churn_rate(dataset)
    segment_distribution = _distribution_map(eda.get("segment_distribution", []), key="name")
    risk_distribution = _distribution_map(eda.get("risk_distribution", []), key="name")

    # Keep metrics short to avoid token overflow
    metrics = models.get("metrics", {})
    metrics_short = {
        k: {mk: mv for mk, mv in v.items() if mk in ("accuracy", "f1_macro", "auc_roc", "recall", "f1")}
        if isinstance(v, dict) else v
        for k, v in metrics.items()
    }

    prompt = (
        "You are SmartBanking's analytics assistant. Be concise.\n\n"
        f"Dataset: {row_count} rows\n"
        f"Churn rate: {churn_rate}\n"
        f"Segments: {segment_distribution}\n"
        f"Risk: {risk_distribution}\n"
        f"Model metrics: {json.dumps(metrics_short, ensure_ascii=True, default=str)}\n"
    )
    return prompt, ["dataset", "model_metrics"]


def _get_session_messages(session_id: str) -> list[dict[str, str]]:
    with _SESSION_LOCK:
        return list(_SESSION_MESSAGES.get(session_id, []))


def _append_session_messages(session_id: str, user_message: str, assistant_reply: str) -> None:
    with _SESSION_LOCK:
        session_messages = _SESSION_MESSAGES.setdefault(session_id, [])
        session_messages.append({"role": "user", "content": user_message})
        session_messages.append({"role": "assistant", "content": assistant_reply})
        if len(session_messages) > _MAX_SESSION_MESSAGES:
            _SESSION_MESSAGES[session_id] = session_messages[-_MAX_SESSION_MESSAGES:]


def clear_session_history(session_id: str) -> bool:
    with _SESSION_LOCK:
        _SESSION_MESSAGES.pop(session_id, None)
    return True


def list_available_models() -> list[str]:
    return list(_CANDIDATE_MODELS)


def generate_chat_reply(message: str, session_id: str) -> dict[str, Any]:
    try:
        client = _get_client()
        system_prompt, sources = build_system_prompt()
        history = _get_session_messages(session_id)

        messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
        for entry in history:
            messages.append({"role": entry["role"], "content": entry["content"]})
        messages.append({"role": "user", "content": message})

        reply = ""
        for model_name in _CANDIDATE_MODELS:
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=512,
            )
            reply = (response.choices[0].message.content or "").strip()
            if reply:
                logger.info("Groq response generated using model: %s", model_name)
                break

        if not reply:
            raise ValueError("Empty Groq response")

        _append_session_messages(session_id=session_id, user_message=message, assistant_reply=reply)
        return {"reply": reply, "session_id": session_id, "sources": sources}

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Groq chat request failed: %s", exc)
        raise _map_chat_exception(exc)