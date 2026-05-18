from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.load_data import get_models
from app.models.predict import predict_one
from app.schemas.customer import BatchPredictRequest, CustomerInput, ErrorResponse, PredictionResponse
from app.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


def _validated_models(models: dict[str, Any]) -> dict[str, Any]:
    if not models.get("loaded", False):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Prediction models are unavailable. Please retrain and reload model artifacts.",
        )
    return models


@router.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Predict Customer Outcomes",
    description="Runs segmentation, risk, churn, and next-best action models for a single customer payload.",
    tags=["predict"],
    responses={503: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def predict_customer(
    customer: CustomerInput,
    models: dict[str, Any] = Depends(get_models),
) -> PredictionResponse:
    validated_models = _validated_models(models)
    try:
        return predict_one(customer, validated_models)
    except HTTPException:
        raise
    except Exception:
        logger.exception("Single prediction failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Prediction service is temporarily unavailable.",
        )


@router.post(
    "/predict/batch",
    response_model=list[PredictionResponse],
    summary="Batch Predict Customer Outcomes",
    description="Runs model predictions for a batch of customer payloads.",
    tags=["predict"],
    responses={503: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def predict_batch(
    payload: BatchPredictRequest,
    models: dict[str, Any] = Depends(get_models),
) -> list[PredictionResponse]:
    validated_models = _validated_models(models)
    outputs: list[PredictionResponse] = []
    try:
        for customer in payload.customers:
            outputs.append(predict_one(customer, validated_models))
        return outputs
    except Exception:
        logger.exception("Batch prediction failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Batch prediction service is temporarily unavailable.",
        )
