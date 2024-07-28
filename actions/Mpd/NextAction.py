from src.backend.PluginManager.ActionBase import ActionBase
from ...color import color_shift

class NextAction(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_key_down(self):
        self.plugin_base.mpd.next()
