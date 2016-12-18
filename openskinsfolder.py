"""This module provides a command to open the Rainmeter Skin folder."""


import os.path

import sublime
import sublime_plugin

from .path.skin_path_provider import get_cached_skin_path


class RainmeterOpenSkinsFolderCommand(sublime_plugin.WindowCommand): #pylint: disable=R0903; sublime text API, methods are overriden
    """
    WindowCommands are instantiated once per window.

    The Window object may be retrieved via self.window.
    """

    def run(self):
        """Called when the command is run."""
        skinspath = get_cached_skin_path()
        if not skinspath or not os.path.exists(skinspath):
            sublime.error_message(
                "Error while trying to open Rainmeter" +
                " skins folder: Directory not found. Please check the" +
                " value of your \"skins_path\" setting.")
            return
        self.window.run_command("open_dir", {"dir": skinspath})
