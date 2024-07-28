from src.backend.PluginManager.ActionBase import ActionBase
from ...color import color_shift
from time import time


class PlayToggleAction(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._play_icon = color_shift(
            "data/icons/com_core447_MaterialIcons/icons/play_arrow-inv.png",
            (0, 220, 0, 255),
        )
        self._pause_icon = color_shift(
            "data/icons/com_core447_MaterialIcons/icons/pause-inv.png",
            (220, 220, 0, 255),
        )
        self._stop_icon = color_shift(
            "data/icons/com_core447_MaterialIcons/icons/stop-inv.png",
            (255, 255, 255, 255),
        )
        self._disconnected_icon = color_shift(
            "data/icons/com_core447_MaterialIcons/icons/music_off-inv.png",
            (220, 0, 0, 255),
        )
        self._unknown_icon = color_shift(
            "data/icons/com_core447_MaterialIcons/icons/question_mark-inv.png",
            (220, 0, 0, 255),
        )

    def on_ready(self) -> None:
        self.set_media(media_path="data/icons/com_core447_MaterialIcons/icons/pause-inv.png")
        self.plugin_base.mpd.listen("state", self._state_change)
        self._state_change(None, self.plugin_base.mpd.status.get("state"))

    def on_key_down(self):
        self._push_time = time()

    def on_key_up(self):
        if time() - self._push_time < 0.5: 
            self.plugin_base.mpd.play_toggle()
        else:
            self.plugin_base.mpd.stop()

    def _state_change(self, old, new):
        if new == "pause":
            self.set_media(self._pause_icon)
        elif new is None:
            self.set_media(self._disconnected_icon)
        elif new == "play":
            self.set_media(self._play_icon)
        elif new == "stop":
            self.set_media(self._stop_icon)
        else:
            self.set_media(self._unknown_icon)
