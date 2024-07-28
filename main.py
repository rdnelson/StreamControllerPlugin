# Import StreamController modules
from src.Signals import Signals
from src.backend.DeckManagement.InputIdentifier import Input
from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.PluginManager.ActionHolder import ActionHolder
from src.backend.PluginManager.ActionInputSupport import ActionInputSupport

# Import actions
from .actions.StatusAction.StatusAction import StatusAction
from .actions.Mpd.PlayToggleAction import PlayToggleAction
from .actions.Mpd.NextAction import NextAction
from .backend.MpdBackend import MpdBackend
import globals as gl

PLUGIN_ID = "ca_rnelson_StreamController"

class MyPlugin(PluginBase):
    def __init__(self):
        super().__init__()

        ## Register actions
        status_action_holder = ActionHolder(
            plugin_base = self,
            action_base = StatusAction,
            action_id = PLUGIN_ID + "::StatusAction",
            action_name = "Command with status monitoring",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNSUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNSUPPORTED,
            },
        )
        self.add_action_holder(status_action_holder)

        mpd_play_toggle_action = ActionHolder(
            plugin_base = self,
            action_base = PlayToggleAction,
            action_id = PLUGIN_ID + "::MpdPlayToggle",
            action_name = "MPD Play/Pause",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNSUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNSUPPORTED,
            },
        )
        self.add_action_holder(mpd_play_toggle_action)

        mpd_next_action = ActionHolder(
            plugin_base = self,
            action_base = NextAction,
            action_id = PLUGIN_ID + "::MpdNext",
            action_name = "MPD Next Song",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNSUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNSUPPORTED,
            },
        )
        self.add_action_holder(mpd_next_action)

        # Register plugin
        self.register(
            plugin_name = "My Actions",
            github_repo = "https://github.com/rdnelson/ca_rnelson_StreamController",
            plugin_version = "0.1.0",
            app_version = "1.5.0-beta"
        )

        settings = self.get_settings()
        mpd_host = settings.get("mpd_host", "localhost")
        mpd_port = settings.get("mpd_port", 6660)

        self.mpd = MpdBackend()
        self.mpd.set_host(mpd_host)
        self.mpd.set_port(mpd_port)

        gl.signal_manager.connect_signal(Signals.AppQuit, self._stop_mpd)

    def _stop_mpd(self):
        self.mpd.disconnect()
