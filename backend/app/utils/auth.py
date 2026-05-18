from __future__ import annotations

import secrets
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field

from app.utils.config import get_settings
from app.utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Store OTP codes in memory (in production, use Redis or database)
OTP_STORE: dict[str, dict] = {}


def _example(value: Any) -> dict[str, Any]:
    return {"example": value}


class LoginRequest(BaseModel):
    enterprise: str = Field(description="Enterprise name", json_schema_extra=_example("AlphaBank"))
    username: str = Field(description="Username or email", json_schema_extra=_example("john@example.com"))
    password: str = Field(description="Password", json_schema_extra=_example("demo1234"))


class OTPRequest(BaseModel):
    email: EmailStr = Field(
        description="Email address to receive OTP",
        json_schema_extra=_example("john@example.com"),
    )


class OTPVerifyRequest(BaseModel):
    email: EmailStr = Field(
        description="Email address OTP was sent to",
        json_schema_extra=_example("john@example.com"),
    )
    otp: str = Field(description="6-digit OTP code", json_schema_extra=_example("123456"))


class LoginResponse(BaseModel):
    success: bool
    message: str
    username: Optional[str] = None
    enterprise: Optional[str] = None
    email: Optional[str] = None


def generate_otp() -> str:
    return "".join([str(secrets.randbelow(10)) for _ in range(6)])


def send_otp_email(email: str, otp: str) -> bool:
    if settings.email_demo_mode:
        logger.info("EMAIL DEMO MODE | To=%s | OTP=%s", email, otp)
        return True

    if not settings.sender_password:
        logger.warning("No sender password configured; OTP email cannot be sent for %s", email)
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = settings.sender_email
        msg["To"] = email
        msg["Subject"] = "SmartBank Authentication Code"

        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px;">
                <div style="max-width: 500px; background: white; border-radius: 10px; padding: 40px; margin: 0 auto; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h1 style="color: #00d4ff; margin: 0 0 20px 0;">SmartBank</h1>
                    <p style="color: #333; font-size: 16px; margin-bottom: 20px;">
                        Your authentication code is:
                    </p>
                    <div style="background: #f0f0f0; border: 2px solid #00d4ff; border-radius: 8px; padding: 20px; text-align: center; margin: 30px 0;">
                        <code style="font-size: 32px; font-weight: bold; color: #00d4ff; letter-spacing: 5px;">
                            {otp}
                        </code>
                    </div>
                    <p style="color: #666; font-size: 14px; margin-bottom: 10px;">
                        This code will expire in 10 minutes.
                    </p>
                </div>
            </body>
        </html>
        """

        msg.attach(MIMEText(body, "html"))
        with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.sender_email, settings.sender_password)
            server.send_message(msg)

        logger.info("OTP email sent to %s", email)
        return True
    except Exception:
        logger.exception("Failed to send OTP email to %s", email)
        return False


def store_otp(email: str, otp: str) -> None:
    OTP_STORE[email] = {
        "otp": otp,
        "expires_at": datetime.utcnow() + timedelta(minutes=10),
        "attempts": 0,
    }


def verify_otp(email: str, otp: str) -> bool:
    if email not in OTP_STORE:
        return False

    stored = OTP_STORE[email]
    if datetime.utcnow() > stored["expires_at"]:
        del OTP_STORE[email]
        return False

    if stored["attempts"] >= 5:
        del OTP_STORE[email]
        return False

    if stored["otp"] == otp:
        del OTP_STORE[email]
        return True

    stored["attempts"] += 1
    return False


def clear_expired_otps() -> None:
    expired = [email for email, data in OTP_STORE.items() if datetime.utcnow() > data["expires_at"]]
    for email in expired:
        del OTP_STORE[email]
