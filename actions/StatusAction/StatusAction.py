# Import StreamController modules
import multiprocessing
from typing import Optional
from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.DeckManagement.DeckController import DeckController
from src.backend.PageManagement.Page import Page
from src.backend.PluginManager.PluginBase import PluginBase
from loguru import logger as log

# Import python modules
import os
import threading
import subprocess
from PIL import Image
from ...color import color_shift

# Import gtk modules - used for the config rows
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

class StatusAction(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._status_timer: Optional[threading.Timer] = None
        self._base_image: Image.Image = None
        
    def on_ready(self) -> None:
        self._base_image = Image.open(os.path.join(self.plugin_base.PATH, "assets", "info.png"))
        self.set_media(self._base_image, size=0.75)
        self.start_timer()
        
    def on_key_down(self) -> None:
        command = self.get_settings().get("button_command", None)
        if command is None:
            return None

        p = multiprocessing.Process(target=subprocess.Popen, args=[command], kwargs={"shell": True, "start_new_session": True, "stdin": subprocess.DEVNULL, "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL, "cwd": os.path.expanduser("~")})
        p.start()

    def start_timer(self):
        self.stop_timer()
        settings = self.get_settings()
        interval = settings.get("status_interval", 1)
        self._status_timer = threading.Timer(interval, self.execute, args=(True,))
        self._status_timer.setDaemon(True)
        self._status_timer.setName("StatusTimer")
        self._status_timer.start()

    def stop_timer(self):
        if self._status_timer is not None:
            self._status_timer.cancel()

    def execute(self, restart_timer: bool = False):
        self.stop_timer()
        settings = self.get_settings()

        result = self.run_status_command(settings.get("status_command", None))
        if restart_timer:
            self.start_timer()

        self.update_status(result == 0)

    def update_status(self, healthy: bool) -> None:
        bg_colour = self.get_settings().get("background_colour", False)
        healthy_colour = (0, 0, 0, 0) if bg_colour else (0, 220, 0, 255)
        if healthy:
            colour = healthy_colour
        else:
            colour = (220, 0, 0, 255)

        if bg_colour:
            self.set_media(self._base_image, size=0.75)
            self.set_background_color([*colour])
        else:
            self.set_media(color_shift(self._base_image.copy(), colour), size=0.75)
            self.set_background_color([0, 0, 0, 0])

    def get_config_rows(self) -> list:
        rows: list = super().get_config_rows()
        settings = self.get_settings()

        status_command = Adw.EntryRow(title="Status Command")
        button_command = Adw.EntryRow(title="Button Command")
        background_switch = Adw.SwitchRow(
            title="Background status display",
            subtitle="When enabled, the status colours will be used as the key background"
        )
        background_switch.set_active(settings.get("background_colour", False))
        background_switch.connect("notify::active", self.bool_change_handler("background_colour"))

        status_command_value = settings.setdefault("status_command", None)

        if status_command_value is None:
            status_command_value = ""

        status_command.set_text(status_command_value)
        status_command.connect("notify::text", self.string_change_handler("status_command"))

        button_command_value = settings.setdefault("button_command", None)
        if button_command_value is None:
            button_command_value = ""

        button_command.set_text(button_command_value)
        button_command.connect("notify::text", self.string_change_handler("button_command"))

        self.set_settings(settings)
        return [*rows, status_command, button_command, background_switch]

    def string_change_handler(self, name) -> None:
        def handler(entry, _):
            settings = self.get_settings()
            settings[name] = entry.get_text()
            self.set_settings(settings)
        return handler

    def bool_change_handler(self, name):
        def handler(switch, _) -> None:
            settings = self.get_settings()
            settings[name] = switch.get_active()
            self.set_settings(settings)
        return handler

    def run_status_command(self, command: Optional[str]) -> Optional[int]:
        if command is None:
            return None

        result = subprocess.Popen(command, shell=True, start_new_session=True, text=True, stdout=subprocess.PIPE, cwd=os.path.expanduser("~"))
        result.wait()
        return result.returncode
        