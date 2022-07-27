from typing import TextIO, Union

from yaiba.log import JsonDecoder, JsonEncoder, SessionLog, VRCLogParser
from yaiba.visualization.vrc import VRCPlayerLocationPlotter


def parse_vrchat_log(fp: Union[TextIO, str], config: VRCLogParser.Config = None) -> SessionLog:
    parser = VRCLogParser(config=config)
    if isinstance(fp, str):
        session_log = parser.parse(fp)
    else:
        session_log = parser.parse_file(fp)
    return session_log


def save_session_log(session_log: SessionLog, fp: TextIO, options: JsonEncoder.Options = None):
    encoder = JsonEncoder(options)
    fp.write(encoder.encode(session_log))


def load_session_log(fp: TextIO, options: JsonDecoder.Options = None) -> SessionLog:
    decoder = JsonDecoder(options)
    return decoder.decode(fp.read())


__all__ = [
    JsonDecoder, JsonEncoder, SessionLog, VRCLogParser,
    parse_vrchat_log,
    save_session_log,
    load_session_log,
]
