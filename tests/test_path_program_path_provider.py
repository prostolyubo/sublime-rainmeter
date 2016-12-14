import sys

from unittest import TestCase

program_path_provider = sys.modules["Rainmeter.path.program_path_provider"]


class TestProgramPathProvider(TestCase):

    def test_default_path(self):
        """
        If the user installed the application into the default directory
        it is in "C:/Program Files/Rainmeter"
        """
        default_program_path = program_path_provider._get_rm_path_from_default_path()

        self.assertEqual(default_program_path, "C:\\Program Files\\Rainmeter")

    def test_from_registry(self):
        """
        Upon normal installation it will leave a registry entry to detect.
        We can use this to find the actual Rainmeter.
        Since we use the default installation path, there should no difference
        """
        registry_program_path = program_path_provider._get_rm_path_from_registry()

        self.assertEqual(registry_program_path, "C:\\Program Files\\Rainmeter")

    def test_overall(self):
        """
        Per default we install it onto "C:/Program Files/Rainmeter"
        but since we use the path internally we already add / to it
        and python internal path uses \\ instead windows /
        """
        program_path = program_path_provider.get_cached_program_path()

        self.assertEqual(program_path, "C:\\Program Files\\Rainmeter\\")
