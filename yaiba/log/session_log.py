from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from yaiba.log.types import FromJson, RawEntry


@dataclass(repr=False)
class SessionLog:
    log_entries: List[Entry]
    metadata: Optional[Any] = field(default=None)

    def __repr__(self):
        return f'SessionLog(log_entries=[{len(self.log_entries)} entries], metadata={self.metadata!r})'


class Entry(FromJson, ABC):
    """
    Base class of all log entry.
    
    Subclass must be a dataclass.
    """

    @classmethod
    @abstractmethod
    def type_id(cls):
        pass

    @classmethod
    @abstractmethod
    def from_json(cls, value: Dict[str, Any]) -> Entry:
        """
        Note: Should use `value.get(name)` rather than `value[name]`. To avoid key value exception.
        """
        pass


class EntryParser(ABC):
    @abstractmethod
    def parse(self, raw_log: RawEntry) -> Optional[Entry]:
        pass
