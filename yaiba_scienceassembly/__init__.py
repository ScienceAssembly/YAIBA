from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from yaiba.log.types import FromJson


@dataclass
class ScienceAssemblyMetadata(FromJson):
    """
    For `SessionLog.metadata`
    """
    event_type: str  # Ex. "理系集会"
    event_date: str  # Ex. "2022-04-29"
    event_description: str  # Ex. "水の汚れを測る方法"
    event_instance: str  # "main", "sub", "petit"

    @classmethod
    def from_json(cls, value: Dict[str, Any]) -> ScienceAssemblyMetadata:
        return cls(**value)
