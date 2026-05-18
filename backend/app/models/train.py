"""
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘   SMART BANKING â€” ML MODELS                                  â•‘
â•‘   Customer Segmentation & Risk Management                    â•‘
â•‘   Author: Khawla Hawari                                      â•‘
â•‘                                                              â•‘
â•‘   INSTRUCTIONS FOR CODEX:                                    â•‘
â•‘   1. Place this file at: backend/app/models/train.py         â•‘
â•‘   2. Place dataset at:   backend/data/bank_customer_dataset.xlsx â•‘
â•‘   3. Run once:           python app/models/train.py          â•‘
â•‘   4. All .pkl files will be saved to: backend/saved_models/  â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
"""

# ============================================================
# IMPORTS
# ============================================================

import pandas as pd
import numpy as np
import joblib
import json
import os
import warnings
warnings.filterwarnings("ignore")

from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.metrics import (
    accuracy_score, f1_score, roc_auc_score, recall_score,
    precision_score, brier_score_loss, average_precision_score,
    top_k_accuracy_score, adjusted_rand_score
)
from app.utils.logging import get_logger

logger = get_logger(__name__)

# ============================================================
# CONFIG â€” change paths here if needed
# ============================================================

DATA_PATH   = Path("data/bank_customer_dataset.xlsx")
OUTPUT_DIR  = Path("saved_models")
RANDOM_STATE = 42

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# CONSTANTS
# ============================================================

# These columns are engineered from targets â†’ must never be used as features
LEAKY_COLS = [
    "risk_score",
    "value_score",
    "churn_probability",
    "churn_label",
    "customer_id",
]

# All target columns â€” dropped from every feature set
ALL_TARGETS = [
    "client_segment",
    "risk_class",
    "recommended_action",
    "churn_label",
    "churn_probability",
    "risk_binary",
    "churn_binary",
]

# Categorical columns that need OneHotEncoding
CATEGORICAL_COLS = [
    "gender",
    "marital_status",
    "education_level",
    "region",
    "employment_status",
    "online_banking_usage",
]

# ============================================================
# HELPER â€” load and clean dataset
# ============================================================

def load_data(path: Path) -> pd.DataFrame:
    """
    Load bank_customer_dataset.xlsx.
    Handles both formats:
    - With section labels: Row 0 = labels, Row 1 = headers, Row 2+ = data
    - Direct format: Row 0 = headers, Row 1+ = data
    """
    df = pd.read_excel(path, header=0)

    # Check if row 0 looks like section labels (not numeric, all same type)
    first_row = df.iloc[0]
    is_labels = all(isinstance(v, str) for v in first_row if pd.notna(v))
    
    # If first row has section labels, skip it
    if is_labels and not any(pd.to_numeric(first_row, errors='coerce').notna()):
        df = df.iloc[1:].reset_index(drop=True).copy()

    # Normalize column names â€” lowercase and replace spaces
    df.columns = df.columns.str.lower().str.replace(" ", "_")

    # Convert everything possible to numeric
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col])
        except (ValueError, TypeError):
            pass

    return df


# ============================================================
# HELPER â€” build preprocessor for a given feature DataFrame
# ============================================================

def build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    """
    Automatically detects numeric vs categorical columns
    and builds a ColumnTransformer:
      - numeric  â†’ StandardScaler
      - categorical â†’ OneHotEncoder (handle_unknown='ignore')
    """
    num_cols = [
        c for c in X.columns
        if c not in CATEGORICAL_COLS
        and X[c].dtype in [np.float64, np.int64, float, int]
    ]
    cat_cols = [c for c in X.columns if c in CATEGORICAL_COLS]

    transformers = []
    if num_cols:
        transformers.append(("num", StandardScaler(), num_cols))
    if cat_cols:
        transformers.append((
            "cat",
            OneHotEncoder(handle_unknown="ignore", sparse_output=False),
            cat_cols
        ))

    return ColumnTransformer(transformers=transformers, remainder="drop")


# ============================================================
# HELPER â€” get clean feature matrix (no leakage, no targets)
# ============================================================

def get_features(df: pd.DataFrame, extra_drop: list = []) -> pd.DataFrame:
    """
    Returns X with all target and leaky columns removed.
    Pass extra_drop to also remove objective-specific columns
    (e.g. risk_binary when training the churn model).
    """
    cols_to_drop = list(set(LEAKY_COLS + ALL_TARGETS + extra_drop))
    keep = [c for c in df.columns if c not in cols_to_drop]
    return df[keep].fillna(0).copy()


# ============================================================
# HELPER â€” tune decision threshold to hit minimum recall
# ============================================================

def tune_threshold(
    y_true: np.ndarray,
    y_proba: np.ndarray,
    target_recall: float = 0.85
) -> float:
    """
    Sweep thresholds from high to low.
    Return the highest threshold that still achieves target_recall.
    Defaults to 0.5 if none found.
    """
    for t in np.linspace(0.99, 0.01, 300):
        y_pred = (y_proba >= t).astype(int)
        if y_pred.sum() > 0 and recall_score(y_true, y_pred) >= target_recall:
            return float(round(t, 4))
    return 0.5


# ============================================================
# OBJECTIVE 1 â€” CLIENT SEGMENT PREDICTION
# ============================================================

def train_segmentation(df: pd.DataFrame) -> dict:
    logger.info("\n" + "â•" * 55)
    logger.info("  OBJECTIVE 1 â€” CLIENT SEGMENT PREDICTION")
    logger.info("â•" * 55)

    # Encode target
    le_seg = LabelEncoder()
    y = le_seg.fit_transform(df["client_segment"])

    # Features â€” drop own target + leaky cols
    X = get_features(df)

    # Train / test split (stratified)
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y,
        test_size=0.2,
        stratify=y,
        random_state=RANDOM_STATE
    )

    # Build pipeline
    preprocessor = build_preprocessor(X)

    model = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(
            n_estimators=400,
            max_depth=None,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1
        ))
    ])

    model.fit(X_tr, y_tr)

    # Evaluate
    y_pred = model.predict(X_te)
    acc = accuracy_score(y_te, y_pred)
    f1  = f1_score(y_te, y_pred, average="macro")
    logger.info(f"  Accuracy  : {acc:.4f}")
    logger.info(f"  F1-Macro  : {f1:.4f}")

    # â”€â”€ Clustering validation (bonus) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    prep_clone = build_preprocessor(X)
    X_transformed = prep_clone.fit_transform(X)

    kmeans = KMeans(n_clusters=6, random_state=RANDOM_STATE, n_init=10)
    km_labels = kmeans.fit_predict(X_transformed)

    gmm = GaussianMixture(n_components=6, random_state=RANDOM_STATE, n_init=5)
    gmm_labels = gmm.fit_predict(X_transformed)

    ari_km  = adjusted_rand_score(y, km_labels)
    ari_gmm = adjusted_rand_score(y, gmm_labels)
    logger.info(f"  ARI KMeans: {ari_km:.4f}")
    logger.info(f"  ARI GMM   : {ari_gmm:.4f}")

    # â”€â”€ Save â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    joblib.dump(model,  OUTPUT_DIR / "segmentation_model.pkl")
    joblib.dump(le_seg, OUTPUT_DIR / "le_segment.pkl")
    joblib.dump(kmeans, OUTPUT_DIR / "kmeans.pkl")
    logger.info("  âœ“ segmentation_model.pkl")
    logger.info("  âœ“ le_segment.pkl")
    logger.info("  âœ“ kmeans.pkl")

    return {
        "model": "RandomForestClassifier(n=400, balanced)",
        "accuracy": round(acc, 4),
        "f1_macro": round(f1, 4),
        "ari_kmeans": round(ari_km, 4),
        "ari_gmm": round(ari_gmm, 4),
        "n_classes": 6,
        "classes": le_seg.classes_.tolist(),
        "n_features_input": X.shape[1],
        "train_size": len(X_tr),
        "test_size": len(X_te),
    }


# ============================================================
# OBJECTIVE 2 â€” HIGH-RISK CLIENT DETECTION
# ============================================================

def train_risk(df: pd.DataFrame) -> dict:
    logger.info("\n" + "â•" * 55)
    logger.info("  OBJECTIVE 2 â€” HIGH-RISK CLIENT DETECTION")
    logger.info("â•" * 55)

    # Create binary target
    df["risk_binary"] = df["risk_class"].isin(["High", "Very High"]).astype(int)
    dist = df["risk_binary"].value_counts().to_dict()
    logger.info(f"  Class balance â†’ Low Risk: {dist.get(0,0)} | High Risk: {dist.get(1,0)}")

    y = df["risk_binary"].values
    X = get_features(df, extra_drop=["risk_binary", "risk_class"])

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y,
        test_size=0.2,
        stratify=y,
        random_state=RANDOM_STATE
    )

    preprocessor = build_preprocessor(X)

    # Base model
    base = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", GradientBoostingClassifier(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            random_state=RANDOM_STATE
        ))
    ])
    base.fit(X_tr, y_tr)

    # Calibrate probabilities
    model = CalibratedClassifierCV(base, method="isotonic", cv=3)
    model.fit(X_tr, y_tr)

    # Evaluate
    y_proba = model.predict_proba(X_te)[:, 1]
    threshold = tune_threshold(y_te, y_proba, target_recall=0.85)
    y_pred = (y_proba >= threshold).astype(int)

    auc   = roc_auc_score(y_te, y_proba)
    prauc = average_precision_score(y_te, y_proba)
    rec   = recall_score(y_te, y_pred)
    prec  = precision_score(y_te, y_pred, zero_division=0)
    f1    = f1_score(y_te, y_pred, zero_division=0)
    brier = brier_score_loss(y_te, y_proba)

    logger.info(f"  AUC-ROC   : {auc:.4f}")
    logger.info(f"  PR-AUC    : {prauc:.4f}")
    logger.info(f"  Recall    : {rec:.4f}  (threshold={threshold:.4f})")
    logger.info(f"  Precision : {prec:.4f}")
    logger.info(f"  F1        : {f1:.4f}")
    logger.info(f"  Brier     : {brier:.4f}")

    # Save
    joblib.dump(model,     OUTPUT_DIR / "risk_model.pkl")
    joblib.dump(threshold, OUTPUT_DIR / "risk_threshold.pkl")
    logger.info("  âœ“ risk_model.pkl")
    logger.info("  âœ“ risk_threshold.pkl")

    # Clean up temp column
    df.drop(columns=["risk_binary"], inplace=True, errors="ignore")

    return {
        "model": "GradientBoostingClassifier + CalibratedClassifierCV(isotonic)",
        "auc_roc": round(auc, 4),
        "pr_auc": round(prauc, 4),
        "recall": round(rec, 4),
        "precision": round(prec, 4),
        "f1": round(f1, 4),
        "brier": round(brier, 4),
        "decision_threshold": round(threshold, 4),
        "class_distribution": {
            "low_risk": int(dist.get(0, 0)),
            "high_risk": int(dist.get(1, 0))
        },
    }


# ============================================================
# OBJECTIVE 3 â€” CHURN PREDICTION
# ============================================================

def train_churn(df: pd.DataFrame) -> dict:
    logger.info("\n" + "â•" * 55)
    logger.info("  OBJECTIVE 3 â€” CHURN PREDICTION")
    logger.info("â•" * 55)

    # Use binary churn target directly
    # (generates from probability if available, otherwise use as-is)
    churn_q75 = None  # Initialize to None
    if "churn_probability" in df.columns:
        churn_q75 = df["churn_probability"].quantile(0.75)
        df["churn_binary"] = (df["churn_probability"] >= churn_q75).astype(int)
        logger.info(f"  Using churn_probability >= Q75 ({churn_q75:.4f})")
    else:
        # Use the binary churn column directly
        df["churn_binary"] = df["churn"].astype(int)
        logger.info(f"  Using binary churn column directly")
    
    dist = df["churn_binary"].value_counts().to_dict()
    logger.info(f"  Class balance â†’ No Churn: {dist.get(0,0)} | Churn: {dist.get(1,0)}")

    y = df["churn_binary"].values
    X = get_features(df, extra_drop=["churn_binary", "risk_binary"])

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y,
        test_size=0.2,
        stratify=y,
        random_state=RANDOM_STATE
    )

    preprocessor = build_preprocessor(X)

    # Base model
    base = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(
            n_estimators=400,
            max_depth=None,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1
        ))
    ])
    base.fit(X_tr, y_tr)

    # Calibrate probabilities
    model = CalibratedClassifierCV(base, method="isotonic", cv=3)
    model.fit(X_tr, y_tr)

    # Evaluate
    y_proba   = model.predict_proba(X_te)[:, 1]
    threshold = tune_threshold(y_te, y_proba, target_recall=0.80)
    y_pred    = (y_proba >= threshold).astype(int)

    auc   = roc_auc_score(y_te, y_proba)
    f1    = f1_score(y_te, y_pred, zero_division=0)
    rec   = recall_score(y_te, y_pred, zero_division=0)
    prec  = precision_score(y_te, y_pred, zero_division=0)
    brier = brier_score_loss(y_te, y_proba)

    logger.info(f"  AUC-ROC   : {auc:.4f}")
    logger.info(f"  F1        : {f1:.4f}")
    logger.info(f"  Recall    : {rec:.4f}  (threshold={threshold:.4f})")
    logger.info(f"  Precision : {prec:.4f}")
    logger.info(f"  Brier     : {brier:.4f}")

    # Save
    joblib.dump(model,     OUTPUT_DIR / "churn_model.pkl")
    joblib.dump(threshold, OUTPUT_DIR / "churn_threshold.pkl")
    logger.info("  âœ“ churn_model.pkl")
    logger.info("  âœ“ churn_threshold.pkl")

    # Clean up temp column
    df.drop(columns=["churn_binary"], inplace=True, errors="ignore")

    metrics_dict = {
        "model": "RandomForestClassifier(n=400, balanced) + CalibratedClassifierCV(isotonic)",
        "auc_roc": round(auc, 4),
        "f1": round(f1, 4),
        "recall": round(rec, 4),
        "precision": round(prec, 4),
        "brier": round(brier, 4),
        "decision_threshold": round(threshold, 4),
    }
    
    # Only add churn_q75_threshold if it was computed
    if churn_q75 is not None:
        metrics_dict["churn_q75_threshold"] = round(float(churn_q75), 4)
    
    return metrics_dict


# ============================================================
# OBJECTIVE 4 â€” BANK ACTION RECOMMENDATION
# ============================================================

def train_action(df: pd.DataFrame) -> dict:
    logger.info("\n" + "â•" * 55)
    logger.info("  OBJECTIVE 4 â€” BANK ACTION RECOMMENDATION")
    logger.info("â•" * 55)

    # Create recommended actions if not present
    if "recommended_action" not in df.columns:
        # Generate actions based on segment and other characteristics
        actions = []
        for idx, row in df.iterrows():
            segment = row.get("client_segment", "Standard")
            churn_risk = 1 if row.get("churn", 0) else 0
            risk_class = row.get("risk_class", "Low")
            income = row.get("monthly_income", 0)
            
            if segment == "VIP":
                action = "Retain" if churn_risk else "Upsell"
            elif segment == "Premium":
                action = "Retain" if churn_risk else "Upsell"
            elif segment == "Active":
                action = "Upgrade" if income > 5000 else "Monitor"
            elif segment == "Standard":
                action = "Engage" if churn_risk else "Monitor"
            else:
                action = "Monitor"
                
            # Adjust based on risk
            if risk_class == "High":
                action = "Monitor"
            
            actions.append(action)
        
        df["recommended_action"] = actions
        logger.info("  Generated recommended_action from customer characteristics")
    
    # Encode target
    le_action = LabelEncoder()
    y = le_action.fit_transform(df["recommended_action"])

    # Features
    X = get_features(df, extra_drop=["risk_binary", "churn_binary"])

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y,
        test_size=0.2,
        stratify=y,
        random_state=RANDOM_STATE
    )

    preprocessor = build_preprocessor(X)

    model = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(
            n_estimators=400,
            max_depth=None,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1
        ))
    ])

    model.fit(X_tr, y_tr)

    # Evaluate
    y_pred  = model.predict(X_te)
    y_proba = model.predict_proba(X_te)

    acc  = accuracy_score(y_te, y_pred)
    f1   = f1_score(y_te, y_pred, average="macro")
    top3 = top_k_accuracy_score(y_te, y_proba, k=3)

    logger.info(f"  Accuracy     : {acc:.4f}")
    logger.info(f"  F1-Macro     : {f1:.4f}")
    logger.info(f"  Top-3 Acc    : {top3:.4f}")

    # Save
    joblib.dump(model,     OUTPUT_DIR / "action_model.pkl")
    joblib.dump(le_action, OUTPUT_DIR / "le_action.pkl")
    logger.info("  âœ“ action_model.pkl")
    logger.info("  âœ“ le_action.pkl")

    return {
        "model": "RandomForestClassifier(n=400, balanced)",
        "accuracy": round(acc, 4),
        "f1_macro": round(f1, 4),
        "top3_accuracy": round(top3, 4),
        "n_classes": 6,
        "classes": le_action.classes_.tolist(),
        "n_features_input": X.shape[1],
    }


# ============================================================
# PREDICT HELPERS â€” used by FastAPI routes
# ============================================================

def load_all_models(models_dir: Path = OUTPUT_DIR) -> dict:
    """
    Load all saved models into a dict.
    Call this once at FastAPI startup.
    """
    required = [
        "segmentation_model.pkl",
        "le_segment.pkl",
        "risk_model.pkl",
        "risk_threshold.pkl",
        "churn_model.pkl",
        "churn_threshold.pkl",
        "action_model.pkl",
        "le_action.pkl",
    ]
    for fname in required:
        path = models_dir / fname
        if not path.exists():
            raise FileNotFoundError(
                f"Missing model file: {path}\n"
                f"Run: python app/models/train.py"
            )

    return {
        "segmentation":    joblib.load(models_dir / "segmentation_model.pkl"),
        "le_segment":      joblib.load(models_dir / "le_segment.pkl"),
        "risk":            joblib.load(models_dir / "risk_model.pkl"),
        "risk_threshold":  joblib.load(models_dir / "risk_threshold.pkl"),
        "churn":           joblib.load(models_dir / "churn_model.pkl"),
        "churn_threshold": joblib.load(models_dir / "churn_threshold.pkl"),
        "action":          joblib.load(models_dir / "action_model.pkl"),
        "le_action":       joblib.load(models_dir / "le_action.pkl"),
        "kmeans":          joblib.load(models_dir / "kmeans.pkl")
                           if (models_dir / "kmeans.pkl").exists() else None,
    }


def predict_customer(customer_dict: dict, models: dict) -> dict:
    """
    Run all 4 models on a single customer dict.
    """
    X = pd.DataFrame([customer_dict]).fillna(0)

    cols_to_drop = [c for c in (LEAKY_COLS + ALL_TARGETS) if c in X.columns]
    X.drop(columns=cols_to_drop, inplace=True, errors="ignore")

    # â”€â”€ 1. Segment â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    seg_proba = models["segmentation"].predict_proba(X)[0]
    seg_idx   = int(np.argmax(seg_proba))
    segment   = models["le_segment"].inverse_transform([seg_idx])[0]
    seg_conf  = float(round(seg_proba[seg_idx], 4))

    # â”€â”€ 2. Risk â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    risk_proba     = float(models["risk"].predict_proba(X)[0][1])
    risk_threshold = float(models["risk_threshold"])
    risk_label     = "High Risk" if risk_proba >= risk_threshold else "Low Risk"

    # â”€â”€ 3. Churn â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    churn_proba     = float(models["churn"].predict_proba(X)[0][1])
    churn_threshold = float(models["churn_threshold"])

    if churn_proba >= churn_threshold:
        churn_label = "High Churn Risk"
    elif churn_proba >= churn_threshold * 0.5:
        churn_label = "Medium Churn Risk"
    else:
        churn_label = "Low Churn Risk"

    # â”€â”€ 4. Action â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    act_proba = models["action"].predict_proba(X)[0]
    act_idx   = int(np.argmax(act_proba))
    action    = models["le_action"].inverse_transform([act_idx])[0]
    act_conf  = float(round(act_proba[act_idx], 4))

    return {
        "segment":            str(segment),
        "segment_confidence": seg_conf,
        "risk_label":         risk_label,
        "risk_probability":   round(risk_proba, 4),
        "churn_probability":  round(churn_proba, 4),
        "churn_label":        churn_label,
        "recommended_action": str(action),
        "action_confidence":  act_conf,
    }


# ============================================================
# MAIN â€” run training when called directly
# ============================================================

if __name__ == "__main__":
    logger.info("â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—")
    logger.info("â•‘   SMART BANKING â€” TRAINING ALL MODELS               â•‘")
    logger.info("â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•")

    # Load data
    logger.info(f"\n  Loading: {DATA_PATH}")
    df = load_data(DATA_PATH)
    logger.info(f"  Shape  : {df.shape}")

    all_metrics = {}

    # Train all 4 objectives
    all_metrics["segmentation"] = train_segmentation(df)
    all_metrics["risk"]         = train_risk(df)
    all_metrics["churn"]        = train_churn(df)
    all_metrics["action"]       = train_action(df)

    # Save metrics JSON
    metrics_path = OUTPUT_DIR / "training_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(all_metrics, f, indent=2)

    # Final report
    logger.info("\n" + "â•" * 55)
    logger.info("  ALL MODELS SAVED")
    logger.info("â•" * 55)
    logger.info(f"\n  ðŸ“ {OUTPUT_DIR}/")
    for fname in sorted(os.listdir(OUTPUT_DIR)):
        size_kb = os.path.getsize(OUTPUT_DIR / fname) / 1024
        logger.info(f"     {fname:<40s} {size_kb:>8.1f} KB")

    logger.info("\n  ðŸ“Š Results:")
    logger.info(f"     Segmentation â†’ F1-Macro : {all_metrics['segmentation']['f1_macro']}")
    logger.info(f"     Risk         â†’ AUC-ROC  : {all_metrics['risk']['auc_roc']}  | Recall: {all_metrics['risk']['recall']}")
    logger.info(f"     Churn        â†’ AUC-ROC  : {all_metrics['churn']['auc_roc']}  | F1: {all_metrics['churn']['f1']}")
    logger.info(f"     Action       â†’ F1-Macro : {all_metrics['action']['f1_macro']} | Top-3: {all_metrics['action']['top3_accuracy']}")

    logger.info(f"\n  âœ… training_metrics.json saved")
    logger.info("  âœ… Ready for FastAPI backend!\n")

