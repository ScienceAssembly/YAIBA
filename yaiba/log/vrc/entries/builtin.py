from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Optional

from yaiba.log.pseudonymizer import Pseudonymizer
from yaiba.log.session_log import Entry, EntryParser
from yaiba.log.types import PseudoUserName, RawEntry, Timestamp, UserName
from yaiba.log.vrc.utils import VRC_REGEX_LOG_PREFIX, create_timestamp_from_match


@dataclass(frozen=True)
class VRCEnteringRoomEntry(Entry):
    timestamp: Timestamp
    room_name: str

    @classmethod
    def type_id(cls):
        return 'vrc/entering_room'

    @classmethod
    def from_json(cls, value: Dict[str, Any]) -> Entry:
        return cls(
            timestamp=Timestamp.from_json(value.get('timestamp')),
            room_name=value.get('room_name')
        )


@dataclass(frozen=True)
class VRCPlayerJoinEntry(Entry):
    timestamp: Timestamp
    user_name: Optional[UserName]
    pseudo_user_name: PseudoUserName

    @classmethod
    def type_id(cls):
        return 'vrc/player_join'

    @classmethod
    def from_json(cls, value: Dict[str, Any]) -> Entry:
        return cls(
            timestamp=Timestamp.from_json(value.get('timestamp')),
            user_name=value.get('user_name'),
            pseudo_user_name=value.get('pseudo_user_name'),
        )


@dataclass(frozen=True)
class VRCPlayerLeftEntry(Entry):
    timestamp: Timestamp
    user_name: Optional[UserName]
    pseudo_user_name: PseudoUserName

    @classmethod
    def type_id(cls):
        return 'vrc/player_left'

    @classmethod
    def from_json(cls, value: Dict[str, Any]) -> Entry:
        return cls(
            timestamp=Timestamp.from_json(value.get('timestamp')),
            user_name=value.get('user_name'),
            pseudo_user_name=value.get('pseudo_user_name'),
        )


class VRCBuiltinEntryParser(EntryParser):
    regex_entering_room: ClassVar[re.Pattern] = re.compile(
        VRC_REGEX_LOG_PREFIX +
        r'\[Behaviour] Entering Room: (?P<room_name>.+)$'
    )
    regex_player_join: ClassVar[re.Pattern] = re.compile(
        VRC_REGEX_LOG_PREFIX +
        r'\[Behaviour] OnPlayerJoined (?P<user_name>.+)$'
    )
    regex_player_left: ClassVar[re.Pattern] = re.compile(
        VRC_REGEX_LOG_PREFIX +
        r'\[Behaviour] OnPlayerLeft (?P<user_name>.+)$'
    )

    def __init__(self, pseudonymizer: Pseudonymizer):
        self.pseudonymizer = pseudonymizer

    def parse(self, log_entry: RawEntry) -> Optional[Entry]:
        for func in [
            self._try_to_parse_entering_room,
            self._try_to_parse_player_join,
            self._try_to_parse_player_left,
        ]:
            value: Optional[Entry] = func(log_entry)
            if value is not None:
                return value
        return None

    def _try_to_parse_entering_room(self, log_entry: RawEntry) -> Optional[VRCEnteringRoomEntry]:
        match = self.regex_entering_room.match(log_entry)
        if match is None:
            return None
        return VRCEnteringRoomEntry(
            timestamp=create_timestamp_from_match(match),
            room_name=match.group('room_name'),
        )

    def _try_to_parse_player_join(self, log_entry: RawEntry) -> Optional[VRCPlayerJoinEntry]:
        match = self.regex_player_join.match(log_entry)
        if match is None:
            return None
        user_name = UserName(match.group("user_name"))
        return VRCPlayerJoinEntry(
            timestamp=create_timestamp_from_match(match),
            user_name=user_name,
            pseudo_user_name=self.pseudonymizer.pseudonymize_user_name(user_name),
        )

    def _try_to_parse_player_left(self, log_entry: RawEntry) -> Optional[VRCPlayerLeftEntry]:
        match = self.regex_player_left.match(log_entry)
        if match is None:
            return None
        user_name = UserName(match.group("user_name"))
        return VRCPlayerLeftEntry(
            timestamp=create_timestamp_from_match(match),
            user_name=user_name,
            pseudo_user_name=self.pseudonymizer.pseudonymize_user_name(user_name),
        )
