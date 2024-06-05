from uuid import UUID
from fastapi import Request
from pydantic import BaseModel

from app import security


class IdentityContext(BaseModel):
    user_id: UUID


def authenticate_user(request: Request) -> IdentityContext | None:
    access_token = request.cookies.get("access_token")
    if access_token is None:
        return None

    claims = security.decode_access_token(access_token)

    user_id = UUID(claims[security.CustomTokenClaims.USER_ID])

    return IdentityContext(user_id=user_id)
