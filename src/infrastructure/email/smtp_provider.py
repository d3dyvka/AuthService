import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from src.application.ports import EmailProvider
from src.infrastructure.config import get_settings

logger = logging.getLogger(__name__)

PURPOSE_SUBJECTS = {
    "registration": "Email Verification Code",
    "login": "Login Verification Code",
    "password_reset": "Password Reset Code",
}


class SMTPEmailProvider(EmailProvider):
    def __init__(self) -> None:
        self._settings = get_settings()

    async def _send(self, to: str, subject: str, body: str) -> None:
        msg = MIMEMultipart("alternative")
        msg["From"] = self._settings.smtp_from
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        try:
            await aiosmtplib.send(
                msg,
                hostname=self._settings.smtp_host,
                port=self._settings.smtp_port,
                username=self._settings.smtp_user,
                password=self._settings.smtp_password,
                start_tls=True,
            )
            logger.info("Email sent to %s subject='%s'", to, subject)
        except Exception:
            logger.exception("Failed to send email to %s", to)
            raise

    async def send_verification_code(self, to_email: str, code: str, purpose: str) -> None:
        subject = PURPOSE_SUBJECTS.get(purpose, "Verification Code")
        body = f"""
        <html><body>
        <h2>{subject}</h2>
        <p>Your verification code:</p>
        <h1 style="letter-spacing:8px;font-family:monospace;">{code}</h1>
        <p>This code expires in <strong>10 minutes</strong>.</p>
        <p>If you did not request this, please ignore this email.</p>
        </body></html>
        """
        logger.info("Sending verification code email for purpose=%s to %s", purpose, to_email)
        await self._send(to_email, subject, body)

    async def send_password_reset_code(self, to_email: str, code: str) -> None:
        subject = "Password Reset Code"
        body = f"""
        <html><body>
        <h2>Password Reset</h2>
        <p>Your password reset code:</p>
        <h1 style="letter-spacing:8px;font-family:monospace;">{code}</h1>
        <p>This code expires in <strong>10 minutes</strong>.</p>
        <p>If you did not request a password reset, please ignore this email.</p>
        </body></html>
        """
        logger.info("Sending password reset email to %s", to_email)
        await self._send(to_email, subject, body)
