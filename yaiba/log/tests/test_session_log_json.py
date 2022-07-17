from yaiba.log.session_log import SessionLog
from yaiba.log.session_log_json import JsonDecoder, JsonEncoder
from yaiba.log.types import PseudoUserName, UserName
from yaiba.log.vrc.entries.builtin import VRCPlayerJoinEntry
from yaiba.log.vrc.utils import parse_timestamp


class TestJsonEncoder:
    def test__normal(self):
        options = JsonEncoder.Options.default()
        encoder = JsonEncoder(options=options)

        log = SessionLog(
            log_entries=[
                VRCPlayerJoinEntry(
                    timestamp=parse_timestamp("2022.03.04 21:50:19"),
                    user_name=UserName("E.HOBA"),
                    pseudo_user_name=PseudoUserName("E.HOBA Pseudo")
                ),
                VRCPlayerJoinEntry(
                    timestamp=parse_timestamp("2022.03.04 21:50:19"),
                    user_name=UserName("E.HOBA"),
                    pseudo_user_name=PseudoUserName("E.HOBA Pseudo")
                ),
                VRCPlayerJoinEntry(
                    timestamp=parse_timestamp("2022.03.04 21:50:19"),
                    user_name=UserName("E.HOBA"),
                    pseudo_user_name=PseudoUserName("E.HOBA Pseudo")
                )
            ])

        assert encoder.encode(log) == (
            '{"log_entries": [{"timestamp": 1646398219.0, "pseudo_user_name": "E.HOBA '
            'Pseudo", "type_id": "vrc/player_join"}, {"timestamp": 1646398219.0, '
            '"pseudo_user_name": "E.HOBA Pseudo", "type_id": "vrc/player_join"}, '
            '{"timestamp": 1646398219.0, "pseudo_user_name": "E.HOBA Pseudo", "type_id": '
            '"vrc/player_join"}], "metadata": null}')

    def test__output_all_personal_info(self):
        options = JsonEncoder.Options.default()
        options.output_user_name = True
        encoder = JsonEncoder(options=options)

        log = SessionLog(
            log_entries=[
                VRCPlayerJoinEntry(
                    timestamp=parse_timestamp("2022.03.04 21:50:19"),
                    user_name=UserName("E.HOBA"),
                    pseudo_user_name=PseudoUserName("E.HOBA Pseudo")
                ),
                VRCPlayerJoinEntry(
                    timestamp=parse_timestamp("2022.03.04 21:50:19"),
                    user_name=UserName("E.HOBA"),
                    pseudo_user_name=PseudoUserName("E.HOBA Pseudo")
                ),
                VRCPlayerJoinEntry(
                    timestamp=parse_timestamp("2022.03.04 21:50:19"),
                    user_name=UserName("E.HOBA"),
                    pseudo_user_name=PseudoUserName("E.HOBA Pseudo")
                )
            ])

        assert encoder.encode(log) == (
            '{"log_entries": [{"timestamp": 1646398219.0, "user_name": "E.HOBA", '
            '"pseudo_user_name": "E.HOBA Pseudo", "type_id": "vrc/player_join"}, '
            '{"timestamp": 1646398219.0, "user_name": "E.HOBA", "pseudo_user_name": '
            '"E.HOBA Pseudo", "type_id": "vrc/player_join"}, {"timestamp": 1646398219.0, '
            '"user_name": "E.HOBA", "pseudo_user_name": "E.HOBA Pseudo", "type_id": '
            '"vrc/player_join"}], "metadata": null}')

    def test__strict_output_option(self):
        options = JsonEncoder.Options.default()
        options.output_timestamp = False
        options.output_pseudo_user_name = False
        options.output_vrc_player_id = False
        options.output_user_name = False
        encoder = JsonEncoder(options=options)

        log = SessionLog(
            log_entries=[
                VRCPlayerJoinEntry(
                    timestamp=parse_timestamp("2022.03.04 21:50:19"),
                    user_name=UserName("E.HOBA"),
                    pseudo_user_name=PseudoUserName("E.HOBA Pseudo")
                ),
                VRCPlayerJoinEntry(
                    timestamp=parse_timestamp("2022.03.04 21:50:19"),
                    user_name=UserName("E.HOBA"),
                    pseudo_user_name=PseudoUserName("E.HOBA Pseudo")
                ),
                VRCPlayerJoinEntry(
                    timestamp=parse_timestamp("2022.03.04 21:50:19"),
                    user_name=UserName("E.HOBA"),
                    pseudo_user_name=PseudoUserName("E.HOBA Pseudo")
                )
            ])

        assert encoder.encode(log) == (
            '{"log_entries": [{"type_id": "vrc/player_join"}, {"type_id": '
            '"vrc/player_join"}, {"type_id": "vrc/player_join"}], "metadata": null}')


class TestJsonDecoder:
    def test__normal(self):
        decoder = JsonDecoder()

        output = decoder.decode(
            '{"log_entries": [{"timestamp": 1646398219.0, "user_name": "E.HOBA", '
            '"pseudo_user_name": "E.HOBA Pseudo", "type_id": "vrc/player_join"}, '
            '{"timestamp": 1646398219.0, "user_name": "E.HOBA", "pseudo_user_name": '
            '"E.HOBA Pseudo", "type_id": "vrc/player_join"}, {"timestamp": 1646398219.0, '
            '"user_name": "E.HOBA", "pseudo_user_name": "E.HOBA Pseudo", "type_id": '
            '"vrc/player_join"}], "metadata": null}')

        assert output == SessionLog(
            log_entries=[
                VRCPlayerJoinEntry(
                    timestamp=parse_timestamp("2022.03.04 21:50:19"),
                    user_name=UserName("E.HOBA"),
                    pseudo_user_name=PseudoUserName("E.HOBA Pseudo")
                ),
                VRCPlayerJoinEntry(
                    timestamp=parse_timestamp("2022.03.04 21:50:19"),
                    user_name=UserName("E.HOBA"),
                    pseudo_user_name=PseudoUserName("E.HOBA Pseudo")
                ),
                VRCPlayerJoinEntry(
                    timestamp=parse_timestamp("2022.03.04 21:50:19"),
                    user_name=UserName("E.HOBA"),
                    pseudo_user_name=PseudoUserName("E.HOBA Pseudo")
                )
            ])
