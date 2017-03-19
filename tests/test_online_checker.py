"""This module is for testing the online checker."""


import sys

from unittest import TestCase

ONLINE_CHECKER = sys.modules["Rainmeter.web.online_checker"]


class TestRmDocOnlineChecker(TestCase):
    """Test of the online checks for Rainmeter Documentation using unittest."""

    def test_is_rm_doc_online(self):
        """Rainmeter Documentation should be up to synchronize with it."""
        is_online = ONLINE_CHECKER.is_rm_doc_online()

        self.assertTrue(is_online)


class TestGithubOnlineChecker(TestCase):
    """Test of the online checks for Github using unittest."""

    def test_is_gh_online(self):
        """Github should be up to download stuff from it."""
        is_online = ONLINE_CHECKER.is_gh_online()

        self.assertTrue(is_online)


class TestRawGithubOnlineChecker(TestCase):
    """Test of the online checks for Raw Github using unittest since raw is served from different service."""

    def test_is_raw_gh_online(self):
        """Raw Github should be up to download stuff from it."""
        is_online = ONLINE_CHECKER.is_gh_raw_online()

        self.assertTrue(is_online)
