from typing import Any, Callable
from src.backend.PluginManager.ActionBase import ActionBase

# Import gtk modules - used for the config rows
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

def create_text_row(action: ActionBase, title: str, setting: str, default: str|None = None):
    row = Adw.EntryRow(title=title)
    settings = action.get_settings()
    value = settings.setdefault(setting, default)
    if value is None:
        value = ""

    row.set_text(value)
    row.connect("notify::text", string_change_handler(action, setting))
    action.set_settings(settings)
    return row

def create_bool_row(action: ActionBase, title: str, setting: str, default: bool|None = False, subtitle: str|None = None):
    row = Adw.SwitchRow(title=title, subtitle=subtitle)
    default = False if default is None else default
    settings = action.get_settings()
    row.set_active(settings.get(setting, default))
    row.connect("notify::active", bool_change_handler(action, setting))
    return row

def string_change_handler(action: ActionBase, name: str) -> None:
    return base_change_handler(action, name, lambda x: x.get_text())

def bool_change_handler(action: ActionBase, name: str) -> None:
    return base_change_handler(action, name, lambda x: x.get_active())

def base_change_handler(action: ActionBase, name: str, getter: Callable) -> Callable[[Any, Any], None]:
    def handler(entry, _):
        settings = action.get_settings()
        settings[name] = getter(entry)
        action.set_settings(settings)
    return handler
