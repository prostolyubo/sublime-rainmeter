import sys

from unittest import TestCase

rainmeter_section = sys.modules["Rainmeter.completion.skin.rainmeter_section"]


class TestFunctions(TestCase):

    def test_completion_skin_rainmeter_section_with_not_rainmeter_should_return_none(self):
        """
        The given section is 'Different' but we are moving in the Rainmeter section
        thus only 'Rainmeter' is allowed
        """
        complete = rainmeter_section.SkinRainmeterSectionAutoComplete()
        value_completion = complete.get_value_context_completion(None, None, None, None, "Different", None, None)

        self.assertEqual(value_completion, None)
