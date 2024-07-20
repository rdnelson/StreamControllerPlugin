# Import StreamController modules
from src.backend.DeckManagement.InputIdentifier import Input
from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.PluginManager.ActionHolder import ActionHolder
from src.backend.PluginManager.ActionInputSupport import ActionInputSupport

# Import actions
from .actions.StatusAction.StatusAction import StatusAction

PLUGIN_ID = "ca_rnelson_StreamController"

class PluginTemplate(PluginBase):
    def __init__(self):
        super().__init__()

        ## Register actions
        self.test_action_holder = ActionHolder(
            plugin_base = self,
            action_base = StatusAction,
            action_id = PLUGIN_ID + "::StatusAction",
            action_name = "Command with status monitoring",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNSUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNSUPPORTED,
            }
        )
        self.add_action_holder(self.test_action_holder)

        # Register plugin
        self.register(
            plugin_name = "My Actions",
            github_repo = "https://github.com/rdnelson/ca_rnelson_StreamController",
            plugin_version = "0.1.0",
            app_version = "1.5.0-beta"
        )
