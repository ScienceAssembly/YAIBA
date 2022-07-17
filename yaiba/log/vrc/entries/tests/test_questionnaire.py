from yaiba.log.test_utils import encode_and_then_decode
from yaiba.log.types import RawEntry
from yaiba.log.vrc.entries.questionnaire import VRCYAIBAQuestionnaireAnswerEntry, YAIBAQuestionnaireAnswerEntryParser
from yaiba.log.vrc.utils import parse_timestamp


class TestYAIBAQuestionnaireAnswerEntry:
    def test__regex(self):
        output = YAIBAQuestionnaireAnswerEntryParser.regex_pattern.match(
            '2022.04.06 22:54:50 Log - [Answer]"question_1","answer_1","question_2","answer_2"')
        assert output is not None

    def test__parse(self):
        parser = YAIBAQuestionnaireAnswerEntryParser()

        output = parser.parse(RawEntry(
            '2022.04.06 22:54:50 Log - [Answer]"question_1","answer_1","question_2","answer_2"'))

        assert output == VRCYAIBAQuestionnaireAnswerEntry(
            timestamp=parse_timestamp('2022.04.06 22:54:50'),
            answer_for_question={
                "question_1": "answer_1",
                "question_2": "answer_2",
            },
        )

    def test__from_json(self):
        entry = VRCYAIBAQuestionnaireAnswerEntry(
            timestamp=parse_timestamp('2022.04.06 22:54:50'),
            answer_for_question={
                "question_1": "answer_1",
                "question_2": "answer_2",
            },
        )
        assert encode_and_then_decode(entry) == entry
