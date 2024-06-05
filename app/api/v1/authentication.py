from fastapi import APIRouter, Response
from pydantic import BaseModel

from app import security
from app.repositories import accounts
from app.api import responses

router = APIRouter()


class AuthenticateRequestV1(BaseModel):
    username: str
    password: str


class AuthenticateResponseV1(BaseModel): ...


class ErrorResponseV1(BaseModel):
    user_feedback: str



@router.post("/api/v1/authenticate")
async def authenticate(request: AuthenticateRequestV1) -> Response:
    account = accounts.get_account_by_username(request.username)
    if account is None:
        return responses.failure(
            user_feedback="Invalid username or password",
            status_code=401,
        )

    if not security.check_password(request.password, account.hashed_password):
        return responses.failure(
            user_feedback="Invalid username or password",
            status_code=401,
        )

    response = AuthenticateResponseV1()
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
