from __future__ import annotations

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import init_db
from app.load_data import get_eda_stats, get_models, load_startup_assets
from app.routes.auth import router as auth_router
from app.routes.chat import router as chat_router
from app.routes.eda import router as eda_router
from app.routes.metrics import router as metrics_router
from app.routes.predict import router as predict_router
from app.routes.upload import router as upload_router
from app.schemas.customer import HealthResponse
from app.utils.config import get_settings
from app.utils.logging import get_logger, setup_logging

load_dotenv()

settings = get_settings()
setup_logging(settings.log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Starting application lifespan")
    load_startup_assets(force_reload=True)
    await init_db()
    yield
    logger.info("Stopping application lifespan")


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(predict_router, prefix="/api")
app.include_router(metrics_router, prefix="/api")
app.include_router(eda_router, prefix="/api")
app.include_router(upload_router, prefix="/api")
app.include_router(chat_router, prefix="/api")


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.get(
    "/api/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Returns API and model/dataset readiness flags.",
    tags=["health"],
)
def health() -> HealthResponse:
    models = get_models()
    eda = get_eda_stats()
    return HealthResponse(
        status="ok",
        models_loaded=bool(models.get("loaded", False)),
        eda_loaded=bool(eda.get("loaded", False)),
    )


@app.get(
    "/api/stats",
    response_model=dict[str, float | int],
    summary="Get Chat Statistics",
    description="Returns aggregated stats for dashboard/chat assistant widgets.",
    tags=["health"],
)
def get_stats_for_chat() -> dict[str, float | int]:
    eda = get_eda_stats()
    risk_dist = eda.get("risk_distribution", [])
    segment_dist = eda.get("segment_distribution", [])
    churn_by_seg = eda.get("churn_by_segment", [])

    high_risk_count = next((r["count"] for r in risk_dist if "high" in str(r["name"]).lower()), 0)
    total_customers = sum(r.get("count", 0) for r in segment_dist)
    avg_churn = sum(c.get("avg_churn_prob", 0) for c in churn_by_seg) / len(churn_by_seg) if churn_by_seg else 0.289
    at_risk_count = next((s["count"] for s in segment_dist if "at-risk" in str(s["name"]).lower()), 0)

    return {
        "high_risk_count": int(high_risk_count),
        "high_risk_pct": round((high_risk_count / max(total_customers, 1)) * 100, 1),
        "total_customers": int(total_customers),
        "avg_churn": round(avg_churn * 100, 1),
        "at_risk_middle_pct": round((at_risk_count / max(total_customers, 1)) * 100, 1),
        "models_active": 4,
    }
