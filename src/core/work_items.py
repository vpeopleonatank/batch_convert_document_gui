from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

WorkKind = Literal["convert", "copy"]


@dataclass(frozen=True, slots=True)
class WorkItem:
    kind: WorkKind
    source: Path
    dest_file: Path

