from uuid import uuid4

from pydantic import BaseModel, Field


class Identity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str


class IdentityManager:
    _identities: Dict[str, Identity] = {}

    @classmethod
    def create_identity(cls, name: str) -> Identity:
        identity = Identity(name=name)
        cls._identities[identity.id] = identity
        return identity

    @classmethod
    def get_identity_by_id(cls, identity_id: str) -> Identity:
        return cls._identities.get(identity_id)

    @classmethod
    def get_all_identities(cls) -> Dict[str, Identity]:
        return cls._identities.copy()
