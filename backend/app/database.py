from __future__ import annotations

from datetime import datetime
from typing import AsyncGenerator

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.utils.config import get_settings
from app.utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


def _normalize_database_url(raw_url: str) -> str:
    if raw_url.startswith("sqlite:///"):
        return raw_url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    return raw_url


DATABASE_URL = _normalize_database_url(settings.database_url)
engine = create_async_engine(DATABASE_URL, future=True)
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    age: Mapped[float | None] = mapped_column(Float, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(50), nullable=True)
    marital_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    education_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    region: Mapped[str | None] = mapped_column(String(50), nullable=True)
    employment_status: Mapped[str | None] = mapped_column(String(50), nullable=True)

    monthly_income: Mapped[float | None] = mapped_column(Float, nullable=True)
    account_balance: Mapped[float | None] = mapped_column(Float, nullable=True)
    savings_balance: Mapped[float | None] = mapped_column(Float, nullable=True)
    credit_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_debt: Mapped[float | None] = mapped_column(Float, nullable=True)
    credit_limit: Mapped[float | None] = mapped_column(Float, nullable=True)
    credit_utilization: Mapped[float | None] = mapped_column(Float, nullable=True)

    tenure_months: Mapped[float | None] = mapped_column(Float, nullable=True)
    num_products: Mapped[int | None] = mapped_column(Integer, nullable=True)
    num_loans: Mapped[int | None] = mapped_column(Integer, nullable=True)
    num_late_payments: Mapped[int | None] = mapped_column(Integer, nullable=True)
    num_defaults: Mapped[int | None] = mapped_column(Integer, nullable=True)
    monthly_transactions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    avg_transaction_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    num_atm_withdrawals: Mapped[int | None] = mapped_column(Integer, nullable=True)

    online_banking_usage: Mapped[str | None] = mapped_column(String(50), nullable=True)
    international_transactions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    days_since_last_activity: Mapped[int | None] = mapped_column(Integer, nullable=True)

    has_investment_account: Mapped[int | None] = mapped_column(Integer, nullable=True)
    investment_balance: Mapped[float | None] = mapped_column(Float, nullable=True)
    has_insurance: Mapped[int | None] = mapped_column(Integer, nullable=True)
    has_mortgage: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mortgage_amount: Mapped[float | None] = mapped_column(Float, nullable=True)

    complaint_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overdraft_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    suspicious_activity_flag: Mapped[int | None] = mapped_column(Integer, nullable=True)

    churn: Mapped[int | None] = mapped_column(Integer, nullable=True)
    risk_class: Mapped[str | None] = mapped_column(String(50), nullable=True)
    recommended_action: Mapped[str | None] = mapped_column(String(100), nullable=True)
    client_segment: Mapped[str | None] = mapped_column(String(100), nullable=True)
    churn_probability: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_probability: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    customer_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    segment: Mapped[str] = mapped_column(String(100), nullable=False)
    segment_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    risk_label: Mapped[str] = mapped_column(String(50), nullable=False)
    risk_probability: Mapped[float] = mapped_column(Float, nullable=False)
    churn_probability: Mapped[float] = mapped_column(Float, nullable=False)
    churn_label: Mapped[str] = mapped_column(String(50), nullable=False)
    recommended_action: Mapped[str] = mapped_column(String(100), nullable=False)
    action_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized")
