from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass
from typing import Any, Dict, Optional, Type

from yaiba.log.entries import ALL_ENTRIES
from yaiba.log.session_log import Entry, SessionLog
from yaiba.log.types import FromJson, PseudoUserName, Timestamp, UserName, VRCPlayerId

ENTRY_TYPE_ID_ATTR_NAME = "type_id"


class JsonEncoder:
    """
    Json serializer. 
    """

    @dataclass
    class Options:
        output_timestamp: bool = True
        output_pseudo_user_name: bool = True
        output_vrc_player_id: bool = True
        output_user_name: bool = True

        @classmethod
        def default(cls):
            return cls()

        @classmethod
        def export_all(cls):
            return cls(
                output_timestamp=True,
                output_pseudo_user_name=True,
                output_vrc_player_id=True,
                output_user_name=True,
            )

        @classmethod
        def pseudonymized(cls):
            return cls(
                output_timestamp=True,
                output_pseudo_user_name=True,
                output_vrc_player_id=True,
                output_user_name=False,
            )

    def __init__(self, options: Optional[Options] = None):
        if options is None:
            options = JsonEncoder.Options.default()
        self.options = options

    def encode(self, session_log: SessionLog):
        encoder = json.JSONEncoder(
            default=self._encoder_default,
        )
        return encoder.encode(session_log)

    def _encoder_default(self, o):
        if isinstance(o, SessionLog):
            return self._dataclasses_shadow_asdict(o)
        if isinstance(o, Entry):
            if dataclasses.is_dataclass(o):
                values = self._make_safe_to_store(self._dataclasses_shadow_asdict(o))
                values[ENTRY_TYPE_ID_ATTR_NAME] = o.type_id()
                return values
        if isinstance(o, Timestamp):
            return o.timestamp()
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)

    @staticmethod
    def _dataclasses_shadow_asdict(o):
        return {
            field.name: getattr(o, field.name)
            for field in dataclasses.fields(o)
        }

    def _make_safe_to_store(self, o: Dict[str, Any]) -> Dict[str, Any]:
        return {
            k: v
            for k, v in o.items()
            if self._is_ok_to_store(k, v)
        }

    def _is_ok_to_store(self, k: str, v: Any):
        if isinstance(v, UserName):
            return self.options.output_user_name

        if isinstance(v, PseudoUserName):
            return self.options.output_pseudo_user_name

        if isinstance(v, VRCPlayerId):
            return self.options.output_vrc_player_id

        if isinstance(v, Timestamp):
            return self.options.output_timestamp

        return True

    @classmethod
    def export_all(cls):
        return cls(JsonEncoder.Options.export_all())


class JsonDecoder:
    """
    Json deserializer.
    """

    @dataclass
    class Options:
        metadata_class: Optional[Type[FromJson]] = None

        @classmethod
        def default(cls):
            return cls

    def __init__(self, options: Optional[Options] = None):
        if options is None:
            options = JsonDecoder.Options.default()
        self.options = options
        self.entry_class_by_id: Dict[str, Entry] = {
            klass.type_id(): klass
            for klass in ALL_ENTRIES
        }

    def decode(self, session_log_str: str) -> SessionLog:
        decoder = json.JSONDecoder()
        session_log_dict = decoder.decode(session_log_str)
        log_entries_json = session_log_dict.get("log_entries")
        metadata_json = session_log_dict.get("metadata")

        log_entries = []
        for entry_json in log_entries_json:
            entry_class = self.entry_class_by_id.get(entry_json.get(ENTRY_TYPE_ID_ATTR_NAME))
            entry = entry_class.from_json(entry_json)
            log_entries.append(entry)

        if metadata_json is not None:
            if self.options.metadata_class is not None:
                metadata = self.options.metadata_class.from_json(metadata_json)
            else:
                metadata = metadata_json
        else:
            metadata = None

        return SessionLog(
            log_entries=log_entries,
            metadata=metadata
        )
