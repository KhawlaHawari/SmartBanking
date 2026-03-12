from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from app.utils.config import get_settings
from app.utils.logging import get_logger
from app.utils.preprocessing import clean_dataset_headers

logger = get_logger(__name__)

_MODELS_CACHE: dict[str, Any] = {"loaded": False}
_DATASET_CACHE: dict[str, Any] = {"loaded": False, "data": None}
_EDA_CACHE: dict[str, Any] = {"loaded": False}


def _force_single_thread(model: Any, seen: set[int] | None = None) -> Any:
    if seen is None:
        seen = set()

    obj_id = id(model)
    if obj_id in seen:
        return model
    seen.add(obj_id)

    if hasattr(model, "n_jobs"):
        try:
            setattr(model, "n_jobs", 1)
        except Exception:
            logger.debug("Could not set n_jobs on %s", type(model).__name__)

    if isinstance(model, dict):
        for value in model.values():
            _force_single_thread(value, seen)
        return model

    if isinstance(model, (list, tuple, set)):
        for value in model:
            _force_single_thread(value, seen)
        return model

    if hasattr(model, "get_params") and hasattr(model, "set_params"):
        try:
            n_jobs_params = {
                key: 1
                for key in model.get_params(deep=True)
                if key.endswith("n_jobs")
            }
            if n_jobs_params:
                model.set_params(**n_jobs_params)
        except Exception:
            logger.debug("Could not set nested n_jobs params on %s", type(model).__name__)

    if hasattr(model, "__dict__"):
        for value in vars(model).values():
            _force_single_thread(value, seen)
    return model


def _compute_eda(df: pd.DataFrame) -> dict[str, Any]:
    stats: dict[str, Any] = {}

    if "client_segment" in df.columns:
        seg_counts = df["client_segment"].value_counts(dropna=False)
        total = float(seg_counts.sum()) if seg_counts.sum() else 1.0
        stats["segment_distribution"] = [
            {
                "name": str(name),
                "count": int(count),
                "pct": round((float(count) / total) * 100.0, 2),
            }
            for name, count in seg_counts.items()
        ]
    else:
        stats["segment_distribution"] = []

    if "risk_class" in df.columns:
        risk_counts = df["risk_class"].value_counts(dropna=False)
        stats["risk_distribution"] = [{"name": str(name), "count": int(count)} for name, count in risk_counts.items()]
    else:
        stats["risk_distribution"] = []

    if "recommended_action" in df.columns:
        action_counts = df["recommended_action"].value_counts(dropna=False)
        stats["action_distribution"] = [{"name": str(name), "count": int(count)} for name, count in action_counts.items()]
    else:
        stats["action_distribution"] = []

    if "client_segment" in df.columns and "churn_probability" in df.columns:
        tmp = df.copy()
        tmp["churn_probability"] = pd.to_numeric(tmp["churn_probability"], errors="coerce")
        grouped = tmp.groupby("client_segment", dropna=False)["churn_probability"].mean().reset_index().fillna(0)
        stats["churn_by_segment"] = [
            {
                "segment": str(row["client_segment"]),
                "avg_churn_prob": round(float(row["churn_probability"]), 4),
            }
            for _, row in grouped.iterrows()
        ]
    else:
        stats["churn_by_segment"] = []

    if "risk_class" in df.columns and "credit_score" in df.columns:
        tmp = df.copy()
        tmp["credit_score"] = pd.to_numeric(tmp["credit_score"], errors="coerce")
        grouped = tmp.groupby("risk_class", dropna=False)["credit_score"].agg(["mean", "min", "max"]).reset_index().fillna(0)
        stats["credit_score_by_risk"] = [
            {
                "risk": str(row["risk_class"]),
                "avg": round(float(row["mean"]), 2),
                "min": round(float(row["min"]), 2),
                "max": round(float(row["max"]), 2),
            }
            for _, row in grouped.iterrows()
        ]
    else:
        stats["credit_score_by_risk"] = []

    if {"client_segment", "value_score", "risk_score"}.issubset(df.columns):
        tmp = df.copy()
        tmp["value_score"] = pd.to_numeric(tmp["value_score"], errors="coerce")
        tmp["risk_score"] = pd.to_numeric(tmp["risk_score"], errors="coerce")
        grouped = (
            tmp.groupby("client_segment", dropna=False)
            .agg(
                avg_value_score=("value_score", "mean"),
                avg_risk_score=("risk_score", "mean"),
                count=("client_segment", "size"),
            )
            .reset_index()
            .fillna(0)
        )
        stats["segment_value_risk"] = [
            {
                "segment": str(row["client_segment"]),
                "avg_value_score": round(float(row["avg_value_score"]), 4),
                "avg_risk_score": round(float(row["avg_risk_score"]), 4),
                "count": int(row["count"]),
            }
            for _, row in grouped.iterrows()
        ]
    else:
        stats["segment_value_risk"] = []

    numeric_df = df.apply(pd.to_numeric, errors="coerce")
    target_cols = [col for col in ["risk_score", "value_score"] if col in numeric_df.columns]
    if target_cols:
        corr = numeric_df.corr(numeric_only=True)
        rows: list[dict[str, Any]] = []
        for feature in corr.index:
            if feature in target_cols:
                continue
            risk_corr = float(corr.loc[feature, "risk_score"]) if "risk_score" in corr.columns else 0.0
            value_corr = float(corr.loc[feature, "value_score"]) if "value_score" in corr.columns else 0.0
            if pd.isna(risk_corr):
                risk_corr = 0.0
            if pd.isna(value_corr):
                value_corr = 0.0
            rows.append({"feature": str(feature), "risk_corr": round(risk_corr, 4), "value_corr": round(value_corr, 4)})
        stats["feature_correlations"] = sorted(
            rows,
            key=lambda x: abs(x["risk_corr"]) + abs(x["value_corr"]),
            reverse=True,
        )[:15]
    else:
        stats["feature_correlations"] = []

    stats["loaded"] = True
    return stats


def _load_models() -> None:
    settings = get_settings()
    base = Path(settings.model_dir)
    expected_artifacts = [
        "segmentation_model.pkl",
        "le_segment.pkl",
        "risk_model.pkl",
        "risk_threshold.pkl",
        "churn_model.pkl",
        "churn_threshold.pkl",
        "action_model.pkl",
        "le_action.pkl",
        "kmeans.pkl",
        "training_metrics.json",
    ]

    _MODELS_CACHE.clear()
    _MODELS_CACHE.update({"loaded": False, "metrics": {}, "model_names": []})

    try:
        import joblib
    except Exception:
        logger.exception("Failed importing joblib while loading model artifacts")
        return

    load_map = {
        "segmentation": "segmentation_model.pkl",
        "le_segment": "le_segment.pkl",
        "risk": "risk_model.pkl",
        "risk_threshold": "risk_threshold.pkl",
        "churn": "churn_model.pkl",
        "churn_threshold": "churn_threshold.pkl",
        "action": "action_model.pkl",
        "le_action": "le_action.pkl",
        "kmeans": "kmeans.pkl",
    }

    loaded_ok = True
    for key, filename in load_map.items():
        file_path = base / filename
        try:
            _MODELS_CACHE[key] = _force_single_thread(joblib.load(file_path))
            logger.info("Model artifact loaded: %s", filename)
        except Exception:
            loaded_ok = False
            logger.exception("Failed loading model artifact: %s", filename)

    metrics_path = base / "training_metrics.json"
    try:
        import json

        with open(metrics_path, "r", encoding="utf-8") as f:
            _MODELS_CACHE["metrics"] = json.load(f)
        logger.info("Model artifact loaded: %s", metrics_path.name)
    except Exception:
        loaded_ok = False
        logger.exception("Failed loading model artifact: %s", metrics_path.name)

    _MODELS_CACHE["model_names"] = expected_artifacts
    _MODELS_CACHE["loaded"] = loaded_ok
    logger.info("Model loading complete. loaded=%s", loaded_ok)


def _load_dataset() -> None:
    settings = get_settings()
    dataset_path = Path(settings.dataset_path)

    _DATASET_CACHE.clear()
    _DATASET_CACHE.update({"loaded": False, "data": None})
    _EDA_CACHE.clear()
    _EDA_CACHE.update({"loaded": False})

    try:
        df = pd.read_excel(dataset_path)
        df = clean_dataset_headers(df)
        _DATASET_CACHE["data"] = df
        _DATASET_CACHE["loaded"] = True
        logger.info("Dataset loaded: %s (%s rows)", dataset_path.name, len(df))
    except Exception:
        logger.exception("Failed loading dataset: %s", dataset_path)
        return

    try:
        _EDA_CACHE.update(_compute_eda(_DATASET_CACHE["data"]))
        logger.info("EDA cache computed successfully")
    except Exception:
        _EDA_CACHE.clear()
        _EDA_CACHE.update({"loaded": False})
        logger.exception("Failed computing EDA cache")


def load_startup_assets(force_reload: bool = False) -> None:
    if _MODELS_CACHE.get("loaded") and _DATASET_CACHE.get("loaded") and not force_reload:
        logger.info("Startup assets already loaded; using cached state")
        return
    _load_models()
    _load_dataset()


def get_models() -> dict[str, Any]:
    if not _MODELS_CACHE.get("loaded", False):
        load_startup_assets()
    return _MODELS_CACHE


def get_dataset() -> pd.DataFrame | None:
    if not _DATASET_CACHE.get("loaded", False):
        load_startup_assets()
    return _DATASET_CACHE.get("data")


def get_eda_stats() -> dict[str, Any]:
    if not _EDA_CACHE.get("loaded", False):
        load_startup_assets()
    return _EDA_CACHE
