from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from app.schemas.customer import CustomerInput, PredictionResponse
from app.models.train import predict_customer as _predict_customer


def _to_dataframe(customer: CustomerInput) -> pd.DataFrame:
    """Convert CustomerInput pydantic model to DataFrame."""
    payload = customer.model_dump()
    return pd.DataFrame([payload]).fillna(0)


def predict_one(customer: CustomerInput, models: dict) -> PredictionResponse:
    """
    Run prediction for a single customer using all 4 trained models.
    
    Args:
        customer: CustomerInput pydantic model
        models: dict with all loaded models from train.load_all_models()
    
    Returns:
        PredictionResponse with predictions from all 4 objectives
    """
    # Convert to dict for internal prediction function
    customer_dict = customer.model_dump(exclude_unset=False)
    
    # Get predictions from all 4 models
    prediction_dict = _predict_customer(customer_dict, models)
    
    return PredictionResponse(
        segment=prediction_dict["segment"],
        segment_confidence=prediction_dict["segment_confidence"],
        risk_label=prediction_dict["risk_label"],
        risk_probability=prediction_dict["risk_probability"],
        churn_probability=prediction_dict["churn_probability"],
        churn_label=prediction_dict["churn_label"],
        recommended_action=prediction_dict["recommended_action"],
        action_confidence=prediction_dict["action_confidence"],
    )
