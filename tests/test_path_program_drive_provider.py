"""This module contains the tests for the program drive provider."""

import sys

from unittest import TestCase

PROGRAM_DRIVE_PROVIDER = sys.modules["Rainmeter.path.program_drive_provider"]


class TestFunctions(TestCase):
    """Testing the proram drive provider with unitttest."""

    def test_default_drive(self):
        """Per default we install it onto c:/."""
        program_drive = PROGRAM_DRIVE_PROVIDER.get_cached_program_drive()

        self.assertEqual(program_drive, "C:")
