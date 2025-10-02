import datetime
from typing import Optional, List

from uuid import uuid4, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, func, Index
from . import Base


class User(Base):
    __tablename__ = "user_table"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username: Mapped[Optional[str]] = mapped_column(nullable=True)
    # TODO: verify if email should be nullable - oauth user creating pipeline now assumes nullable=True
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)

    registration_date: Mapped[datetime.datetime] = mapped_column(nullable=False, default=func.now())

    providers: Mapped[List["UserProvider"]] = relationship(back_populates="user", lazy="selectin")

    __table_args__ = (
        Index("user_username_lower_idx", func.lower(username), unique=True),
    )

    def __repr__(self) -> str:
        return f"User(id={self.id})"


class UserProvider(Base):
    __tablename__ = "user_provider_table"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(nullable=False)
    client_id: Mapped[Optional[str]] = mapped_column(nullable=True)
    client_username: Mapped[Optional[str]] = mapped_column(nullable=True)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("user_table.id"), nullable=False)
    user: Mapped["User"] = relationship()

    def __repr__(self) -> str:
        return (f"Provider(id={self.id}, name={self.name},"
                f" client_id={self.client_id}, client_username={self.client_username})")
