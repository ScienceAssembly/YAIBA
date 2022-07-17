from yaiba.log.vrc.entries.builtin import VRCEnteringRoomEntry, VRCPlayerJoinEntry, VRCPlayerLeftEntry
from yaiba.log.vrc.entries.player_position import VRCYAIBAPlayerPositionEntry, VRCYAIBAPlayerPositionVersionEntry
from yaiba.log.vrc.entries.questionnaire import VRCYAIBAQuestionnaireAnswerEntry
from yaiba.log.vrc.entries.yodokoro_tag_marker import VRCYodokoroTagMarkerEntry

ALL_ENTRIES = [
    VRCEnteringRoomEntry,
    VRCPlayerJoinEntry,
    VRCPlayerLeftEntry,
    VRCYodokoroTagMarkerEntry,
    VRCYAIBAPlayerPositionEntry,
    VRCYAIBAPlayerPositionVersionEntry,
    VRCYAIBAQuestionnaireAnswerEntry,
]

__all__ = ALL_ENTRIES
