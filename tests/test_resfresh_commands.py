import sys

from unittest import TestCase

REFRESH_COMMANDS = sys.modules["Rainmeter.refreshcommands"]


class TestRefreshCommandArgs(TestCase):
    """Test class wrapper using unittest."""

    # pylint: disable=W0703; This is acceptable since we are testing it not failing

    def test_w_activate_inc_should_be_shorter(self):
        """."""
        shorter = REFRESH_COMMANDS.calculate_refresh_commands("Rainmeter.exe", "test-config", "file.inc", True, True)
        longer = REFRESH_COMMANDS.calculate_refresh_commands("Rainmeter.exe", "test-config", "file.ini", True, False)

        self.assertGreater(longer, shorter)

    def test_w_activate_ini_one_larger(self):
        """Calling an inc file should matter only by one argument.

        It is missing the file name since we cannot directly refresh the inc file."""

        inc = REFRESH_COMMANDS.calculate_refresh_commands("Rainmeter.exe", "test-config", "file.inc", True, True)
        ini = REFRESH_COMMANDS.calculate_refresh_commands("Rainmeter.exe", "test-config", "file.ini", True, False)

        self.assertEqual(len(inc) + 1, len(ini))

    def test_without_activate_ini_inc_same(self):
        """."""
        inc = REFRESH_COMMANDS.calculate_refresh_commands("Rainmeter.exe", "test-config", "file.inc", False, True)
        ini = REFRESH_COMMANDS.calculate_refresh_commands("Rainmeter.exe", "test-config", "file.ini", False, False)

        self.assertEquals(inc, ini)
