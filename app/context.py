from abc import ABC

from fastapi import Request
import redis.asyncio as aioredis


class AbstractContext(ABC):
    redis_connection: aioredis.Redis


class APIRequestContext(AbstractContext):
    def __init__(self, request: Request):
        self.redis_connection = request.app.state._redis_connection
