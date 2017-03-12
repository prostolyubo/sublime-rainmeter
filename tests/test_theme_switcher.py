"""This module is to test the theme switcher plugin."""

import sublime

from unittest import TestCase


class TestThemeSwitcherEditThemeCommand(TestCase):
    """Test class wrapper using unittest."""

    # pylint: disable=W0703; This is acceptable since we are testing it not failing

    def test_single_theme(self):
        """Changing the theme should effect the settings."""
        win = sublime.active_window()

        future_skin = "Lachgummi Joghurt"
        win.run_command(
            "edit_theme",
            {
                "theme": future_skin
            }
        )

        settings = sublime.load_settings("Rainmeter.sublime-settings")
        post_theme = settings.get("color_scheme", None)

        self.assertTrue(future_skin in post_theme)

    def test_multi_theme(self):
        """Changing to a non existing theme does not effect the settings."""
        win = sublime.active_window()

        settings = sublime.load_settings("Rainmeter.sublime-settings")
        prior_theme = settings.get("color_scheme", None)

        win.run_command(
            "edit_theme",
            {
                "theme": "Not existing skin"
            }
        )

        settings = sublime.load_settings("Rainmeter.sublime-settings")
        post_theme = settings.get("color_scheme", None)

        self.assertEqual(prior_theme, post_theme)
