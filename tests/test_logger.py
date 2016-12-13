"""
This module is about testing the logger.
"""

import sys

from unittest import TestCase

logger = sys.modules["Rainmeter.logger"]


class TestFunctions(TestCase):

    def test_info(self):
        """
        info should not through exceptions due to settings
        """
        try:
            logger.info(
                __file__,
                "test_info(self)",
                "info test"
            )
        except Exception as error:
            self.fail("logger.info() raised exception '" + error + "'")

    def test_error(self):
        """
        error should not through exception due to settings
        """
        try:
            logger.error(
                __file__,
                "test_error(self)",
                "error test"
            )
        except Exception as error:
            self.fail("logger.error() raised exception '" + error + "'")
