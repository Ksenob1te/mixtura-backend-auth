import contextlib
from typing import AsyncIterator
import aiosmtplib
from email.mime.text import MIMEText
from email.header import Header
from src.env_config import env


class SMTPManager:
    def __init__(self):
        self._host = env.smtp.host
        self._port = env.smtp.port
        self._user = env.smtp.user
        self._password = env.smtp.password

    @contextlib.asynccontextmanager
    async def client(self) -> AsyncIterator[aiosmtplib.SMTP]:
        server = aiosmtplib.SMTP(
            hostname=self._host,
            port=self._port,
            use_tls=True
        )
        try:
            await server.connect()
            await server.login(self._user, self._password)
            yield server
        finally:
            if server.is_connected:
                await server.quit()
