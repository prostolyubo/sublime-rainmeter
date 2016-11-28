import sys

from unittest import TestCase

levenshtein = sys.modules["Rainmeter.completion.levenshtein"]


class TestFunctions(TestCase):

    def test_levenshtein(self):
        diff = levenshtein.levenshtein("hello", "hello")

        self.assertEqual(diff, 0)
