from yaiba.log import SessionLog
from yaiba.log.session_log_csv import CsvEncoder
from yaiba.log.types import PseudoUserName, UserName, VRCPlayerId
from yaiba.log.vrc.entries.builtin import VRCPlayerJoinEntry
from yaiba.log.vrc.entries.player_position import VRCYAIBAPlayerPositionEntry
from yaiba.log.vrc.utils import parse_timestamp


class TestCsvEncoder:
    def test__normal(self):
        session_log = SessionLog(log_entries=[
            VRCYAIBAPlayerPositionEntry(
                parse_timestamp("2022.03.04 21:50:19"),

                player_id=VRCPlayerId(7),

                user_name=UserName("E.HOBA"),
                pseudo_user_name=PseudoUserName('E.HOBA pseudo'),

                location_x=1.0,
                location_y=2.0,
                location_z=3.0,
                rotation_1=4.0,
                rotation_2=5.0,
                rotation_3=6.0,

                is_vr=True,
            ),
            VRCYAIBAPlayerPositionEntry(
                parse_timestamp("2022.03.04 21:50:19"),

                player_id=VRCPlayerId(7),

                user_name=UserName("A.HOBA"),
                pseudo_user_name=PseudoUserName('A.HOBA pseudo'),

                location_x=1.0,
                location_y=2.0,
                location_z=3.0,
                rotation_1=4.0,
                rotation_2=5.0,
                rotation_3=6.0,

                is_vr=True,
            ),
            VRCPlayerJoinEntry(
                parse_timestamp("2022.03.04 21:50:19"),

                user_name=UserName("E.HOBA"),
                pseudo_user_name=PseudoUserName('E.HOBA pseudo'),
            ),
            VRCYAIBAPlayerPositionEntry(
                parse_timestamp("2022.03.04 21:50:19"),

                player_id=VRCPlayerId(7),

                user_name=UserName("B.HOBA"),
                pseudo_user_name=PseudoUserName('B.HOBA pseudo'),

                location_x=1.0,
                location_y=2.0,
                location_z=3.0,
                rotation_1=4.0,
                rotation_2=5.0,
                rotation_3=6.0,

                is_vr=True,
            ),
        ])

        encoder = CsvEncoder(VRCYAIBAPlayerPositionEntry)

        assert encoder.encode(session_log) == (
            'timestamp,player_id,user_name,pseudo_user_name,location_x,location_y,location_z,rotation_1,rotation_2,'
            'rotation_3,is_vr\r\n'
            '2022-03-04 21:50:19,7,E.HOBA,E.HOBA pseudo,1.0,2.0,3.0,4.0,5.0,6.0,True\r\n'
            '2022-03-04 21:50:19,7,A.HOBA,A.HOBA pseudo,1.0,2.0,3.0,4.0,5.0,6.0,True\r\n'
            '2022-03-04 21:50:19,7,B.HOBA,B.HOBA pseudo,1.0,2.0,3.0,4.0,5.0,6.0,True\r\n')
