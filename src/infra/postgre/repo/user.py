from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from ..models import User
import bcrypt


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    async def _hash_password(password: str):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    async def check_password(user: User, password: str) -> bool:
        return bcrypt.checkpw(password.encode(), user.hashed_password.encode())

    async def get_by_id(self, user_id: UUID) -> User | None:
        stmt = select(User).where(User.id == user_id).limit(1)
        return await self.session.scalar(stmt)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email).limit(1)
        return await self.session.scalar(stmt)

    async def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username).limit(1)
        return await self.session.scalar(stmt)

    async def create_user(self, username: str, email: str, password: str) -> User:
        user = User(username=username, email=email, hashed_password=await self._hash_password(password))
        self.session.add(user)
        await self.session.flush()
        return await self.get_by_id(user.id)

    async def change_username(self, user_id: UUID, new_username: str) -> bool:
        stmt = update(User).where(User.id == user_id).values(username=new_username)
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount == 1

    async def change_password(self, user_id: UUID, new_password: str) -> bool:
        stmt = update(User).where(User.id == user_id).values(hashed_password=await self._hash_password(new_password))
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount == 1



