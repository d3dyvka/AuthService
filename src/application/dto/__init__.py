from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass
class RegisterDTO:
    email: str
    password: str
    name: str


@dataclass
class VerifyRegistrationDTO:
    email: str
    code: str


@dataclass
class LoginDTO:
    email: str
    password: str


@dataclass
class VerifyLoginDTO:
    email: str
    code: str


@dataclass
class RefreshTokenDTO:
    refresh_token: str


@dataclass
class LogoutDTO:
    refresh_token: str


@dataclass
class PasswordResetRequestDTO:
    email: str


@dataclass
class PasswordResetConfirmDTO:
    email: str
    code: str
    new_password: str

@dataclass
class TokenPairDTO:
    access_token: str
    refresh_token: str


@dataclass
class AccessTokenDTO:
    access_token: str


@dataclass
class UserDTO:
    id: UUID
    email: str
    name: str
    created_at: datetime
