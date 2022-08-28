import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional

from yaiba.log.pseudonymizer import Pseudonymizer
from yaiba.log.session_log import Entry, EntryParser
from yaiba.log.types import PseudoUserName, RawEntry, Timestamp, UserName, VRCPlayerId
from yaiba.log.vrc.utils import VRC_REGEX_LOG_PREFIX, create_timestamp_from_match

logger = logging.getLogger(__name__)


@dataclass
class VRCYAIBAPlayerPositionVersionEntry(Entry):
    timestamp: Timestamp

    major: int
    minor: int
    patch: int

    def to_tuple(self):
        return (
            self.major,
            self.minor,
            self.patch,
        )

    @classmethod
    def type_id(cls):
        return 'yaiba/player_position/version'

    @classmethod
    def from_json(cls, value: Dict[str, Any]) -> Entry:
        return cls(
            timestamp=Timestamp.from_json(value.get('timestamp')),
            major=value.get('major'),
            minor=value.get('minor'),
            patch=value.get('patch'),
        )


@dataclass
class VRCYAIBAPlayerPositionEntry(Entry):
    timestamp: Timestamp
    player_id: VRCPlayerId

    user_name: Optional[UserName]
    pseudo_user_name: PseudoUserName

    location_x: float
    location_y: Optional[float]
    location_z: float  # Can be None for V0 (ScienceAssembly internal version; pre-YAIBA)

    rotation_1: float  # rotation for x axis, pitch in unity
    rotation_2: float  # rotation for y axis, yaw in unity
    rotation_3: float  # rotation for z axis, roll in unity

    is_vr: bool

    @classmethod
    def type_id(cls):
        return 'yaiba/player_position'

    @classmethod
    def from_json(cls, value: Dict[str, Any]) -> Entry:
        return cls(
            timestamp=Timestamp.from_json(value.get('timestamp')),
            player_id=VRCPlayerId(value.get('player_id')),

            user_name=UserName(value.get('user_name')),
            pseudo_user_name=PseudoUserName(value.get('pseudo_user_name')),

            location_x=value.get('location_x'),
            location_y=value.get('location_y'),
            location_z=value.get('location_z'),
            rotation_1=value.get('rotation_1'),
            rotation_2=value.get('rotation_2'),
            rotation_3=value.get('rotation_3'),

            is_vr=value.get('is_vr'),
        )


class YAIBAPlayerPositionEntryParser(EntryParser):
    """
    Note: This parser may not work for some locales that uses a comma as a decimal point. 
    """

    regex_version = re.compile(
        VRC_REGEX_LOG_PREFIX +
        r'\[Player Position Version]\s*(?P<major>\d+).(?P<minor>\d+).(?P<patch>\d+)'
    )

    regex_entry_v0 = re.compile(
        VRC_REGEX_LOG_PREFIX +
        r'\[Player Position](?P<player_id>\d+),"(?P<user_name>.+)",'
        r'(?P<location_x>[^,]*),(?P<location_z>[^,]*),'
        r'(?P<rotation_1>[^,]*),(?P<rotation_2>[^,]*),'
        r'(?P<rotation_3>[^,]*),'
        r'(?P<is_vr>[^,]*)'
    )

    regex_entry_v1_0_0 = re.compile(
        VRC_REGEX_LOG_PREFIX +
        r'\[Player Position](?P<player_id>\d+),"(?P<user_name>.+)",'
        r'(?P<location_x>[^,]*),(?P<location_y>[^,]*),(?P<location_z>[^,]*),'
        r'(?P<rotation_1>[^,]*),(?P<rotation_2>[^,]*),'
        r'(?P<rotation_3>[^,]*),'
        r'(?P<is_vr>[^,]*)'
    )

    def __init__(self, pseudonymizer: Pseudonymizer):
        self.regex_entry_used = self.regex_entry_v0
        self.pseudonymizer = pseudonymizer

    def parse(self, raw_log: RawEntry) -> Optional[Entry]:
        # Tries to parse as a position entry
        # Since position entry appears more frequently than version entry, checks position before version.
        position_entry = self._try_to_parse_entry(raw_log)
        if position_entry is not None:
            return position_entry

        # Tries to parse as a version
        version = self._try_to_parse_version(raw_log)
        if version is not None:
            self.regex_entry_used = self.regex_entry_v1_0_0
            if version.to_tuple() > (1, 0, 0):
                logger.warning(f"unexpected version is applied: {version}. Fallback to latest one")
            return version

    def _try_to_parse_version(self, log_entry: RawEntry) -> Optional[VRCYAIBAPlayerPositionVersionEntry]:
        match = self.regex_version.match(log_entry)
        if match is None:
            return None

        timestamp = create_timestamp_from_match(match)
        major = int(match['major'])
        minor = int(match['minor'])
        patch = int(match['patch'])

        return VRCYAIBAPlayerPositionVersionEntry(
            timestamp=timestamp,
            major=major, minor=minor, patch=patch,
        )

    def _try_to_parse_entry(self, log_entry: RawEntry) -> Optional[VRCYAIBAPlayerPositionEntry]:
        match = self.regex_entry_used.match(log_entry)
        if match is None:
            return None

        timestamp = create_timestamp_from_match(match)
        player_id = VRCPlayerId(match.group('player_id'))

        user_name = match.group('user_name').replace('""', '"')  # Following CSV Escape
        user_name = UserName(user_name)
        p_user_name = self.pseudonymizer.pseudonymize_user_name(user_name)

        location_x = float(match.group('location_x'))
        location_y = match.groupdict().get("location_y", None)  # missing in v0. Return None.
        if location_y is not None:
            location_y = float(location_y)
        location_z = float(match.group('location_z'))
        rotation_1 = float(match.group('rotation_1'))
        rotation_2 = float(match.group('rotation_2'))
        rotation_3 = float(match.group('rotation_3'))
        is_vr = match.group('is_vr').lower() == "true"

        return VRCYAIBAPlayerPositionEntry(
            timestamp=timestamp,
            player_id=player_id,

            user_name=user_name,
            pseudo_user_name=p_user_name,

            location_x=location_x,
            location_y=location_y,
            location_z=location_z,

            rotation_1=rotation_1,
            rotation_2=rotation_2,
            rotation_3=rotation_3,

            is_vr=is_vr,
        )
