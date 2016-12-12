import sys

from unittest import TestCase

levenshtein = sys.modules["Rainmeter.completion.levenshtein"]


class TestLevenShtein(TestCase):
    """
    Test for the levenshtein module
    """

    def same_word_should_equal_zero(self):
        """
        if we use the same word there should be no difference required
        """
        diff = levenshtein.levenshtein("hello", "hello")

        self.assertEqual(diff, 0)

    def zero_words_should_equal_zero(self):
        """
        special case with same word but both are empty
        """
        diff = levenshtein.levenshtein("", "")

        self.assertEqual(diff, 0)

    def first_word_one_longer_should_equal_one(self):
        """
        try with same word base but missing characters
        """
        diff = levenshtein.levenshtein("hello", "hell")

        self.assertEqual(diff, 1)

    def second_word_one_longer_should_equal_one(self):
        """
        reversed case of the missing character.
        method should work in both ways and not return a negative difference
        """
        diff = levenshtein.levenshtein("hell", "hello")

        self.assertEqual(diff, 1)
