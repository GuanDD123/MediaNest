from dataclasses import dataclass
from datetime import datetime as Datetime
from pathlib import Path

__all__ = ("RootInfo",)


@dataclass(slots=True)
class RootInfo:
    id: int
    path: Path
    last_sync_time: Datetime
