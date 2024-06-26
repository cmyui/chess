from __future__ import annotations

import json
from typing import Any
from uuid import UUID


class JSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, UUID):
            return str(o)
        return super().default(o)
