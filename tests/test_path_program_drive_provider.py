import sys

from unittest import TestCase

program_drive_provider = sys.modules["Rainmeter.path.program_drive_provider"]


class TestFunctions(TestCase):

    def test_completion_skin_rainmeter_section_with_not_rainmeter_should_return_none(self):
        """
        Per default we install it onto c:/
        """
        program_drive = program_drive_provider.get_cached_program_drive()

        self.assertEqual(program_drive, "C:")
