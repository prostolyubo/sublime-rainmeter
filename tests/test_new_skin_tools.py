"""This module is to test the new skin tools module."""

import sys

import sublime

from unittest import TestCase

NEW_SKIN_TOOLS = sys.modules["Rainmeter.newskintools"]


class TestFunctions(TestCase):
    """Test class wrapper using unittest."""

    # pylint: disable=W0703; This is acceptable since we are testing it not failing

    def test_command(self):
        """Should run through."""
        win = sublime.active_window()
        prior_views = win.views()
        prior_views_size = len(prior_views)
        win.run_command("rainmeter_new_skin_file")
        post_views = win.views()
        post_views_size = len(post_views)

        win.active_view().set_scratch(True)
        win.run_command("close")

        self.assertEqual(prior_views_size + 1, post_views_size)
