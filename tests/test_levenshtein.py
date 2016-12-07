import sys

from unittest import TestCase

levenshtein = sys.modules["Rainmeter.completion.levenshtein"]


class TestFunctions(TestCase):

    def test_levenshtein_same_word_should_equal_zero(self):
        diff = levenshtein.levenshtein("hello", "hello")

        self.assertEqual(diff, 0)

    def test_levenshtein_zero_words_should_equal_zero(self):
        diff = levenshtein.levenshtein("", "")

        self.assertEqual(diff, 0)

    def test_levenshtein_first_word_one_longer_should_equal_one(self):
        diff = levenshtein.levenshtein("hello", "hell")

        self.assertEqual(diff, 1)

    def test_levenshtein_second_word_one_longer_should_equal_one(self):
        diff = levenshtein.levenshtein("hell", "hello")

        self.assertEqual(diff, 1)
