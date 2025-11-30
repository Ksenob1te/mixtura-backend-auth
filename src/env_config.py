from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class LocalSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")


class RedisConfig(LocalSettings):
    host: str = Field(default="localhost", alias="REDIS_HOST")
    port: int = Field(default=6379, alias="REDIS_PORT")
    user: str = Field(default="default", alias="REDIS_USER")
    password: str = Field(alias="REDIS_PASSWORD")

    @property
    def url(self) -> str:
        return f"redis://{self.user}:{self.password}@{self.host}:{self.port}"


class SMTPConfig(LocalSettings):
    host: str = Field(default="mail.demogram.ru", alias="SMTP_HOST")
    port: int = Field(default=465, alias="SMTP_PORT")
    user: str = Field(alias="SMTP_USER")
    password: str = Field(alias="SMTP_PASSWORD")
    domain: str = Field(default="demogram.ru", alias="SMTP_DOMAIN")

    @property
    def email(self) -> str:
        return f"{self.user}@{self.domain}"
    
class RabbitConfig(LocalSettings):
    host: str = Field(default="localhost", alias="RABBITMQ_HOST")
    port: int = Field(default=5672, alias="RABBITMQ_PORT")
    user: str = Field(default="guest", alias="RABBITMQ_USER")
    password: str = Field(default="guest", alias="RABBITMQ_PASSWORD")
    vhost: str = Field(default="/", alias="RABBITMQ_VHOST")

    @property
    def url(self) -> str:
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}{self.vhost}"



class PostgresConfig(LocalSettings):
    host: str = Field(default="localhost", alias="POSTGRES_HOST")
    port: int = Field(default=5432, alias="POSTGRES_PORT")
    user: str = Field(default="postgres", alias="POSTGRES_USER")
    password: str = Field(default="pgAdminPassword", alias="POSTGRES_PASSWORD")
    db: str = Field(default="mixtura-auth", alias="POSTGRES_DB")

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


class ServerConfig(LocalSettings):
    proxy: str | None = Field(default=None, alias="SERVER_PROXY")


class Env(LocalSettings):
    postgres: PostgresConfig = Field(default_factory=PostgresConfig)    # type: ignore
    server: ServerConfig = Field(default_factory=ServerConfig)          # type: ignore
    smtp: SMTPConfig = Field(default_factory=SMTPConfig)                # type: ignore
    redis: RedisConfig = Field(default_factory=RedisConfig)             # type: ignore
    rabbit: RabbitConfig = Field(default_factory=RabbitConfig)          # type: ignore

    @classmethod
    def load(cls) -> "Env":
        return cls()


env = Env.load()
