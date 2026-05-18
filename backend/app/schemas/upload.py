from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


def _example(value: Any) -> dict[str, Any]:
    return {"example": value}


class DatasetUploadResponse(BaseModel):
    filename: str = Field(
        description="Uploaded file name",
        json_schema_extra=_example("bank_customer_dataset.xlsx"),
    )
    rows: int = Field(
        description="Number of data rows parsed from the file",
        json_schema_extra=_example(5000),
    )
    columns: int = Field(
        description="Number of columns parsed from the file",
        json_schema_extra=_example(32),
    )
    column_names: list[str] = Field(description="List of dataset column names")
    missing_values: dict[str, int] = Field(description="Missing value counts per column")
    numeric_summary: dict[str, dict[str, float]] = Field(
        description="Numeric column summary with mean/std/min/max for each column",
    )
    categorical_summary: dict[str, dict[str, int]] = Field(
        description="Categorical value counts for each categorical column",
    )
    duplicate_rows: int = Field(
        description="Number of duplicate rows in the file",
        json_schema_extra=_example(0),
    )
    preview: list[dict[str, Any]] = Field(description="First five rows as JSON objects")


class FilePredictionItem(BaseModel):
    row_index: int = Field(
        description="Zero-based row index in uploaded file",
        json_schema_extra=_example(0),
    )
    churn_prediction: int = Field(
        description="Binary churn prediction (1=churn risk)",
        json_schema_extra=_example(0),
    )
    churn_probability: float = Field(
        description="Predicted churn probability",
        json_schema_extra=_example(0.23),
    )
    risk_class: str = Field(
        description="Predicted risk class",
        json_schema_extra=_example("Low"),
    )
    client_segment: str = Field(
        description="Predicted client segment",
        json_schema_extra=_example("Premium"),
    )


class FilePredictionSummary(BaseModel):
    churn_rate: float = Field(
        description="Average churn prediction rate across predicted rows",
        json_schema_extra=_example(0.18),
    )
    segment_distribution: dict[str, int] = Field(description="Count of predictions per segment")
    risk_distribution: dict[str, int] = Field(description="Count of predictions per risk class")


class PredictFromFileResponse(BaseModel):
    total_rows: int = Field(
        description="Total rows found in the uploaded file",
        json_schema_extra=_example(5000),
    )
    predictions: list[FilePredictionItem] = Field(description="Per-row prediction outputs")
    summary: FilePredictionSummary = Field(description="Aggregate summary over predicted rows")
