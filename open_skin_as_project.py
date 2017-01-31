import os
import subprocess

import sublime
import sublime_plugin

from .path.skin_path_provider import get_cached_skin_path


class RainmeterOpenSkinAsProjectCommand(sublime_plugin.ApplicationCommand):

    def run(self):
        skins_path = get_cached_skin_path()
        skins = os.listdir(skins_path)

        sublime.active_window().show_quick_panel(skins, self.on_skin_selected, 0, 0, None)

    def on_skin_selected(self, selected_skin_id):
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
