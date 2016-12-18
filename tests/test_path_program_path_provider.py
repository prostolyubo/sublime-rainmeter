"""This module is to test the program path provider."""

import sys

from unittest import TestCase

PROGRAM_PATH_PROVIDER = sys.modules["Rainmeter.path.program_path_provider"]


class TestProgramPathProvider(TestCase):
    """Need to use a class to extend from TestCase."""

    def test_default_path(self):
        r"""
        If the user installed the application into the default directory.

        it is in "C:/Program Files/Rainmeter"
        """
        default_program_path = PROGRAM_PATH_PROVIDER.get_rm_path_from_default_path()

        self.assertEqual(default_program_path, "C:\\Program Files\\Rainmeter")

    def test_from_registry(self):
        r"""
        Upon normal installation it will leave a registry entry to detect.

        We can use this to find the actual Rainmeter.
        Since we use the default installation path, there should no difference
        """
        registry_program_path = PROGRAM_PATH_PROVIDER.get_rm_path_from_registry()

        self.assertEqual(registry_program_path, "C:\\Program Files\\Rainmeter")

    def test_overall(self):
        r"""
        Per default we install it onto "C:/Program Files/Rainmeter".

        But since we use the path internally we already add / to it
        and python internal path uses \\ instead windows /
        """
        program_path = PROGRAM_PATH_PROVIDER.get_cached_program_path()

        self.assertEqual(program_path, "C:\\Program Files\\Rainmeter\\")
