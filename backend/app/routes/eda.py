from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.load_data import get_eda_stats
from app.schemas.customer import EDAResponse, ErrorResponse
from app.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get(
    "/eda",
    response_model=EDAResponse,
    summary="Get EDA Statistics",
    description="Returns precomputed exploratory data analysis statistics from the cached dataset.",
    tags=["eda"],
    responses={503: {"model": ErrorResponse}},
)
def get_eda(eda_stats: dict = Depends(get_eda_stats)) -> EDAResponse:
    if not eda_stats.get("loaded", False):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="EDA stats are unavailable. Ensure the dataset is loaded at startup.",
        )
    try:
        return EDAResponse(**eda_stats)
    except Exception:
        logger.exception("Failed to build EDA response")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="EDA service is temporarily unavailable.",
        )
