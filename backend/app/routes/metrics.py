from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.load_data import get_models
from app.schemas.customer import ErrorResponse, ModelsInfoResponse
from app.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


def _validated_models(models: dict[str, Any]) -> dict[str, Any]:
    if not models.get("loaded", False):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model metrics are unavailable because model artifacts are not loaded.",
        )
    return models


@router.get(
    "/metrics",
    response_model=dict[str, Any],
    summary="Get Training Metrics",
    description="Returns training metrics loaded from training_metrics.json.",
    tags=["metrics"],
    responses={503: {"model": ErrorResponse}},
)
def get_metrics(models: dict[str, Any] = Depends(get_models)) -> dict[str, Any]:
    validated_models = _validated_models(models)
    try:
        return validated_models.get("metrics", {})
    except Exception:
        logger.exception("Failed to return metrics")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Metrics service is temporarily unavailable.",
        )


@router.get(
    "/models/info",
    response_model=ModelsInfoResponse,
    summary="Get Models Information",
    description="Returns expected model artifact names and loaded training metrics.",
    tags=["metrics"],
    responses={503: {"model": ErrorResponse}},
)
def get_models_info(models: dict[str, Any] = Depends(get_models)) -> ModelsInfoResponse:
    validated_models = _validated_models(models)
    try:
        return ModelsInfoResponse(
            model_names=validated_models.get("model_names", []),
            training_metrics=validated_models.get("metrics", {}),
        )
    except Exception:
        logger.exception("Failed to build /api/models/info response")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model information service is temporarily unavailable.",
        )
