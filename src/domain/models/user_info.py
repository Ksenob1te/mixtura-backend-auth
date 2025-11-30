from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AuthCheckResponse(BaseModel):
    user_id: Optional[UUID]


class ProviderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    client_id: Optional[str]
    client_username: Optional[str]


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: Optional[str]
    email: Optional[str]
    registration_date: datetime
    providers: List[ProviderResponse]
