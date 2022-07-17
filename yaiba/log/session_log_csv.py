import csv
import dataclasses
import io
from dataclasses import is_dataclass, dataclass
from typing import TextIO, Type

from yaiba.log import Entry, SessionLog
from yaiba.log.types import PseudoUserName, Timestamp, UserName, VRCPlayerId


class CsvEncoder:

    @dataclass
    class Options:
        encode_timestamp: bool = True
        encode_pseudo_user_name: bool = True
        encode_vrc_player_id: bool = True
        encode_user_name: bool = False

        @classmethod
        def default(cls):
            return cls()

        @classmethod
        def export_all(cls):
            return cls(
                encode_user_name=True,
                encode_pseudo_user_name=True,
                encode_timestamp=True,
                encode_vrc_player_id=True,
            )

    def __init__(self, entry_class: Type[Entry], options: Options = None):
        self.entry_class = entry_class
        if options is None:
            options = CsvEncoder.Options.default()
        self.options = options

    def encode(self, session_log: SessionLog) -> str:
        fp = io.StringIO()
        self.write(session_log, fp)
        return fp.getvalue()

    def write(self, session_log: SessionLog, fp: TextIO):
        assert is_dataclass(self.entry_class)
        fields = dataclasses.fields(self.entry_class)
        field_names = [
            f.name for f in fields
            if self._is_ok_to_encode(f.type)
        ]

        writer = csv.DictWriter(fp, fieldnames=field_names, extrasaction="ignore")

        writer.writeheader()
        for entry in session_log.log_entries:
            if not isinstance(entry, self.entry_class):
                continue
            writer.writerow(dataclasses.asdict(entry))

    def _is_ok_to_encode(self, v_type):
        if isinstance(v_type, Timestamp):
            return self.options.encode_timestamp
        if isinstance(v_type, PseudoUserName):
            return self.options.encode_pseudo_user_name
        if isinstance(v_type, UserName):
            return self.options.encode_user_name
        if isinstance(v_type, VRCPlayerId):
            return self.options.encode_vrc_player_id
        return True