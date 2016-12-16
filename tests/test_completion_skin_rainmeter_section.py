"""
These are unit tests especially made for Rainmeter and Sublime Text.

The ST3 modules need to be loaded differently than the usual import,
because they are not official modules.
"""

import sys

from unittest import TestCase

RAINMETER_SECTION = sys.modules["Rainmeter.completion.skin.rainmeter_section"]


class TestSkinRainmeterSectionCompletion(TestCase):
    """Testing the skin/rainmeter section completion."""

    def test_wrong_section_return_none(self):
        """
        Test should fail since we move in wrong section.

        The given section is 'Different' but we are moving in the Rainmeter section
        thus only 'Rainmeter' is allowed
        """
        complete = RAINMETER_SECTION.SkinRainmeterSectionAutoComplete()
        value_completion = complete.get_value_context_completion("Different", None)

        self.assertEqual(value_completion, None)
