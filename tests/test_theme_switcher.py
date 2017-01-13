import sublime

from unittest import TestCase


class TestThemeSwitcher(TestCase):
    """Test class wrapper using unittest."""

    # pylint: disable=W0703; This is acceptable since we are testing it not failing

    def test_edit_theme_command(self):
        """Should run through."""
        win = sublime.active_window()
        win.run_command(
            "edit_theme",
            {
                "theme": "Rainmeter (Light)"
            }
        )
