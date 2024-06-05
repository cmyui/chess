import json
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class JSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, UUID):
            return str(o)
        return super().default(o)
