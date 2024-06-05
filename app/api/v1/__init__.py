from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.accounts import router as accounts_router
from app.api.v1.authentication import router as authentication_router
from app.api.v1.chess import router as chess_router

v1_router = APIRouter()

v1_router.include_router(chess_router)
v1_router.include_router(authentication_router)
v1_router.include_router(accounts_router)
