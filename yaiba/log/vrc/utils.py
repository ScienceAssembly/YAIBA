import re
from typing import Union

from yaiba.constants import DEFAULT_TIMEZONE
from yaiba.log.types import RawEntry, Timestamp

"""
Matches
"2022.03.04 21:50:19 Log        -  "

"2022.03.04 21:50:19 Log        -  [Behaviour] EnteringRoom: Some Room"  
"""
REGEX_LOG_TIMESTAMP = re.compile(
    r'^(?P<year>\d{4})\.(?P<month>\d{2}).(?P<day>\d{2})\s+'
    r'(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})'
)


def parse_timestamp(log_entry: Union[RawEntry, str]) -> Timestamp:
    match = REGEX_LOG_TIMESTAMP.match(log_entry)
    assert match is not None, f'could not find timestamp, {log_entry:?}'
    return create_timestamp_from_match(match)


def create_timestamp_from_match(match: re.Match) -> Timestamp:
    return Timestamp(
        year=int(match.group('year')),
        month=int(match.group('month')),
        day=int(match.group('day')),
        hour=int(match.group('hour')),
        minute=int(match.group('minute')),
        second=int(match.group('second')),
        tzinfo=DEFAULT_TIMEZONE,
    )


VRC_REGEX_LOG_PREFIX = (
    # Timestamp
    r'^(?P<year>\d{4})\.(?P<month>\d{2}).(?P<day>\d{2})\s+'
    r'(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})'
    # Splitter
    r'\s*'
    # Log level
    r'(?P<log_level>[A-z]+)'
    # Splitter
    r'\s*-\s+'
)
