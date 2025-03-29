from __future__ import annotations

import io
import re
import typing
from dataclasses import dataclass, field
from typing import List, Optional

from yaiba.log.pseudonymizer import Pseudonymizer
from yaiba.log.session_log import Entry, EntryParser, SessionLog
from yaiba.log.types import RawEntry
from yaiba.log.vrc.entries.builtin import VRCBuiltinEntryParser
from yaiba.log.vrc.entries.player_position import YAIBAPlayerPositionEntryParser
from yaiba.log.vrc.entries.questionnaire import YAIBAQuestionnaireAnswerEntryParser
from yaiba.log.vrc.entries.yodokoro_tag_marker import TAG_NAMES_USED_IN_SCIENCE_ASSEMBLY, YodokoroTagMarkerEntryParser


class VRCLogParser:
    """
    Note: Assumes two empty lines between log entries.
    """

    @dataclass
    class Config:
        """
        Yodokoro tag names. The order must be the same as the one specified in Unity.

        This field is ignored when parser_list is not none. 
        """
        yodokoro_tag_marker_names: List[str] = field(
            default_factory=lambda: TAG_NAMES_USED_IN_SCIENCE_ASSEMBLY,
        )
        pseudonymizer: Pseudonymizer = field(
            default_factory=lambda: Pseudonymizer.new_random(),
        )

        """
        The list of parsers. Should be ordered by the frequency of its entry for better performance.

        If None, default parsers are used.
        """
        parsers: Optional[List[EntryParser]] = field(default=None)

        @classmethod
        def default(cls) -> VRCLogParser.Config:
            return VRCLogParser.Config()

    def __init__(
            self,
            config: Optional[Config] = None,
    ):
        if config is None:
            config = VRCLogParser.Config.default()
        if config.parsers is not None:
            self.parsers = config.parsers
            return
        else:
            self.parsers = self._create_default_parsers(config)

    @classmethod
    def _create_default_parsers(cls, config: Config):
        return [
            YAIBAPlayerPositionEntryParser(config.pseudonymizer),
            YodokoroTagMarkerEntryParser(config.yodokoro_tag_marker_names),
            VRCBuiltinEntryParser(config.pseudonymizer),
            YAIBAQuestionnaireAnswerEntryParser(),
        ]

    def parse(self, value: str) -> SessionLog:
        return self.parse_file(io.StringIO(value))

    def parse_file(self, fp: typing.TextIO) -> SessionLog:
        log_entries: List[Entry] = []
        for raw_entry_str in _iter_per_vrc_log_entry(fp):
            entry = self._parse_one_entry(RawEntry(raw_entry_str))
            if entry is not None:
                log_entries.append(entry)
        return SessionLog(log_entries)

    def _parse_one_entry(self, raw_entry: RawEntry) -> Optional[Entry]:
        for parser in self.parsers:
            entry = parser.parse(raw_entry)
            if entry is not None:
                return entry
        return None


def _iter_per_vrc_log_entry(fp: typing.TextIO):
    """
    VRC log entries are separated by two empty lines.
    
    Note: VRC log entry may contain "\r", and the number of empty lines between entries can be more than three.
    
    :param fp: 
    :type fp: 
    :return: 
    :rtype: 
    """
    return filter(lambda line: len(line) > 0, _iter_per_timestamp_line(fp))


VRC_TIMESTAMP_REGEX = re.compile(r"\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2} Log.*")


def _iter_per_timestamp_line(fp: typing.TextIO):
    log_entry_lines = []
    count_empty_lines = 0
    while True:
        line = fp.readline()
        if VRC_TIMESTAMP_REGEX.match(line):
            if len(log_entry_lines) > 0:
                yield '\n'.join(log_entry_lines).strip('\n')
            log_entry_lines = []
        log_entry_lines.append(line)
        if line == '':
            count_empty_lines += 1
        if count_empty_lines >= 100:
            break
    yield '\n'.join(log_entry_lines).strip('\n')
