class DomainException(Exception):
    error_code: str = "domain_error"
    message: str = "Domain error occurred"

    def __init__(self) -> None:
        super().__init__(self.message)


class UserAlreadyExistsException(DomainException):
    error_code = "user_already_exists"
    message = "User with this email already exists"


class UserNotFoundException(DomainException):
    error_code = "user_not_found"
    message = "User not found"


class UserNotActiveException(DomainException):
    error_code = "user_not_active"
    message = "User account is not activated"


class InvalidCredentialsException(DomainException):
    error_code = "invalid_credentials"
    message = "Invalid email or password"


class InvalidVerificationCodeException(DomainException):
    error_code = "invalid_verification_code"
    message = "Invalid or expired verification code"


class TooManyAttemptsException(DomainException):
    error_code = "too_many_attempts"
    message = "Too many failed attempts. Please request a new code"


class InvalidTokenException(DomainException):
    error_code = "invalid_token"
    message = "Invalid or expired token"


class InvalidPasswordException(DomainException):
    error_code = "invalid_password"
    message = "Password does not meet requirements"
