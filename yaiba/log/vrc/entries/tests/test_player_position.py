import pytest

from yaiba.log.test_utils import encode_and_then_decode, new_pseudonymizer
from yaiba.log.types import PseudoUserName, RawEntry, UserName, VRCPlayerId
from yaiba.log.vrc.entries.player_position import VRCYAIBAPlayerPositionEntry, VRCYAIBAPlayerPositionVersionEntry, \
    YAIBAPlayerPositionEntryParser
from yaiba.log.vrc.utils import parse_timestamp


class TestYAIBAPlayerPositionVersionEntry:
    def test__regex(self):
        output = YAIBAPlayerPositionEntryParser.regex_version.match(
            "2022.03.04 21:50:19 Log        -  [Player Position Version]1.0.0")

        assert output is not None

    def test__parse(self):
        parser = YAIBAPlayerPositionEntryParser(new_pseudonymizer())

        output = parser.parse(RawEntry("2022.03.04 21:50:19 Log        -  [Player Position Version]1.0.0"))

        assert isinstance(output, VRCYAIBAPlayerPositionVersionEntry)
        assert output == VRCYAIBAPlayerPositionVersionEntry(
            timestamp=parse_timestamp('2022.03.04 21:50:19'),
            major=1, minor=0, patch=0)

    def test__from_json(self):
        entry = VRCYAIBAPlayerPositionVersionEntry(
            timestamp=parse_timestamp('2022.03.04 21:50:19'),
            major=1, minor=0, patch=0)

        assert encode_and_then_decode(entry) == entry


class TestYAIBAPlayerPositionEntry:
    def test__regex_v0(self):
        output = YAIBAPlayerPositionEntryParser.regex_entry_v0.match(
            '2022.03.04 21:57:53 Log        -  [Player Position]13,"E.HOBA",-1.622916,1.637101,230.3723,'
            '-3.32147,-2.619154,True'
        )

        assert output is not None

    """
    v0ケースは不要とのことで、削除
    def test__parse_v0(self): ...
    """

    """
    v0ケースは不要とのことで、削除
    def test__parse_v0__user_name_contains_double_quotes__unescape(self): ...
    """

    def test__regex_v1_0_0(self):
        output = YAIBAPlayerPositionEntryParser.regex_entry_v1_0_0.match(
            '2022.03.04 21:57:53 Log        -  [Player Position]13,"E.HOBA",-1.622916,1.637101,1.937101,230.3723,'
            '-3.32147,-2.619154,-0.03742229,-0.007943284,0.0001138111,True'
        )

        assert output is not None

    def test__parse_v1_0_0(self):
        parser = YAIBAPlayerPositionEntryParser(new_pseudonymizer("pseudo E.HOBA"))

        # Feed version entry to switch the version
        parser.parse(RawEntry("2022.03.04 21:50:19 Log        -  [Player Position Version]1.0.0"))

        output = parser.parse(RawEntry(
            '2022.03.04 21:57:53 Log        -  [Player Position]13,"E.HOBA",-1.622916,1.637101,1.937101,230.3723,'
            '-3.32147,-2.619154,-0.03742229,-0.007943284,0.0001138111,True'
        ))

        assert isinstance(output, VRCYAIBAPlayerPositionEntry)
        assert isinstance(output.user_name, UserName)
        assert isinstance(output.player_id, VRCPlayerId)
        assert isinstance(output.pseudo_user_name, PseudoUserName)
        assert output == VRCYAIBAPlayerPositionEntry(
            timestamp=parse_timestamp('2022.03.04 21:57:53'),
            player_id=VRCPlayerId(13),
            user_name=UserName('E.HOBA'),
            pseudo_user_name=PseudoUserName("pseudo E.HOBA"),
            location_x=pytest.approx(-1.622916),
            location_y=pytest.approx(1.637101),
            location_z=pytest.approx(1.937101),
            rotation_1=pytest.approx(230.3723),
            rotation_2=pytest.approx(-3.32147),
            rotation_3=pytest.approx(-2.619154),
            velocity_x=pytest.approx(-0.03742229),
            velocity_y=pytest.approx(-0.007943284),
            velocity_z=pytest.approx(0.0001138111),
            is_vr=True,
        )

    def test__parse_v1_0_0__user_name_contains_double_quotes__unescape(self):
        parser = YAIBAPlayerPositionEntryParser(new_pseudonymizer("pseudo E.HOBA"))

        # Feed version entry to switch the version
        parser.parse(RawEntry("2022.03.04 21:50:19 Log        -  [Player Position Version]1.0.0"))

        output = parser.parse(RawEntry(
            '2022.03.04 21:57:53 Log        -  [Player Position]13,"E"".""HOBA",-1.622916,1.637101,1.937101,230.3723,'
            '-3.32147,-2.619154,-0.03742229,-0.007943284,0.0001138111,True'
        ))

        assert isinstance(output, VRCYAIBAPlayerPositionEntry)
        assert isinstance(output.user_name, UserName)
        assert isinstance(output.player_id, VRCPlayerId)
        assert isinstance(output.pseudo_user_name, PseudoUserName)
        assert output == VRCYAIBAPlayerPositionEntry(
            timestamp=parse_timestamp('2022.03.04 21:57:53'),
            player_id=VRCPlayerId(13),
            user_name=UserName('E"."HOBA'),
            pseudo_user_name=PseudoUserName("pseudo E.HOBA"),
            location_x=pytest.approx(-1.622916),
            location_y=pytest.approx(1.637101),
            location_z=pytest.approx(1.937101),
            rotation_1=pytest.approx(230.3723),
            rotation_2=pytest.approx(-3.32147),
            rotation_3=pytest.approx(-2.619154),
            velocity_x=pytest.approx(-0.03742229),
            velocity_y=pytest.approx(-0.007943284),
            velocity_z=pytest.approx(0.0001138111),
            is_vr=True,
        )

    def test__from_json(self):
        entry = VRCYAIBAPlayerPositionEntry(
            timestamp=parse_timestamp('2022.03.04 21:57:53'),
            player_id=VRCPlayerId(13),
            user_name=UserName('E"."HOBA'),
            pseudo_user_name=PseudoUserName("pseudo E.HOBA"),
            location_x=-1.622916,
            location_y=1.637101,
            location_z=1.937101,
            rotation_1=230.3723,
            rotation_2=-3.32147,
            rotation_3=-2.619154,
            velocity_x=-0.03742229,
            velocity_y=-0.007943284,
            velocity_z=0.0001138111,
            is_vr=True,
        )
        
        assert encode_and_then_decode(entry) == entry
        assert isinstance(entry.user_name, UserName)
        assert isinstance(entry.player_id, VRCPlayerId)
        assert isinstance(entry.pseudo_user_name, PseudoUserName)

    def test__from_json__velocity_is_none_for_previously_generated_json_files(self):
        # Issue: https://github.com/ScienceAssembly/YAIBA/issues/11

        entry = VRCYAIBAPlayerPositionEntry(
            timestamp=parse_timestamp('2022.03.04 21:57:53'),
            player_id=VRCPlayerId(13),
            user_name=UserName('E"."HOBA'),
            pseudo_user_name=PseudoUserName("pseudo E.HOBA"),
            location_x=-1.622916,
            location_y=1.637101,
            location_z=1.937101,
            rotation_1=230.3723,
            rotation_2=-3.32147,
            rotation_3=-2.619154,
            velocity_x=None,
            velocity_y=None,
            velocity_z=None,
            is_vr=True,
        )

        assert encode_and_then_decode(entry) == entry
        assert isinstance(entry.user_name, UserName)
        assert isinstance(entry.player_id, VRCPlayerId)
        assert isinstance(entry.pseudo_user_name, PseudoUserName)
