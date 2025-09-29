import contextlib
from typing import AsyncIterator
import aiosmtplib


class SMTPManager:
    def __init__(self, host, port, user, password):
        self._host = host
        self._port = port
        self._user = user
        self._password = password

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
