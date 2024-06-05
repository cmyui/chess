from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import datetime
from typing import Any
from typing import Literal

from fastapi import BackgroundTasks
from fastapi import Response
from pydantic import BaseModel

from app.json import JSONEncoder


class JSONResponse(Response):
    media_type = "application/json"

    def __init__(
        self,
        content: Any,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTasks | None = None,
    ) -> None:
        super().__init__(content, status_code, headers, media_type, background)

    def render(self, content: Any) -> bytes:
        if isinstance(content, str):
            return content.encode("utf-8")
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            cls=JSONEncoder,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")


class Cookie(BaseModel):
    key: str
    value: str = ""
    max_age: int | None = None
    expires: datetime | str | int | None = None
    path: str = "/"
    domain: str | None = None
    secure: bool = False
    httponly: bool = False
    samesite: Literal["lax", "strict", "none"] | None = "lax"


def success(
    *,
    content: BaseModel,
    status_code: int = 200,
    cookies: list[Cookie] | None = None,
) -> JSONResponse:
    http_response = JSONResponse(
        content=content.model_dump_json(),
        status_code=status_code,
    )
    for cookie in cookies or []:
        http_response.set_cookie(
            key=cookie.key,
            value=cookie.value,
            max_age=cookie.max_age,
            expires=cookie.expires,
            path=cookie.path,
            domain=cookie.domain,
            secure=cookie.secure,
            httponly=cookie.httponly,
            samesite=cookie.samesite,
        )
    return http_response


def failure(
    *,
    user_feedback: str,
    status_code: int = 400,
    cookies: list[Cookie] | None = None,
) -> JSONResponse:
    http_response = JSONResponse(
        {"user_feedback": user_feedback},
        status_code=status_code,
    )
    for cookie in cookies or []:
        http_response.set_cookie(
            key=cookie.key,
            value=cookie.value,
            max_age=cookie.max_age,
            expires=cookie.expires,
            path=cookie.path,
            domain=cookie.domain,
            secure=cookie.secure,
            httponly=cookie.httponly,
            samesite=cookie.samesite,
        )
    return http_response
