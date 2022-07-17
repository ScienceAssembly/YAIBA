from yaiba.log.test_utils import encode_and_then_decode, new_pseudonymizer
from yaiba.log.types import PseudoUserName, RawEntry, Timestamp, UserName
from yaiba.log.vrc.entries.builtin import VRCBuiltinEntryParser, VRCEnteringRoomEntry, VRCPlayerJoinEntry, \
    VRCPlayerLeftEntry
from yaiba.log.vrc.utils import parse_timestamp


class TestVRCEnteringRoomEntry:
    def test__regex(self):
        output = VRCBuiltinEntryParser.regex_entering_room.match(
            '2022.03.04 21:50:19 Log        -  [Behaviour] Entering Room: VRC理系集会-Science Assembly-')

        assert output is not None

    def test__parse(self):
        parser = VRCBuiltinEntryParser(new_pseudonymizer())

        input = RawEntry("2022.03.04 21:50:19 Log        -  [Behaviour] Entering Room: HAKOBUNE")
        output = parser.parse(input)

        assert isinstance(output, VRCEnteringRoomEntry)
        assert isinstance(output.timestamp, Timestamp)
        assert output == VRCEnteringRoomEntry(
            timestamp=parse_timestamp('2022.03.04 21:50:19'),
            room_name="HAKOBUNE",
        )

    def test__from_json(self):
        entry = VRCEnteringRoomEntry(
            timestamp=parse_timestamp('2022.03.04 21:50:19'),
            room_name="HAKOBUNE",
        )
        
        assert encode_and_then_decode(entry) == entry


class TestVRCPlayerJoinEntry:
    def test__regex(self):
        output = VRCBuiltinEntryParser.regex_player_join.match(
            '2022.03.04 21:50:22 Log        -  [Behaviour] OnPlayerJoined E.HOBA')

        assert output is not None

    def test__parse(self):
        parser = VRCBuiltinEntryParser(new_pseudonymizer(return_value="pseudonymized E.HOBA"))

        input = RawEntry('2022.03.04 21:50:22 Log        -  [Behaviour] OnPlayerJoined E.HOBA')
        output = parser.parse(input)

        assert isinstance(output, VRCPlayerJoinEntry)
        assert isinstance(output.timestamp, Timestamp)
        assert isinstance(output.user_name, UserName)
        assert isinstance(output.pseudo_user_name, PseudoUserName)
        assert output == VRCPlayerJoinEntry(
            timestamp=parse_timestamp('2022.03.04 21:50:22'),
            user_name=UserName('E.HOBA'),
            pseudo_user_name=PseudoUserName("pseudonymized E.HOBA"),
        )

    def test__from_json(self):
        entry = VRCPlayerJoinEntry(
            timestamp=parse_timestamp('2022.03.04 21:50:22'),
            user_name=UserName('E.HOBA'),
            pseudo_user_name=PseudoUserName("pseudonymized E.HOBA"),
        )

        assert encode_and_then_decode(entry) == entry


class TestVRCPlayerLeftEntry:
    def test__regex(self):
        output = VRCBuiltinEntryParser.regex_player_left.match(
            '2022.03.04 21:50:22 Log        -  [Behaviour] OnPlayerLeft E.HOBA')

        assert output is not None

    def test__parse(self):
        parser = VRCBuiltinEntryParser(new_pseudonymizer(return_value="pseudonymized E.HOBA"))

        input = RawEntry('2022.03.04 21:50:22 Log        -  [Behaviour] OnPlayerLeft E.HOBA')
        output = parser.parse(input)

        assert isinstance(output, VRCPlayerLeftEntry)
        assert isinstance(output.timestamp, Timestamp)
        assert isinstance(output.user_name, UserName)
        assert isinstance(output.pseudo_user_name, PseudoUserName)
        assert output == VRCPlayerLeftEntry(
            timestamp=parse_timestamp('2022.03.04 21:50:22'),
            user_name=UserName('E.HOBA'),
            pseudo_user_name=PseudoUserName("pseudonymized E.HOBA"),
        )

    def test__from_json(self):
        entry = VRCPlayerLeftEntry(
            timestamp=parse_timestamp('2022.03.04 21:50:22'),
            user_name=UserName('E.HOBA'),
            pseudo_user_name=PseudoUserName("pseudonymized E.HOBA"),
        )

        assert encode_and_then_decode(entry) == entry
