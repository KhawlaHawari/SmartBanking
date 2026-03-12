from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.schemas.customer import ErrorResponse
from app.utils.auth import (
    LoginRequest,
    LoginResponse,
    OTPRequest,
    OTPVerifyRequest,
    generate_otp,
    send_otp_email,
    store_otp,
    verify_otp,
)
from app.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])


class RequestOTPResponse(BaseModel):
    success: bool
    message: str


class VerifyOTPResponse(BaseModel):
    success: bool
    message: str
    user: dict | None = None


@router.post(
    "/request-otp",
    response_model=RequestOTPResponse,
    summary="Request OTP",
    description="Generates and sends an OTP to the provided email address.",
    tags=["authentication"],
    responses={500: {"model": ErrorResponse}},
)
async def request_otp(request: OTPRequest) -> RequestOTPResponse:
    try:
        otp = generate_otp()
        success = send_otp_email(request.email, otp)
        store_otp(request.email, otp)
        if success:
            return RequestOTPResponse(success=True, message=f"Authentication code sent to {request.email}")
        return RequestOTPResponse(
            success=True,
            message=f"Auth code: {otp} (email delivery may have failed - check logs)",
        )
    except Exception:
        logger.exception("Failed to request OTP for email %s", request.email)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP.",
        )


@router.post(
    "/verify-otp",
    response_model=VerifyOTPResponse,
    summary="Verify OTP",
    description="Validates OTP and completes authentication.",
    tags=["authentication"],
    responses={401: {"model": ErrorResponse}},
)
async def verify_otp_endpoint(request: OTPVerifyRequest) -> VerifyOTPResponse:
    if verify_otp(request.email, request.otp):
        return VerifyOTPResponse(
            success=True,
            message="Authentication successful",
            user={
                "email": request.email,
                "username": request.email.split("@")[0],
                "authenticated": True,
            },
        )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication code",
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login and Trigger OTP",
    description="Validates login payload and triggers OTP delivery for the supplied username/email.",
    tags=["authentication"],
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def login(request: LoginRequest) -> LoginResponse:
    try:
        if not request.username or not request.enterprise:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Enterprise and username are required",
            )

        otp = generate_otp()
        email = request.username if "@" in request.username else f"{request.username}@{request.enterprise.lower()}.bank"
        success = send_otp_email(email, otp)
        store_otp(email, otp)

        if success:
            return LoginResponse(
                success=True,
                message="Authentication code sent. Check your email.",
                username=request.username,
                enterprise=request.enterprise,
                email=email,
            )

        return LoginResponse(
            success=True,
            message=f"Auth code: {otp} (email delivery failed)",
            username=request.username,
            enterprise=request.enterprise,
            email=email,
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception("Login flow failed for username=%s", request.username)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed.",
        )
