"""This module is for testing Levenshtein distance."""


import sys

from unittest import TestCase

LEVENSHTEIN = sys.modules["Rainmeter.completion.levenshtein"]


class TestLevenShtein(TestCase):
    """Test for the levenshtein module using unittest."""

    def test_same_word_should_zero(self):
        """We use the same word there should be no difference required."""
        diff = LEVENSHTEIN.levenshtein("hello", "hello")

        self.assertEqual(diff, 0)

    def test_zero_words_should_zero(self):
        """Special case with same word but both are empty."""
        diff = LEVENSHTEIN.levenshtein("", "")

        self.assertEqual(diff, 0)

    def test_first_longer_equal_one(self):
        """Same word base but missing characters."""
        diff = LEVENSHTEIN.levenshtein("hello", "hell")

        self.assertEqual(diff, 1)

    def test_second_longer_equal_one(self):
        """
        Reversed case of the missing character.

        Method should work in both ways and not return a negative difference.
        """
        diff = LEVENSHTEIN.levenshtein("hell", "hello")

        self.assertEqual(diff, 1)
