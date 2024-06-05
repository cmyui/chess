from uuid import UUID
from fastapi import APIRouter, Response, Depends
from pydantic import BaseModel

from app import security
from app.context import APIRequestContext
from app.repositories import accounts
from app.api import responses

router = APIRouter()


class CreateAccountRequestV1(BaseModel):
    username: str
    password: str


class CreateAccountResponseV1(BaseModel):
    user_id: UUID


class ErrorResponseV1(BaseModel):
    user_feedback: str


@router.post("/api/v1/accounts")
async def create_account(
    request: CreateAccountRequestV1,
    context: APIRequestContext = Depends(),
) -> Response:
    account = await accounts.get_account_by_username(context, request.username)
    if account is not None:
        return responses.failure(
            user_feedback="Username already exists",
            status_code=400,
        )

    # TODO: minimum password requirements

    hashed_password = security.hash_password(request.password)
    account = await accounts.create_account(context, request.username, hashed_password)

    response = CreateAccountResponseV1(user_id=account.user_id)
    access_token = security.create_access_token(account.user_id)
    return responses.success(
        content=response,
        cookies=[
            responses.Cookie(
                key="access_token",
                value=access_token,
                expires=60 * 60,
                secure=True,
                httponly=True,
                samesite="strict",
            )
        ],
    )
