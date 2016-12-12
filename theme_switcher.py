"""
The theme switcher is a construct to allow easy manipulations
of the rainmeter themes. The rainmeter themes are hidden to the default system
so other systems can not use these color schemes.
"""

import re

import sublime
import sublime_plugin

from . import logger


class EditThemeCommand(sublime_plugin.ApplicationCommand):

    def run(self, theme):
        """
        This will search all *.tmTheme files in the Rainmeter space and
        tries to match it to the theme param. If no matching theme was found
        an error is reported to the log and tell the user that his intended operation failed.

        Parameters
        ----------
        self: EditThemeCommand
            the current instance given to the method.

        theme: String
            Given String through the menu. Should match one of the tmTheme in the Rainmeter space
        """
        all_themes = sublime.find_resources("*.hidden-tmTheme")

        # only list rainmeter themes
        # could be installed via "add repository" then the file is named after the repository
        rm_exp = re.compile(r"Packages\/Rainmeter\/", re.IGNORECASE)

        theme_exp = re.compile(re.escape(theme))
        filtered_themes = list(filter(lambda t: rm_exp.search(t) and theme_exp.search(t), all_themes))

        if len(filtered_themes) != 1:
            stringified_all_themes = '\n'.join(map(str, all_themes))
            stringified_filtered_themes = '\n'.join(map(str, filtered_themes))
            message = """searched for '{theme}' in

                         {stringified_all_themes}

                         but resulted into more or less than 1 result with

                         {stringified_filtered_themes}"""
            formatted_message = message.format(
                theme=theme,
                stringified_all_themes=stringified_all_themes,
                stringified_filtered_themes=stringified_filtered_themes
            )
            logger.error(__file__, "run(self, theme)", formatted_message)
            sublime.error_message(formatted_message)

        # we found only one
        theme = filtered_themes[0]
        settings = sublime.load_settings("Rainmeter.sublime-settings")
        settings.set("color_scheme", theme)
        sublime.save_settings("Rainmeter.sublime-settings")

    def is_checked(self, theme):
        settings = sublime.load_settings("Rainmeter.sublime-settings")
        color_scheme = settings.get("color_scheme", None)
        theme_exp = re.compile(re.escape(theme))

        return not not theme_exp.search(color_scheme)
