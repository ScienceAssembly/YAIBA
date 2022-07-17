from unittest.mock import Mock

from yaiba.log import Entry, JsonDecoder, JsonEncoder, SessionLog
from yaiba.log.pseudonymizer import Pseudonymizer
from yaiba.log.types import PseudoUserName


def new_pseudonymizer(return_value: str = "pseudo_user_name") -> Pseudonymizer:
    pseudonymizer: Pseudonymizer = Mock()
    pseudonymizer.pseudonymize_user_name.return_value = PseudoUserName(return_value)
    return pseudonymizer


def encode_and_then_decode(entry: Entry) -> Entry:
    encoder = JsonEncoder.export_all()
    json = encoder.encode(SessionLog(log_entries=[entry]))

    decoder = JsonDecoder()
    session_log = decoder.decode(json)

    assert len(session_log.log_entries) == 1
    return session_log.log_entries[0]
