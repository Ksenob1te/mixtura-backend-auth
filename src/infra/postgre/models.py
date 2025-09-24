from typing import Optional

from uuid import uuid4, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime, func
from . import Base

class User(Base):
    __tablename__ = "user_table"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username: Mapped[Optional[str]] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)

    registration_date: Mapped[DateTime] = mapped_column(nullable=False, default=func.now())

    providers: Mapped[list["Provider"]] = relationship(backref="user", lazy="selectin")

    def __repr__(self) -> str:
        return f"User(id={self.id})"

class Provider(Base):
    __tablename__ = "provider_table"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(nullable=False)
    client_id: Mapped[Optional[str]] = mapped_column(nullable=True)
    client_username: Mapped[Optional[str]] = mapped_column(nullable=True)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("user_table.id"), nullable=False)
    user: Mapped["User"] = relationship()

    def __repr__(self) -> str:
        return (f"Provider(id={self.id}, name={self.name},"
                f" client_id={self.client_id}, client_username={self.client_username})")
