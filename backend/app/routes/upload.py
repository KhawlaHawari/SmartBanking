from __future__ import annotations

from collections import Counter
from io import BytesIO
from typing import Any

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import ValidationError

from app.load_data import get_models
from app.models.predict import predict_one
from app.schemas.customer import CustomerInput, ErrorResponse
from app.schemas.upload import (
    DatasetUploadResponse,
    FilePredictionItem,
    FilePredictionSummary,
    PredictFromFileResponse,
)
from app.utils.config import get_settings
from app.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

_ALLOWED_EXTENSIONS = {".csv", ".xlsx"}
_REQUIRED_COLUMNS = ("age", "monthly_income", "credit_score", "gender", "region")


def _validate_filename(filename: str | None) -> str:
    if not filename:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Uploaded file must have a filename.")
    lowered = filename.lower()
    if not any(lowered.endswith(ext) for ext in _ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid file type. Only .xlsx and .csv files are supported.",
        )
    return filename


async def _read_upload_dataframe(file: UploadFile) -> tuple[str, pd.DataFrame]:
    filename = _validate_filename(file.filename)
    content = await file.read()
    max_bytes = get_settings().max_upload_size_bytes

    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Uploaded file exceeds max size of {get_settings().max_upload_size_mb}MB.",
        )

    try:
        if filename.lower().endswith(".csv"):
            df = pd.read_csv(BytesIO(content))
        else:
            df = pd.read_excel(BytesIO(content))
    except Exception:
        logger.exception("Failed parsing uploaded file: %s", filename)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Failed to parse uploaded file.",
        )

    if df.empty:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Uploaded file has no rows.",
        )

    # Normalize incoming columns for model compatibility.
    df.columns = [str(col).strip().lower().replace(" ", "_") for col in df.columns]
    return filename, df


def _numeric_summary(df: pd.DataFrame) -> dict[str, dict[str, float]]:
    result: dict[str, dict[str, float]] = {}
    numeric_df = df.select_dtypes(include="number")

    for col in numeric_df.columns:
        values = pd.to_numeric(numeric_df[col], errors="coerce").dropna()
        if values.empty:
            continue
        result[str(col)] = {
            "mean": round(float(values.mean()), 4),
            "std": round(float(values.std(ddof=0)), 4),
            "min": round(float(values.min()), 4),
            "max": round(float(values.max()), 4),
        }
    return result


def _categorical_summary(df: pd.DataFrame) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    categorical_df = df.select_dtypes(exclude="number")

    for col in categorical_df.columns:
        counts = categorical_df[col].value_counts(dropna=False)
        result[str(col)] = {
            ("null" if pd.isna(value) else str(value)): int(count)
            for value, count in counts.items()
        }
    return result


@router.post(
    "/upload/dataset",
    response_model=DatasetUploadResponse,
    summary="Upload Dataset",
    description="Uploads a CSV/XLSX file and returns data quality/profile statistics.",
    tags=["upload"],
    responses={422: {"model": ErrorResponse}},
)
async def upload_dataset(file: UploadFile = File(...)) -> DatasetUploadResponse:
    filename, df = await _read_upload_dataframe(file)
    missing_values = {str(col): int(count) for col, count in df.isna().sum().to_dict().items()}
    preview_records = df.head(5).where(pd.notna(df), None).to_dict(orient="records")

    return DatasetUploadResponse(
        filename=filename,
        rows=int(len(df)),
        columns=int(len(df.columns)),
        column_names=[str(c) for c in df.columns],
        missing_values=missing_values,
        numeric_summary=_numeric_summary(df),
        categorical_summary=_categorical_summary(df),
        duplicate_rows=int(df.duplicated().sum()),
        preview=preview_records,
    )


@router.post(
    "/upload/predict-from-file",
    response_model=PredictFromFileResponse,
    summary="Predict From Uploaded File",
    description="Runs model predictions for each valid row in an uploaded CSV/XLSX customer dataset.",
    tags=["upload"],
    responses={422: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
async def predict_from_file(
    file: UploadFile = File(...),
    models: dict[str, Any] = Depends(get_models),
) -> PredictFromFileResponse:
    if not models.get("loaded", False):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Prediction models are unavailable. Please retrain and reload model artifacts.",
        )

    _, df = await _read_upload_dataframe(file)
    predictions: list[FilePredictionItem] = []

    for row_index, row in df.iterrows():
        missing_required = [col for col in _REQUIRED_COLUMNS if col not in df.columns or pd.isna(row.get(col))]
        if missing_required:
            logger.warning("Skipping row %s due to missing required columns: %s", row_index, ", ".join(missing_required))
            continue

        payload: dict[str, Any] = {}
        for field_name in CustomerInput.model_fields:
            if field_name in df.columns:
                value = row.get(field_name)
                payload[field_name] = None if pd.isna(value) else value

        try:
            customer = CustomerInput(**payload)
        except ValidationError as exc:
            logger.warning("Skipping row %s due to validation error: %s", row_index, exc)
            continue

        try:
            prediction = predict_one(customer, models)
        except Exception as exc:
            logger.exception("Model prediction failed for row %s: %s", row_index, exc)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Prediction service is temporarily unavailable.",
            )

        churn_threshold = float(models.get("churn_threshold", 0.5))
        churn_prediction = int(prediction.churn_probability >= churn_threshold)
        risk_class = "High" if "high" in prediction.risk_label.lower() else "Low"

        predictions.append(
            FilePredictionItem(
                row_index=int(row_index),
                churn_prediction=churn_prediction,
                churn_probability=float(prediction.churn_probability),
                risk_class=risk_class,
                client_segment=prediction.segment,
            ),
        )

    segment_distribution = dict(Counter([item.client_segment for item in predictions]))
    risk_distribution = dict(Counter([item.risk_class for item in predictions]))
    churn_rate = round(
        (sum(item.churn_prediction for item in predictions) / len(predictions)) if predictions else 0.0,
        4,
    )

    return PredictFromFileResponse(
        total_rows=int(len(df)),
        predictions=predictions,
        summary=FilePredictionSummary(
            churn_rate=churn_rate,
            segment_distribution={str(k): int(v) for k, v in segment_distribution.items()},
            risk_distribution={str(k): int(v) for k, v in risk_distribution.items()},
        ),
    )
