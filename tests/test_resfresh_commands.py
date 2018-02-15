"""This module is to test the refresh commands plugin."""

import sys

from unittest import TestCase

REFRESH_COMMANDS = sys.modules["Rainmeter.refreshcommands"]


class TestRefreshCommandArgs(TestCase):
    """Test class wrapper using unittest."""

    # pylint: disable=W0703; This is acceptable since we are testing it not failing

    def test_for_more_flags(self):
        """Calling from an inc file should result in less call flags."""
        shorter = REFRESH_COMMANDS.calculate_refresh_commands("Rainmeter.exe", "test-config", "file.inc", True, False)
        longer = REFRESH_COMMANDS.calculate_refresh_commands("Rainmeter.exe", "test-config", "file.ini", True, True)

        self.assertGreater(longer, shorter)

    def test_for_size(self):
        """Calling an inc file should matter only by one argument.

        It is missing the file name since we cannot directly refresh the inc file."""

        inc = REFRESH_COMMANDS.calculate_refresh_commands("Rainmeter.exe", "test-config", "file.inc", True, True)
        ini = REFRESH_COMMANDS.calculate_refresh_commands("Rainmeter.exe", "test-config", "file.ini", True, False)

        self.assertEqual(len(inc) + 1, len(ini))

    def test_config_overwrite(self):
        """If the config option is not activated we force it to do nothing thus resulting in the same result."""
        inc = REFRESH_COMMANDS.calculate_refresh_commands("Rainmeter.exe", "test-config", "file.inc", False, True)
        ini = REFRESH_COMMANDS.calculate_refresh_commands("Rainmeter.exe", "test-config", "file.ini", False, False)

        self.assertEquals(inc, ini)
