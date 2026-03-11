from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ---- Request schemas ----

class RegisterRequest(BaseModel):
    email: EmailStr = Field(examples=["user@example.com"])
    password: str = Field(min_length=8, examples=["Password123"])
    name: str = Field(min_length=1, max_length=255, examples=["John"])


class VerifyCodeRequest(BaseModel):
    email: EmailStr = Field(examples=["user@example.com"])
    code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$", examples=["123456"])


class LoginRequest(BaseModel):
    email: EmailStr = Field(examples=["user@example.com"])
    password: str = Field(examples=["Password123"])


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."])


class LogoutRequest(BaseModel):
    refresh_token: str = Field(examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."])


class ResendCodeRequest(BaseModel):
    email: EmailStr = Field(examples=["user@example.com"])
    purpose: str = Field(pattern=r"^(registration|login)$", examples=["registration"])


class PasswordResetRequest(BaseModel):
    email: EmailStr = Field(examples=["user@example.com"])


class PasswordResetConfirmRequest(BaseModel):
    email: EmailStr = Field(examples=["user@example.com"])
    code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$", examples=["123456"])
    new_password: str = Field(min_length=8, examples=["NewPassword123"])


# ---- Response schemas ----

class MessageResponse(BaseModel):
    message: str = Field(examples=["verification code sent"])


class TokenPairResponse(BaseModel):
    access_token: str = Field(examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."])
    refresh_token: str = Field(examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."])


class AccessTokenResponse(BaseModel):
    access_token: str = Field(examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."])


class UserResponse(BaseModel):
    id: UUID = Field(examples=["123e4567-e89b-12d3-a456-426614174000"])
    email: str = Field(examples=["user@example.com"])
    name: str = Field(examples=["John"])
    created_at: datetime = Field(examples=["2026-01-01T10:00:00"])


class ErrorResponse(BaseModel):
    error: str = Field(examples=["invalid_credentials"])
    message: str = Field(examples=["Invalid email or password"])
