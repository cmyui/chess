from __future__ import annotations

from enum import StrEnum
from typing import Any
from uuid import UUID

import bcrypt
import jwt

from app import settings
from app.json import JSONEncoder


class CustomTokenClaims(StrEnum):
    USER_ID = "custom:user_id"


def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


def check_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed)


def create_access_token(user_id: UUID) -> str:
    return jwt.encode(
        {CustomTokenClaims.USER_ID: user_id},
        settings.JWT_PRIVATE_KEY,
        algorithm="HS256",
        json_encoder=JSONEncoder,
    )


def decode_access_token(access_token: str) -> dict[Any, Any]:
    payload = jwt.decode(
        access_token,
        settings.JWT_PRIVATE_KEY,
        algorithms=["HS256"],
    )
    if not isinstance(payload, dict):
        raise ValueError("Invalid JWT payload structure")
    return payload
