"""
Parse log entries outputted by "ヨドコロちゃんのタグマーカー" (https://booth.pm/ja/items/3109716).

See https://booth.pm/ja/items/3109716 for detailed format of the log entry. 
"""

import itertools
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from yaiba.log.session_log import Entry, EntryParser
from yaiba.log.types import RawEntry, Timestamp, VRCPlayerId
from yaiba.log.vrc.utils import VRC_REGEX_LOG_PREFIX, create_timestamp_from_match

TAG_NAMES_USED_IN_SCIENCE_ASSEMBLY = [
    "機械工学",
    "電気系工学",
    "物理工学",
    "物理学",
    "化学",
    "生物学",
    "天文学",
    "数学",
    "農学",
    "環境学",
    "薬学",
    "情報学",
    "医学",
    "土木工学",
    "地学",
    "製造学",
    "文系",
    "その他",
    "初めて来ました",
    "聞きたい",
    "話したい",
    "議論したい",
]


@dataclass
class VRCYodokoroTagMarkerEntry(Entry):
    timestamp: Timestamp
    tag_names_for_player_id: Dict[VRCPlayerId, List[str]]

    @classmethod
    def type_id(cls):
        return 'yodokoro/tag_marker'

    @classmethod
    def from_json(cls, value: Dict[str, Any]) -> Entry:
        tag_names_for_player_id = value.get('tag_names_for_player_id')
        if isinstance(tag_names_for_player_id, dict):
            tag_names_for_player_id = {
                VRCPlayerId(k): v
                for k, v in
                tag_names_for_player_id.items()
            }
        return cls(
            timestamp=Timestamp.from_json(value.get('timestamp')),
            tag_names_for_player_id=tag_names_for_player_id,
        )


class YodokoroTagMarkerEntryParser(EntryParser):
    """
    See https://booth.pm/ja/items/3109716 for detailed format of the log entry.
    """

    regex_pattern = re.compile(
        VRC_REGEX_LOG_PREFIX +
        r'\[Yodo]\[Dump](?P<tags_for_all_players>.+)'
    )

    regex_one_tag = re.compile(r'\[(?P<index>\d+),(?P<player_id>\d+),(?P<tags_hex>\d+)],')

    def __init__(self, tag_names: List[str]):
        self.tag_names = tag_names

    def parse(self, raw_log: RawEntry) -> Optional[Entry]:
        match = self.regex_pattern.match(raw_log)
        if match is None:
            return None

        timestamp = create_timestamp_from_match(match)
        tag_names_for_player_id = self._parse_tags_for_all_players(match.group("tags_for_all_players"))

        return VRCYodokoroTagMarkerEntry(
            timestamp=timestamp,
            tag_names_for_player_id=tag_names_for_player_id,
        )

    def _parse_tags_for_all_players(self, value: str) -> Dict[VRCPlayerId, List[str]]:
        """
        :param value: Ex. "[0,00000030],[1,00000030],[2,00000030],...[81,00000030]," 
        :return: parsed value.
        """
        tags_for_player_id = {}
        for match in self.regex_one_tag.finditer(value):
            player_id = VRCPlayerId(match.group('player_id'))
            if player_id == -1:
                continue
            tags = self._parse_tags(match.group('tags_hex'))
            tags_for_player_id[player_id] = tags
        return tags_for_player_id

    def _parse_tags(self, tags_hex: str) -> List[str]:
        tags_bin = bin(int(tags_hex, 16))[2:]  # to drop "0b"
        return [
            tag_name
            for tag_name, has_tag in itertools.zip_longest(self.tag_names, reversed(tags_bin))
            if has_tag == '1'
        ]
