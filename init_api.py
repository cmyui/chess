#!/usr/bin/env python3
from contextlib import asynccontextmanager
from typing import AsyncIterator
from fastapi import FastAPI
from app import settings
from app.api.v1 import v1_router
import redis.asyncio as aioredis


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    print("Application starting up")
    app.state._redis_connection = aioredis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=0,
    )
    await app.state._redis_connection.initialize()
    yield
    print("Application shutting down")
    await app.state._redis_connection.aclose()


app = FastAPI(lifespan=lifespan)

app.include_router(v1_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("init_api:app", reload=True)
