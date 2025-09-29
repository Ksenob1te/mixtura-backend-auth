from src.env_config import env
from typing import Optional
from datetime import timedelta
from uuid import UUID
import aiosmtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr


class SMTPRepository:
    source_email = env.smtp.email

    def __init__(self, smtp: aiosmtplib.SMTP):
        self.smtp = smtp

    @staticmethod
    async def _get_body(code: str) -> str:
        with open("assets/smtp/transactional.html", "r") as f:
            body_text = f.read()
        return body_text.replace("{{code}}", code)

    async def send_code(self, to_email: str, code: str) -> None:
        body_html = await self._get_body(code)
        msg = MIMEText(body_html, 'html', 'utf-8')
        msg["From"] = formataddr(("Mixtura", self.source_email))
        msg['To'] = to_email
        msg['Subject'] = Header("Mixtura Verification Code", 'utf-8')
        await self.smtp.sendmail(self.source_email, to_email, msg.as_string())
