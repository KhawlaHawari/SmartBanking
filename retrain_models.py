from __future__ import annotations
import json
import os
import sys
from pathlib import Path


def _configure_utf8_output() -> None:
    # Avoid Windows cp1252 encoding crashes when imported training code prints Unicode.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass


def main() -> None:
    root_dir = Path(__file__).resolve().parent
    backend_dir = root_dir / "backend"
    data_path = backend_dir / "data" / "bank_customer_dataset.xlsx"
    models_dir = backend_dir / "saved_models"
    metrics_path = models_dir / "training_metrics.json"
    models_dir.mkdir(parents=True, exist_ok=True)
    data_path.parent.mkdir(parents=True, exist_ok=True)

    # Ensure backend modules can be imported from project root.
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))

    # Match existing training behavior that uses relative paths.
    os.chdir(backend_dir)

    # ── MLflow setup ──────────────────────────────────────────────────────────
    import mlflow
    mlflow.set_tracking_uri("file:./mlruns")          # stores runs locally
    mlflow.set_experiment("SmartBanking")
    # ─────────────────────────────────────────────────────────────────────────

    from generate_data import generate_banking_dataset, save_dataset
    from app.models import train as train_module

    print("Deleting existing .pkl model files...")
    removed_files: list[str] = []
    for pkl_path in sorted(models_dir.glob("*.pkl")):
        pkl_path.unlink(missing_ok=True)
        removed_files.append(pkl_path.name)
        print(f"  removed: {pkl_path.name}")
    if not removed_files:
        print("  no existing .pkl files found")

    if metrics_path.exists():
        metrics_path.unlink(missing_ok=True)
        print("  removed: training_metrics.json")

    print("\nGenerating fresh dataset...")
    generated_df = generate_banking_dataset(n_samples=5000)
    save_dataset(generated_df, data_path)
    print(f"  generated: {data_path}")

    print("\nTraining models with MLflow tracking...")
    df = train_module.load_data(data_path)

    all_metrics: dict[str, dict] = {}

    # ── Helper: log a model run ───────────────────────────────────────────────
    def log_run(name: str, metrics: dict) -> dict:
        with mlflow.start_run(run_name=name):
            mlflow.set_tag("model_type", name)
            mlflow.log_param("n_samples", 5000)

            # Log every numeric metric that comes back from training
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    mlflow.log_metric(key, round(float(value), 6))

            # Log the saved .pkl files as artifacts
            for pkl_path in models_dir.glob(f"{name}*.pkl"):
                mlflow.log_artifact(str(pkl_path), artifact_path="models")

            print(f"  [MLflow] Run logged: {name} → metrics: {list(metrics.keys())}")
        return metrics
    # ─────────────────────────────────────────────────────────────────────────

    all_metrics["segmentation"] = log_run(
        "segmentation", train_module.train_segmentation(df)
    )
    all_metrics["risk"] = log_run(
        "risk", train_module.train_risk(df)
    )
    all_metrics["churn"] = log_run(
        "churn", train_module.train_churn(df)
    )
    all_metrics["action"] = log_run(
        "action", train_module.train_action(df)
    )

    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(all_metrics, f, indent=2)
    print(f"  saved: {metrics_path.name}")

    expected_files = [
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

    print("\nSaved artifacts:")
    missing: list[str] = []
    for filename in expected_files:
        file_path = models_dir / filename
        if file_path.exists():
            print(f"  ok: {filename}")
        else:
            print(f"  missing: {filename}")
            missing.append(filename)

    if missing:
        raise RuntimeError(f"Missing expected artifact(s): {', '.join(missing)}")

    print("\nRetraining complete. All expected files were generated.")
    print("\n✅ MLflow tracking complete!")
    print("   View your runs:  mlflow ui")
    print("   Then open:       http://127.0.0.1:5000")


if __name__ == "__main__":
    _configure_utf8_output()
    main()