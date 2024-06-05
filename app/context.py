from __future__ import annotations

from abc import ABC

import redis.asyncio as aioredis
from fastapi import Request


class AbstractContext(ABC):
    redis_connection: aioredis.Redis


class APIRequestContext(AbstractContext):
    def __init__(self, request: Request):
        self.redis_connection = request.app.state._redis_connection
