from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from ..models import Provider
from typing import List

class ProviderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, provider_id: UUID) -> Provider | None:
        stmt = select(Provider).where(Provider.id == provider_id).limit(1)
        return await self.session.scalar(stmt)

    async def get_by_user_id(self, user_id: UUID) -> List[Provider]:
        stmt = select(Provider).where(Provider.user_id == user_id)
        return list((await self.session.scalars(stmt)).all())

    async def create_provider(self, name: str, client_id: str = None, client_username: str = None, user_id: UUID = None) -> Provider:
        provider = Provider(name=name, client_id=client_id, client_username=client_username, user_id=user_id)
        self.session.add(provider)
        await self.session.flush()
        return await self.get_by_id(provider.id)

    async def get_by_user_and_provider_name(self, user_id: UUID, provider_name: str) -> Provider | None:
        stmt = select(Provider).where(Provider.user_id == user_id, Provider.name == provider_name).limit(1)
        return await self.session.scalar(stmt)
