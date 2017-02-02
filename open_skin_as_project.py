"""
This module is for the feature "Open Skin as Project".

This feature provides a command which lists all Rainmeter Skins
installed in the Rainmeter Skin folder and allows a quick panel
to open the skin in a new window.

This is done by creating a new sublime text instance using subprocesses.
"""

import os
import subprocess

import sublime
import sublime_plugin

from .path.skin_path_provider import get_cached_skin_path


def on_skin_selected(selected_skin_id):
    """
    This is a callback upon user selecting a skin.

    This can handle user canceling the input.
    Upon selection a respective path is evaluated
    and send to a new sublime text instance.
    """
    if selected_skin_id == -1:
        return

    skins_path = get_cached_skin_path()
    skins = os.listdir(skins_path)
    selected_skin = skins[selected_skin_id]
    selected_skin_path = os.path.join(skins_path, selected_skin)

    # to open a folder in new window, just create a new process with the folder as argument
    st_path = sublime.executable_path()
    subprocess.Popen([
        st_path,
        selected_skin_path
    ])


class RainmeterOpenSkinAsProjectCommand(sublime_plugin.ApplicationCommand):  # pylint: disable=R0903; only provide one method
    """You can execute this command via the sublime API like sublime.run_command("rainmeter_open_skin_as_project")."""

    def run(self):
        """Automatically called upon calling the command."""
        skins_path = get_cached_skin_path()
        skins = os.listdir(skins_path)

        sublime.active_window().show_quick_panel(skins, on_skin_selected, 0, 0, None)
