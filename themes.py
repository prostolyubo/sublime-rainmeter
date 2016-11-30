# import os.path
import re

import sublime
import sublime_plugin


class EditThemeCommand(sublime_plugin.ApplicationCommand):

    def run(self, theme):
        """
        bla
        """
        all_themes = sublime.find_resources("*.tmTheme")

        # only list rainmeter themes
        rm_exp = re.compile(r"Packages\/Rainmeter\/")
        rainmeter_themes = list(filter(lambda t: rm_exp.search(t), all_themes))
        theme_exp = re.compile(re.escape(theme))

        for theme in rainmeter_themes:
            if theme_exp.search(theme):
                settings = sublime.load_settings("Rainmeter.sublime-settings")
                settings.set("color_scheme", theme)
                sublime.save_settings("Rainmeter.sublime-settings")

    def is_checked(self, theme):
        settings = sublime.load_settings("Rainmeter.sublime-settings")
        color_scheme = settings.get("color_scheme", None)
        theme_exp = re.compile(re.escape(theme))

        return not not theme_exp.search(color_scheme)
