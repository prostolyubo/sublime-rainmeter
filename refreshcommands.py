"""
This module is about refreshing Rainmeter from within Sublime Text.

This can be either activated via a command or as part of the build system.
"""


import os.path

import sublime
import sublime_plugin
from . import rainmeter
from .path.program_path_provider import get_cached_program_path


def calculate_refresh_commands(rm_exe, config, fil, activate, is_inc):
    """Detect if an activate config flag is required or not."""
    if activate:
        cmds = [rm_exe, "!ActivateConfig", config]
        if is_inc:
            cmds.append(fil)
        return cmds
    else:
        return None


class RainmeterRefreshConfigCommand(sublime_plugin.ApplicationCommand):
    """Refresh a given skin file, or Rainmeter if no path is specified."""

    def run(self, cmd):  # pylint: disable=R0201; sublime text API, no need for class reference
        """Called when the command is run."""
        # Get Rainmeter exe path
        rm_path = get_cached_program_path()

        if not rm_path:
            sublime.error_message(
                "Error while trying to refresh Rainmeter" +
                " skin: The Rainmeter executable could not be found." +
                " Please check the value of your \"rainmeter_path\"" +
                " setting.")
            return
        rainmeter_exe = os.path.join(rm_path, "Rainmeter.exe")

        # Refresh skin (or whole rainmeter if no skin specified)
        if not cmd:
            sublime.status_message("Refreshing Rainmeter")
            sublime.active_window().run_command(
                "exec",
                {"cmd": [rainmeter_exe, "!RefreshApp"]}
            )
        else:
            config = rainmeter.get_current_config(cmd[0])
            if not config:
                sublime.error_message(
                    "Error while trying to refresh Rainmeter skin:" +
                    " The config could not be found. Please check the" +
                    " path of the config and your" +
                    " \"rainmeter_skins_path\" setting.")

            # by rainmeter documentation
            # If not specified, the next .ini file variant in the config folder is activated.
            fil = rainmeter.get_current_file(cmd[0])
            if not fil:
                fil = ""

            sublime.status_message("Refreshing config: " + config)

            # Load activate setting
            settings = sublime.load_settings("Rainmeter.sublime-settings")
            activate = settings.get("rainmeter_refresh_and_activate", True)
            is_inc = fil.endswith(".inc")

            refresh_commands = calculate_refresh_commands(rainmeter_exe, config, fil, activate, is_inc)
            if refresh_commands:
                sublime.active_window().run_command("exec", {"cmd": refresh_commands})
            refresh_config = [
                rainmeter_exe, "!Refresh", config
            ]
            sublime.active_window().run_command("exec", {"cmd": refresh_config})

    def description(self):  # pylint: disable=R0201; sublime text API, no need for class reference
        """
        Return a description of the command with the given arguments.

        Used in the menu, if no caption is provided.

        Return None to get the default description.
        """
        return "Refresh Rainmeter Config"


class RainmeterRefreshCommand(sublime_plugin.ApplicationCommand):  # pylint: disable=R0903; sublime text API, methods are overriden
    """Refresh Rainmeter."""

    def run(self):  # pylint: disable=R0201; sublime text API, no need for class reference
        """Called when the command is run."""
        sublime.run_command("rainmeter_refresh_config", {"cmd": []})


class RainmeterRefreshCurrentSkinCommand(sublime_plugin.TextCommand):
    """
    TextCommands are instantiated once per view.

    The View object may be retrieved via self.view.

    Refresh the current skin file opened in a view.
    """

    def run(self, _):  # pylint: disable=R0201; sublime text API, no need for class reference
        """
        Called when the command is run.

        edit param is not used
        """
        # Get current file's path
        filepath = self.view.file_name()

        if not filepath:
            return

        # Refresh config
        sublime.run_command("rainmeter_refresh_config", {"cmd": [filepath]})

    def is_enabled(self):  # pylint: disable=R0201; sublime text API, no need for class reference
        """
        Return True if the command is able to be run at this time.

        The default implementation simply always returns True.
        """
        # Check if current syntax is rainmeter
        israinmeter = self.view.score_selector(self.view.sel()[0].a,
                                               "source.rainmeter")

        return israinmeter > 0

    def description(self):  # pylint: disable=R0201; sublime text API, no need for class reference
        """
        Return a description of the command with the given arguments.

        Used in the menus, and for Undo/Redo descriptions.

        Return None to get the default description.
        """
        return "Refresh Current Rainmeter Skin"
