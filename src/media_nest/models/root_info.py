from dataclasses import dataclass
from datetime import datetime as Datetime
from pathlib import Path


@dataclass(slots=True)
class RootInfo:
    id: int
    path: Path
    last_sync_at: Datetime
