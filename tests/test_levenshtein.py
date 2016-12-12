import sys

from unittest import TestCase

levenshtein = sys.modules["Rainmeter.completion.levenshtein"]


class TestLevenShtein(TestCase):

    def same_word_should_equal_zero(self):
        diff = levenshtein.levenshtein("hello", "hello")

        self.assertEqual(diff, 0)

    def zero_words_should_equal_zero(self):
        diff = levenshtein.levenshtein("", "")

        self.assertEqual(diff, 0)

    def first_word_one_longer_should_equal_one(self):
        diff = levenshtein.levenshtein("hello", "hell")

        self.assertEqual(diff, 1)

    def second_word_one_longer_should_equal_one(self):
        diff = levenshtein.levenshtein("hell", "hello")

        self.assertEqual(diff, 1)
