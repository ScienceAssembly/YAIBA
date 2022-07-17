import dataclasses
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional

from yaiba.log.session_log import Entry, EntryParser
from yaiba.log.types import RawEntry, Timestamp
from yaiba.log.vrc.utils import VRC_REGEX_LOG_PREFIX, create_timestamp_from_match


@dataclass
class VRCYAIBAQuestionnaireAnswerEntry(Entry):
    timestamp: Timestamp
    answer_for_question: Dict[str, str] = dataclasses.field(default_factory=dict)

    @classmethod
    def type_id(cls):
        return 'yaiba/questionnaire_answer'

    @classmethod
    def from_json(cls, value: Dict[str, Any]) -> Entry:
        return VRCYAIBAQuestionnaireAnswerEntry(
            timestamp=Timestamp.from_json(value.get('timestamp')),
            answer_for_question=value.get('answer_for_question')
        )


class YAIBAQuestionnaireAnswerEntryParser(EntryParser):
    regex_pattern: re.Pattern = re.compile(
        VRC_REGEX_LOG_PREFIX +
        r'\[Answer](?P<question_and_answer>.*)$'
    )

    def parse(self, raw_log: RawEntry) -> Optional[Entry]:
        match = self.regex_pattern.match(raw_log)
        if match is None:
            return None

        timestamp = create_timestamp_from_match(match)
        answer_for_question = self._parse_q_and_a(match.group("question_and_answer"))

        return VRCYAIBAQuestionnaireAnswerEntry(
            timestamp=timestamp,
            answer_for_question=answer_for_question
        )

    def _parse_q_and_a(self, qas_str) -> Dict[str, str]:
        """
        :param qas_str: Ex. `"question_1","answer_1","question_2","answer_2"`
        """
        if len(qas_str) < 3:
            return {}
        qas_list = qas_str[1:- 1].split('","')
        questions = qas_list[0::2]
        answers = qas_list[1::2]
        return {
            question: answer
            for question, answer
            in zip(questions, answers)
        }
