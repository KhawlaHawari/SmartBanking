from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


VALID_CUSTOMER = {
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


@pytest.mark.asyncio
async def test_health_check() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["models_loaded"] is True
    assert body["eda_loaded"] is True


@pytest.mark.asyncio
async def test_single_predict_valid() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/predict", json=VALID_CUSTOMER)
    assert response.status_code == 200
    body = response.json()
    assert "segment" in body
    assert "risk_label" in body
    assert "recommended_action" in body


@pytest.mark.asyncio
async def test_batch_predict_valid() -> None:
    payload = {"customers": [VALID_CUSTOMER, {**VALID_CUSTOMER, "age": 31, "monthly_income": 4000}]}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/predict/batch", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 2


@pytest.mark.asyncio
async def test_predict_missing_fields_returns_422() -> None:
    invalid_payload = {"age": 42, "monthly_income": 6200}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/predict", json=invalid_payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_predict_bad_types_returns_422() -> None:
    invalid_payload = {**VALID_CUSTOMER, "age": "not-a-number"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/predict", json=invalid_payload)
    assert response.status_code == 422
