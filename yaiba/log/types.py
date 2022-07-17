from __future__ import annotations

import datetime
from abc import ABC, abstractmethod
from typing import Any, Dict, TypeVar


class FromJson(ABC):
    @classmethod
    @abstractmethod
    def from_json(cls, value: Dict[str, Any]) -> T:
        pass


class Timestamp(datetime.datetime, FromJson):
    @classmethod
    def from_json(cls, timestamp):
        return cls.fromtimestamp(timestamp)


class UserName(str):
    pass


class PseudoUserName(str):
    """
    Pseudonymized user name.
    """
    pass


class VRCPlayerId(int):
    """
    World internal player id.
    https://docs.vrchat.com/docs/getting-players#getplayerbyid
    """
    pass


class RawEntry(str):
    """
    One log entry which is not parsed yet.
    
    Ex. VRChat:`2022.03.04 21:50:19 Log        -  [Behaviour] EnteringRoom: Some Room`
    """
    pass


T = TypeVar("T")
