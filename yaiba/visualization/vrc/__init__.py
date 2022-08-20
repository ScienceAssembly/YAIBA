from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import List, Optional, Tuple

import pandas
import pandas as pd
import plotly.graph_objects as go
from ipywidgets import Dropdown, HBox, IntSlider, Label, Play, VBox, jslink

from yaiba import SessionLog
from yaiba.log.types import PseudoUserName, Timestamp
from yaiba.log.vrc import VRCEnteringRoomEntry, VRCPlayerLeftEntry, VRCYAIBAPlayerPositionEntry


@dataclass
class PlayerLocation:
    timestamp: Timestamp
    pseudo_user_name: PseudoUserName
    location_x: Optional[float]
    location_z: Optional[float]


class VRCPlayerLocationPlotter():
    timestamp_start: Timestamp
    timestamp_end: Timestamp

    # timestamp: pseudo_user_name (str), user_id (int), location_x (float), location_z (float)
    df: Optional[pd.DataFrame]
    world_boundary: Optional[WorldBoundary]

    def __init__(self, session_log: SessionLog):
        self.session_log = session_log

        self.room_names = self._get_room_names(session_log)
        default_room_name = self.room_names[0]
        self.log_idx_slice = self._get_log_entry_slice(session_log, default_room_name)

        # UI components
        self.room_dropdown = Dropdown(
            options=self.room_names,
            value=default_room_name,
        )
        self.play = Play(step=10, interval=500)
        self.slider = IntSlider()

        self.label_current_timestamp = Label("")

        self.controllers = VBox(
            [
                HBox([
                    Label("Entering room:"),
                    self.room_dropdown,
                ]),
                HBox([
                    self.play,
                    self.slider,
                    Label("(sec)"),
                    self.label_current_timestamp
                ])
            ]
        )

        self.scatter = go.Scatter(
            mode='markers',
        )
        self.figure_widget = go.FigureWidget(
            data=[self.scatter],
            layout=go.Layout(
                yaxis=dict(
                    scaleanchor='x'
                ),
                height=640,
                width=640,
                barmode='overlay',

            )
        )

        jslink((self.play, 'value'), (self.slider, 'value'))
        jslink((self.play, 'min'), (self.slider, 'min'))
        jslink((self.play, 'max'), (self.slider, 'max'))
        self.slider.observe(self._on_changed_slider_value, names='value')
        self.room_dropdown.observe(self._on_changed_room_dropdown_value, names='value')

        self.container = VBox([
            self.controllers,
            self.figure_widget,
        ])

        self.change_entering_room(default_room_name)

    def plot(self):
        return self.container

    def change_entering_room(self, formatted_entering_room: str):

        self.log_idx_slice = self._get_log_entry_slice(self.session_log, formatted_entering_room)

        self.timestamp_start: Timestamp = self.session_log.log_entries[self.log_idx_slice][0].timestamp
        self.timestamp_end: Timestamp = self.session_log.log_entries[self.log_idx_slice][-1].timestamp

        duration_sec = int(self.timestamp_end.timestamp()) - int(self.timestamp_start.timestamp())

        self.play.min = 0
        self.play.max = duration_sec

        self.df = self._gen_dataframe(self.session_log, self.log_idx_slice)
        self.world_boundary = self._get_world_boundary(self.df)

        if self.world_boundary is not None:
            with self.figure_widget.batch_update():
                self.figure_widget.update_layout(xaxis_range=[self.world_boundary.x_min, self.world_boundary.x_max])
                self.figure_widget.update_layout(yaxis_range=[self.world_boundary.z_min, self.world_boundary.z_max])

    def _on_changed_slider_value(self, values):
        sec_diff = values["new"]
        timestamp = self.timestamp_start + timedelta(seconds=sec_diff)
        self.label_current_timestamp.value = timestamp.isoformat()

        if self.df is None or self.world_boundary is None:
            return

        with self.figure_widget.batch_update():
            data_x, data_z, data_username, data_user_id = self._calc_scatter_data(timestamp)
            self.figure_widget.data[0].x = data_x
            self.figure_widget.data[0].y = data_z
            self.figure_widget.data[0].text = data_username
            self.figure_widget.data[0].marker.color = data_user_id

    def _calc_scatter_data(self, timestamp: Timestamp) -> Tuple[List[float], List[float], List[str], List[int]]:
        one_shot_data = self.df.loc[:timestamp].groupby("pseudo_user_name").tail(1).dropna()
        x = one_shot_data["location_x"].tolist()
        z = one_shot_data["location_z"].tolist()
        pseudo_user_name = one_shot_data["pseudo_user_name"].tolist()
        user_id = one_shot_data["user_id"].tolist()
        return (x, z, pseudo_user_name, user_id)

    def _on_changed_room_dropdown_value(self, value):
        new_room_name: str = value.get("new")
        self.change_entering_room(new_room_name)

    @classmethod
    def _get_room_names(cls, session_log: SessionLog) -> List[str]:
        return [
            cls._format_room_dropdown_item(e)
            for e in session_log.log_entries
            if isinstance(e, VRCEnteringRoomEntry)
        ]

    @classmethod
    def _format_room_dropdown_item(cls, entering: VRCEnteringRoomEntry):
        return f"{entering.timestamp.isoformat()} : {entering.room_name}"

    @classmethod
    def _get_log_entry_slice(cls, session_log: SessionLog, formatted_dropdown_item: str) -> slice:
        all_enter_indexes = [
            (idx, e)
            for idx, e in enumerate(session_log.log_entries)
            if isinstance(e, VRCEnteringRoomEntry)
        ]
        maybe_enter_index = [
            enter_idx
            for enter_idx, (log_idx, e) in enumerate(all_enter_indexes)
            if cls._format_room_dropdown_item(e) == formatted_dropdown_item
        ]
        assert len(maybe_enter_index) == 1, f"{formatted_dropdown_item} should only exist one"

        enter_idx = maybe_enter_index[0]

        log_entry_index_start: int = all_enter_indexes[enter_idx][0]
        log_entry_index_end: int = len(session_log.log_entries) \
            if enter_idx + 1 == len(all_enter_indexes) else \
            all_enter_indexes[enter_idx + 1][0]

        return slice(
            log_entry_index_start,
            log_entry_index_end,
        )

    @classmethod
    def _get_world_boundary(cls, df: pandas.DataFrame) -> Optional[WorldBoundary]:
        if df is None:
            return None
        return WorldBoundary(
            x_min=df["location_x"].min(),
            x_max=df["location_x"].max(),
            z_min=df["location_z"].min(),
            z_max=df["location_z"].max(),
        )

    @classmethod
    def _gen_dataframe(cls, session_log: SessionLog, idx_slice: slice) -> Optional[pd.DataFrame]:
        raw_entries = session_log.log_entries[idx_slice]

        has_location_entry = False

        location_entries: List[PlayerLocation] = []
        for entry in raw_entries:
            if isinstance(entry, VRCYAIBAPlayerPositionEntry):
                has_location_entry = True
                location_entries.append(
                    PlayerLocation(
                        timestamp=entry.timestamp,
                        pseudo_user_name=entry.pseudo_user_name,
                        location_x=entry.location_x,
                        location_z=entry.location_z,
                    )
                )
                continue
            if isinstance(entry, VRCPlayerLeftEntry):
                location_entries.append(
                    PlayerLocation(
                        timestamp=entry.timestamp,
                        pseudo_user_name=entry.pseudo_user_name,
                        location_x=None,
                        location_z=None,
                    )
                )
                continue

        if not has_location_entry:
            # No data to be rendered.
            return None

        df = pd.DataFrame(location_entries)
        df.set_index(["timestamp"], inplace=True)

        ids = sorted(set(df["pseudo_user_name"].tolist()))

        df["user_id"] = df["pseudo_user_name"].apply(lambda t: ids.index(t))

        return df


@dataclass
class WorldBoundary:
    x_min: float
    x_max: float
    z_min: float
    z_max: float
