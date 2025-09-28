import io

from yaiba.log.vrc.entries.builtin import VRCEnteringRoomEntry, VRCPlayerJoinEntry, VRCPlayerLeftEntry
from yaiba.log.vrc.entries.player_position import VRCYAIBAPlayerPositionEntry, VRCYAIBAPlayerPositionVersionEntry
from yaiba.log.vrc.parser import VRCLogParser, _iter_per_vrc_log_entry


class TestVRCLogParser():
    def test__normal(self):
        input_data = '\n'.join([
            # entity 1
            '2022.03.04 21:50:19 Log      -  [Behaviour] Entering Room: FirstRoom',
            # entity 2
            '2022.03.04 21:50:22 Log        -  [Behaviour] OnPlayerJoined E.HOBA',
            # entity to be ignored
            '2022.03.04 21:50:22 Log        -  [Behaviour] Initialized PlayerAPI "E.HOBA" is remote',
            # entity 3
            "2022.03.04 21:50:23 Log        -  [Player Position Version]1.0.0",
            # entity 4
            '2022.03.04 21:50:31 Log        -  [Player Position]13,"E.HOBA",-6.329126,-0.3207326,-0.3207326,272.0943,'
            '-0.009579957,-0.01711023,0.0004068119,-0.06890159,-0.007717842,True',
            # entity 5
            '2022.03.04 21:50:41 Log        -  [Player Position]13,"E.HOBA",-6.336999,-0.3212091,-0.3212091,291.8254,'
            '-0.01143897,0.03140759,0.0004068119,-0.06890159,-0.007717842,True',
            # entity to be ignored
            '2022.03.04 21:50:25 Log        -  Measure Human Avatar Avatar',
            '2022.03.04 21:50:25 Warning    -  Measure Human Avatar Avatar',
            '2022.03.04 21:50:25 Debug    -  Measure Human Avatar Avatar:',
            '{',
            '    "Avatar": "E.HOBA",',
            '    "AvatarId": 13,',
            '}',
            # entity 6
            '2022.03.05 03:13:50 Log        -  [Behaviour] OnPlayerLeft E.HOBA',
            # entity 7
            '2022.03.04 21:50:19 Log        -  [Behaviour] Entering Room: SecondRoom',
        ])
        parser = VRCLogParser()

        session_log = parser.parse(input_data)

        assert isinstance(session_log.log_entries[0], VRCEnteringRoomEntry)
        assert isinstance(session_log.log_entries[1], VRCPlayerJoinEntry)
        assert isinstance(session_log.log_entries[2], VRCYAIBAPlayerPositionVersionEntry)
        assert isinstance(session_log.log_entries[3], VRCYAIBAPlayerPositionEntry)
        assert isinstance(session_log.log_entries[4], VRCYAIBAPlayerPositionEntry)
        assert isinstance(session_log.log_entries[5], VRCPlayerLeftEntry)
        assert isinstance(session_log.log_entries[6], VRCEnteringRoomEntry)
        assert len(session_log.log_entries) == 7

    def test__splitter(self):
        input_data = '\n'.join([
            # entity 1
            '2022.03.04 21:50:19 Log      -  [Behaviour] Entering Room: FirstRoom',
            # entity 2
            '2022.03.04 21:50:22 Log        -  [Behaviour] OnPlayerJoined E.HOBA',
            # entity 3
            '2022.03.04 21:50:22 Log        -  [Behaviour] Initialized PlayerAPI "E.HOBA" is remote',
            # entity 4
            "2022.03.04 21:50:23 Log        -  [Player Position Version]1.0.0",
            # entity 5
            '2022.03.04 21:50:31 Log        -  [Player Position]13,"E.HOBA",-6.329126,-0.3207326,-0.3207326,272.0943,'
            '-0.009579957,-0.01711023,0.0004068119,-0.06890159,-0.007717842,True',
            # entity 6
            '2022.03.04 21:50:41 Log        -  [Player Position]13,"E.HOBA",-6.336999,-0.3212091,-0.3212091,291.8254,'
            '-0.01143897,0.03140759,0.0004068119,-0.06890159,-0.007717842,True',
            # entity 7
            '2022.03.04 21:50:25 Log        -  Measure Human Avatar Avatar',
            # entity 8
            '2022.03.04 21:50:25 Warning    -  Measure Human Avatar Avatar',
            # entity 9
            '2022.03.04 21:50:25 Debug    -  Measure Human Avatar Avatar:',
            '{',
            '    "Avatar": "E.HOBA",',
            '    "AvatarId": 13,',
            '}',
            # entity 10
            '2022.03.05 03:13:50 Log        -  [Behaviour] OnPlayerLeft E.HOBA',
            # entity 11
            '2022.03.04 21:50:19 Log        -  [Behaviour] Entering Room: SecondRoom',
        ])

        values = list(_iter_per_vrc_log_entry(io.StringIO(input_data)))
        assert len(values) == 11


    def test__past_format__double_empty_line(self):
        input_data = '\n\n\n'.join([
            # entity 1
            '2022.03.04 21:50:19 Log        -  [Behaviour] Entering Room: FirstRoom',
            # entity 2
            '2022.03.04 21:50:22 Log        -  [Behaviour] OnPlayerJoined E.HOBA',
            # entity to be ignored
            '2022.03.04 21:50:22 Log        -  [Behaviour] Initialized PlayerAPI "E.HOBA" is remote',
            # entity 3
            "2022.03.04 21:50:23 Log        -  [Player Position Version]1.0.0",
            # entity 4
            '2022.03.04 21:50:31 Log        -  [Player Position]13,"E.HOBA",-6.329126,-0.3207326,-0.3207326,272.0943,'
            '-0.009579957,-0.01711023,0.0004068119,-0.06890159,-0.007717842,True',
            # entity 5
            '2022.03.04 21:50:41 Log        -  [Player Position]13,"E.HOBA",-6.336999,-0.3212091,-0.3212091,291.8254,'
            '-0.01143897,0.03140759,0.0004068119,-0.06890159,-0.007717842,True',
            # entity to be ignored
            '2022.03.04 21:50:25 Log        -  Measure Human Avatar Avatar',
            # entity 6
            '2022.03.05 03:13:50 Log        -  [Behaviour] OnPlayerLeft E.HOBA',
            # entity 7
            '2022.03.04 21:50:19 Log        -  [Behaviour] Entering Room: SecondRoom',
        ])
        parser = VRCLogParser()

        session_log = parser.parse(input_data)

        assert isinstance(session_log.log_entries[0], VRCEnteringRoomEntry)
        assert isinstance(session_log.log_entries[1], VRCPlayerJoinEntry)
        assert isinstance(session_log.log_entries[2], VRCYAIBAPlayerPositionVersionEntry)
        assert isinstance(session_log.log_entries[3], VRCYAIBAPlayerPositionEntry)
        assert isinstance(session_log.log_entries[4], VRCYAIBAPlayerPositionEntry)
        assert isinstance(session_log.log_entries[5], VRCPlayerLeftEntry)
        assert isinstance(session_log.log_entries[6], VRCEnteringRoomEntry)
        assert len(session_log.log_entries) == 7
