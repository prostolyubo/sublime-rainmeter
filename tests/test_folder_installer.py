"""This module is for testing installing skins via given folders."""


import os.path
import shutil
import sys
import tempfile

from unittest import TestCase

FOLDER_INSTALLER = sys.modules["Rainmeter.install.from_folder"]
SKIN_PATH_PROVIDER = sys.modules["Rainmeter.path.skin_path_provider"]


class TestFolderInstaller(TestCase):
    """
    Test for the levenshtein module using unittest.
    """

    def test_find_inis_correct_count(self):
        """Find 8 ini files in skin_folder."""
        tests_folder = os.path.dirname(os.path.abspath(__file__))
        folder_path = os.path.join(tests_folder, "skin_folder")

        inis = FOLDER_INSTALLER.find_inis_in_folder(folder_path)

        self.assertEqual(len(inis), 8)

    def test_find_inis_exists(self):
        """All found ini files exist."""
        tests_folder = os.path.dirname(os.path.abspath(__file__))
        folder_path = os.path.join(tests_folder, "skin_folder")

        inis = FOLDER_INSTALLER.find_inis_in_folder(folder_path)

        for ini in inis:
            self.assertTrue(os.path.exists(ini))

    def test_find_skin_name_in_inis(self):
        """Skin name BeatTime found via ini files."""
        tests_folder = os.path.dirname(os.path.abspath(__file__))
        folder_path = os.path.join(tests_folder, "skin_folder")

        inis = FOLDER_INSTALLER.find_inis_in_folder(folder_path)
        skin_name = FOLDER_INSTALLER.find_skin_name_in_inis(inis)

        self.assertEqual(skin_name, "BeatTime")

    def test_find_resources_folder(self):
        """Should find a resources folder."""
        tests_folder = os.path.dirname(os.path.abspath(__file__))
        folder_path = os.path.join(tests_folder, "skin_folder")

        maybe_resources_folder = FOLDER_INSTALLER.find_resources_folder_in_folder(folder_path)

        self.assertNotEqual(maybe_resources_folder, None)

    def test_existence_resource_folder(self):
        """Found folder should exist."""
        tests_folder = os.path.dirname(os.path.abspath(__file__))
        folder_path = os.path.join(tests_folder, "skin_folder")

        maybe_resources_folder = FOLDER_INSTALLER.find_resources_folder_in_folder(folder_path)

        self.assertTrue(os.path.exists(maybe_resources_folder))

    def test_common_path_exists(self):
        """Common path between inis exists."""
        tests_folder = os.path.dirname(os.path.abspath(__file__))
        folder_path = os.path.join(tests_folder, "skin_folder")

        inis = FOLDER_INSTALLER.find_inis_in_folder(folder_path)
        common_path = FOLDER_INSTALLER.common_path(inis)

        self.assertTrue(os.path.exists(common_path))

    def test_common_path_of_skin_exists(self):
        """Common path testing with ini and @Resources folder mixed."""
        tests_folder = os.path.dirname(os.path.abspath(__file__))
        folder_path = os.path.join(tests_folder, "skin_folder")

        inis = FOLDER_INSTALLER.find_inis_in_folder(folder_path)
        resources = FOLDER_INSTALLER.find_resources_folders(folder_path)

        paths = list(inis)
        paths.extend(resources)

        common_path = FOLDER_INSTALLER.common_path(paths)

        self.assertTrue(os.path.exists(common_path))

    def test_install_into_skins_folder(self):
        """Install simple skin into Rainmeter skins folder."""
        tests_folder = os.path.dirname(os.path.abspath(__file__))
        folder_path = os.path.join(tests_folder, "skin_folder")

        # we need to make a temp copy first since we do not want to delete our original test data
        with tempfile.TemporaryDirectory() as temp_path:
            dst_path = os.path.join(temp_path, "skin_folder")
            shutil.copytree(folder_path, dst_path)

            actual_skin_path = FOLDER_INSTALLER.install_into_skins_folder(dst_path)
            self.assertTrue(os.path.isdir(actual_skin_path))

            skins_path = SKIN_PATH_PROVIDER.get_cached_skin_path()
            skin_path = os.path.join(skins_path, "BeatTime")
            skin_path_exists = os.path.exists(skin_path)

            self.assertEquals(actual_skin_path, skin_path)

            resources_path = os.path.join(skin_path, "@Resources")
            resources_path_exists = os.path.exists(resources_path)

            # cleanup
            shutil.rmtree(skin_path)

            self.assertTrue(skin_path_exists)
            self.assertTrue(resources_path_exists)

    def test_install_multi_skin_folder_into_skins_folder(self):
        """Install multi skin configuration into Rainmeter skins folder."""
        tests_folder = os.path.dirname(os.path.abspath(__file__))
        folder_path = os.path.join(tests_folder, "multi_skin_folder")

        # we need to make a temp copy first since we do not want to delete our original test data
        with tempfile.TemporaryDirectory() as temp_path:
            dst_path = os.path.join(temp_path, "multi_skin_folder")
            shutil.copytree(folder_path, dst_path)

            actual_skin_path = FOLDER_INSTALLER.install_into_skins_folder(dst_path)
            self.assertTrue(os.path.isdir(actual_skin_path))

            skins_path = SKIN_PATH_PROVIDER.get_cached_skin_path()
            skin_path = os.path.join(skins_path, "Miniml")
            skin_path_exists = os.path.exists(skin_path)

            self.assertEquals(actual_skin_path, skin_path)

            # cleanup
            shutil.rmtree(skin_path)

            self.assertTrue(skin_path_exists)

    def test_folder_already_exists_existing(self):
        """
        Given
            installing a skin with name BeatTime from a folder

        Then
            checking after the installation if that skin already exists

        Should
            detect an already existing skin
        """
        tests_folder = os.path.dirname(os.path.abspath(__file__))
        folder_path = os.path.join(tests_folder, "skin_folder")

        # we need to make a temp copy first since we do not want to delete our original test data
        with tempfile.TemporaryDirectory() as temp_path:
            dst_path = os.path.join(temp_path, "skin_folder")
            shutil.copytree(folder_path, dst_path)

            actual_skin_path = FOLDER_INSTALLER.install_into_skins_folder(dst_path)
            self.assertTrue(len(actual_skin_path) > 0)
            self.assertTrue(os.path.isdir(actual_skin_path))

            skins_path = SKIN_PATH_PROVIDER.get_cached_skin_path()
            skin_path = os.path.join(skins_path, "BeatTime")
            skin_path_exists = FOLDER_INSTALLER.folder_already_exists(dst_path)
            self.assertEquals(actual_skin_path, skin_path)

            # cleanup the installed skin to make it reproduceable
            shutil.rmtree(skin_path)

            self.assertTrue(skin_path_exists)

    def test_folder_already_exists_not_existing(self):
        """A skin skin_folder should not be already installed at destination."""
        tests_folder = os.path.dirname(os.path.abspath(__file__))
        folder_path = os.path.join(tests_folder, "skin_folder")

        # we need to make a temp copy first since we do not want to delete our original test data
        with tempfile.TemporaryDirectory() as temp_path:
            dst_path = os.path.join(temp_path, "skin_folder")
            shutil.copytree(folder_path, dst_path)

            self.assertFalse(FOLDER_INSTALLER.folder_already_exists(dst_path))
