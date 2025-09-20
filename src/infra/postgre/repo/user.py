from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from ..models import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: UUID) -> User | None:
        stmt = select(User).where(User.id == user_id).limit(1)
        return await self.session.scalar(stmt)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email).limit(1)
        return await self.session.scalar(stmt)

    async def create_user(self, email: str, hashed_password: str) -> User:
        user = User(email=email, hashed_password=hashed_password)
        self.session.add(user)
        await self.session.flush()
        return await self.get_by_id(user.id)
