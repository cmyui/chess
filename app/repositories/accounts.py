#!/usr/bin/env python3

from uuid import UUID, uuid4
from pydantic import BaseModel

from app.context import AbstractContext


class Account(BaseModel):
    user_id: UUID
    username: str
    hashed_password: bytes


async def create_account(
    context: AbstractContext,
    username: str,
    hashed_password: bytes,
) -> Account:
    account = Account(
        user_id=uuid4(),
        username=username,
        hashed_password=hashed_password,
    )
    await context.redis_connection.set(
        f"account:{account.user_id}",
        account.model_dump_json(),
    )
    return account


async def get_account_by_id(
    context: AbstractContext,
    user_id: UUID,
) -> Account | None:
    account_data: bytes | None = await context.redis_connection.get(
        f"account:{user_id}"
    )
    if account_data is None:
        return None
    return Account.model_validate_json(account_data)


async def get_account_by_username(
    context: AbstractContext, username: str
) -> Account | None:
    account_data: bytes | None = await context.redis_connection.get(
        f"account:{username}"
    )
    if account_data is None:
        return None
    return Account.model_validate_json(account_data)
