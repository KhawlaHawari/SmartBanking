from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


def _example(value: Any) -> dict[str, Any]:
    return {"example": value}


class ErrorResponse(BaseModel):
    detail: str = Field(
        description="Error message describing what failed",
        json_schema_extra=_example("Models are not available"),
    )


class CustomerInput(BaseModel):
    age: float = Field(description="Customer age in years", json_schema_extra=_example(42))
    monthly_income: float = Field(description="Monthly income", json_schema_extra=_example(6200))
    account_balance: float | None = Field(
        default=None,
        description="Current account balance",
        json_schema_extra=_example(18500),
    )
    savings_balance: float | None = Field(
        default=None,
        description="Savings account balance",
        json_schema_extra=_example(9100),
    )
    tenure_months: float | None = Field(
        default=None,
        description="Customer tenure in months",
        json_schema_extra=_example(48),
    )
    num_products: float | None = Field(
        default=None,
        description="Number of products owned",
        json_schema_extra=_example(3),
    )
    credit_score: float = Field(description="Credit score", json_schema_extra=_example(690))
    total_debt: float | None = Field(
        default=None,
        description="Total debt value",
        json_schema_extra=_example(7400),
    )
    credit_limit: float | None = Field(
        default=None,
        description="Assigned credit limit",
        json_schema_extra=_example(15000),
    )
    credit_utilization: float | None = Field(
        default=None,
        description="Credit utilization ratio",
        json_schema_extra=_example(0.42),
    )
    num_loans: float | None = Field(
        default=None,
        description="Number of active loans",
        json_schema_extra=_example(2),
    )
    num_late_payments: float | None = Field(
        default=None,
        description="Late payments count",
        json_schema_extra=_example(1),
    )
    num_defaults: float | None = Field(
        default=None,
        description="Defaults count",
        json_schema_extra=_example(0),
    )
    monthly_transactions: float | None = Field(
        default=None,
        description="Monthly transaction count",
        json_schema_extra=_example(67),
    )
    avg_transaction_amount: float | None = Field(
        default=None,
        description="Average transaction amount",
        json_schema_extra=_example(94),
    )
    num_atm_withdrawals: float | None = Field(
        default=None,
        description="ATM withdrawals per month",
        json_schema_extra=_example(4),
    )
    international_transactions: float | None = Field(
        default=None,
        description="International transaction count",
        json_schema_extra=_example(2),
    )
    has_investment_account: float | None = Field(
        default=None,
        description="1 if customer has investment account",
        json_schema_extra=_example(1),
    )
    investment_balance: float | None = Field(
        default=None,
        description="Investment account balance",
        json_schema_extra=_example(12000),
    )
    has_insurance: float | None = Field(
        default=None,
        description="1 if customer has insurance products",
        json_schema_extra=_example(1),
    )
    has_mortgage: float | None = Field(
        default=None,
        description="1 if customer has a mortgage",
        json_schema_extra=_example(0),
    )
    mortgage_amount: float | None = Field(
        default=None,
        description="Mortgage principal amount",
        json_schema_extra=_example(0),
    )
    days_since_last_activity: float | None = Field(
        default=None,
        description="Days since last account activity",
        json_schema_extra=_example(3),
    )
    complaint_count: float | None = Field(
        default=None,
        description="Customer complaint count",
        json_schema_extra=_example(0),
    )
    overdraft_count: float | None = Field(
        default=None,
        description="Number of overdraft events",
        json_schema_extra=_example(0),
    )
    suspicious_activity_flag: float | None = Field(
        default=None,
        description="Suspicious activity flag (1/0)",
        json_schema_extra=_example(0),
    )
    gender: str = Field(description="Customer gender", json_schema_extra=_example("Male"))
    marital_status: str | None = Field(
        default=None,
        description="Marital status",
        json_schema_extra=_example("Married"),
    )
    education_level: str | None = Field(
        default=None,
        description="Education level",
        json_schema_extra=_example("Bachelor"),
    )
    region: str = Field(description="Geographic region", json_schema_extra=_example("West"))
    employment_status: str | None = Field(
        default=None,
        description="Employment status",
        json_schema_extra=_example("Employed"),
    )
    online_banking_usage: str | None = Field(
        default=None,
        description="Online banking usage level",
        json_schema_extra=_example("High"),
    )
    churn: float | None = Field(
        default=None,
        description="Known churn label (if available)",
        json_schema_extra=_example(0),
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "age": 42,
                "monthly_income": 6200,
                "account_balance": 18500,
                "savings_balance": 9100,
                "tenure_months": 48,
                "num_products": 3,
                "credit_score": 690,
                "total_debt": 7400,
                "credit_limit": 15000,
                "credit_utilization": 0.42,
                "num_loans": 2,
                "num_late_payments": 1,
                "num_defaults": 0,
                "monthly_transactions": 67,
                "avg_transaction_amount": 94,
                "num_atm_withdrawals": 4,
                "international_transactions": 2,
                "has_investment_account": 1,
                "investment_balance": 12000,
                "has_insurance": 1,
                "has_mortgage": 0,
                "mortgage_amount": 0,
                "days_since_last_activity": 3,
                "complaint_count": 0,
                "overdraft_count": 0,
                "suspicious_activity_flag": 0,
                "gender": "Male",
                "marital_status": "Married",
                "education_level": "Bachelor",
                "region": "West",
                "employment_status": "Employed",
                "online_banking_usage": "High",
                "churn": 0,
            }
        }
    )


class PredictionResponse(BaseModel):
    segment: str = Field(description="Predicted customer segment", json_schema_extra=_example("Active"))
    segment_confidence: float = Field(
        description="Confidence score of segment prediction",
        json_schema_extra=_example(0.91),
    )
    risk_label: str = Field(description="Predicted risk label", json_schema_extra=_example("Low Risk"))
    risk_probability: float = Field(
        description="Probability of high risk",
        json_schema_extra=_example(0.12),
    )
    churn_probability: float = Field(
        description="Predicted churn probability",
        json_schema_extra=_example(0.23),
    )
    churn_label: str = Field(
        description="Predicted churn risk label",
        json_schema_extra=_example("Low Churn Risk"),
    )
    recommended_action: str = Field(
        description="Recommended next-best action",
        json_schema_extra=_example("Upsell"),
    )
    action_confidence: float = Field(
        description="Confidence score of action recommendation",
        json_schema_extra=_example(0.87),
    )


class BatchPredictRequest(BaseModel):
    customers: list[CustomerInput] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Batch payload of customer records for prediction",
        json_schema_extra=_example({"customers": [{"age": 42, "monthly_income": 6200, "credit_score": 690}]}),
    )


class HealthResponse(BaseModel):
    status: str = Field(description="Service status", json_schema_extra=_example("ok"))
    models_loaded: bool = Field(
        description="Indicates whether all model artifacts loaded",
        json_schema_extra=_example(True),
    )
    eda_loaded: bool = Field(
        description="Indicates whether EDA dataset cache loaded",
        json_schema_extra=_example(True),
    )


class MetricsResponse(BaseModel):
    metrics: dict[str, Any] = Field(description="Training metrics keyed by model name")


class ModelsInfoResponse(BaseModel):
    model_names: list[str] = Field(description="List of expected model artifact filenames")
    training_metrics: dict[str, Any] = Field(description="Metrics from training_metrics.json")


class EDAResponse(BaseModel):
    loaded: bool = Field(
        description="Indicates whether EDA cache is loaded",
        json_schema_extra=_example(True),
    )
    segment_distribution: list[dict[str, Any]] = Field(default_factory=list)
    risk_distribution: list[dict[str, Any]] = Field(default_factory=list)
    action_distribution: list[dict[str, Any]] = Field(default_factory=list)
    churn_by_segment: list[dict[str, Any]] = Field(default_factory=list)
    credit_score_by_risk: list[dict[str, Any]] = Field(default_factory=list)
    segment_value_risk: list[dict[str, Any]] = Field(default_factory=list)
    feature_correlations: list[dict[str, Any]] = Field(default_factory=list)
