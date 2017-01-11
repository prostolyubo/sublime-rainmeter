"""This module is for testing the completion compilers."""


import sys

from unittest import TestCase

COMPLETION_COMPILER = sys.modules["Rainmeter.completion.compiler"]


class TestCompletionCompilerKeys(TestCase):
    """Test for the completion key compiler using unittest."""

    def test_empty_same_size(self):
        """."""
        options = list()

        compiled_key = COMPLETION_COMPILER.compile_keys(options)

        self.assertEqual(len(options), len(compiled_key))

    def test_title_hint(self):
        """."""
        options = [
            {
                "title": "test",
                "hint": "hint"
            }
        ]

        actual = COMPLETION_COMPILER.compile_keys(options)

        expected = [
            ("test", "test\thint", "test", False)
        ]

        self.assertEqual(actual, expected)

    def test_multiple_title_hint(self):
        """."""
        options = [
            {
                "title": "test",
                "hint": "hint"
            },
            {
                "title": "second_title",
                "hint": "second_hint"
            }
        ]

        actual = COMPLETION_COMPILER.compile_keys(options)

        expected = [
            ("test", "test\thint", "test", False),
            ("second_title", "second_title\tsecond_hint", "second_title", False),
        ]

        self.assertEqual(actual, expected)

    def test_title_hint_value(self):
        """."""
        options = [
            {
                "title": "test",
                "hint": "hint",
                "value": "value"
            }
        ]

        actual = COMPLETION_COMPILER.compile_keys(options)

        expected = [
            ("test", "test\thint", "value", False)
        ]

        self.assertEqual(actual, expected)

    def test_title_hint_value_unique(self):
        """."""
        options = [
            {
                "title": "test",
                "hint": "hint",
                "value": "value",
                "unique": True
            }
        ]

        actual = COMPLETION_COMPILER.compile_keys(options)

        expected = [
            ("test", "test\thint", "value", True)
        ]

        self.assertEqual(actual, expected)

    def test_title_hint_unique(self):
        """."""
        options = [
            {
                "title": "title",
                "hint": "hint",
                "unique": True
            }
        ]

        actual = COMPLETION_COMPILER.compile_keys(options)

        expected = [
            ("title", "title\thint", "title", True)
        ]

        self.assertEqual(actual, expected)


class TestCompletionCompilerValues(TestCase):
    """."""

    def test_empty(self):
        """."""
        options = list()

        compiled_key_values = COMPLETION_COMPILER.compile_values(options)

        # empty dict evaluates to False -> not False = True
        self.assertTrue(not compiled_key_values)

    def test_title(self):
        """."""
        options = [
            {
                "title": "title"
            }
        ]

        expected = {
            "title": []
        }

        compiled_key_values = COMPLETION_COMPILER.compile_values(options)

        self.assertEqual(compiled_key_values, expected)

    def test_multiple_title(self):
        """."""
        options = [
            {
                "title": "title"
            },
            {
                "title": "test"
            }
        ]

        expected = {
            "title": [],
            "test": []
        }

        compiled_key_values = COMPLETION_COMPILER.compile_values(options)

        self.assertEqual(compiled_key_values, expected)

    def test_title_valuekey(self):
        """."""
        options = [
            {
                "title": "title",
                "values": [
                    ["key"]
                ]
            }
        ]

        expected = {
            "title": [("key\tDefault", "key")]
        }

        compiled_key_values = COMPLETION_COMPILER.compile_values(options)

        self.assertEqual(compiled_key_values, expected)

    def test_title_multiple_valuekeys(self):
        """."""
        options = [
            {
                "title": "title",
                "values": [
                    ["key"],
                    ["key2"]
                ]
            }
        ]

        expected = {
            "title": [
                ("key\tDefault", "key"),
                ("key2\tDefault", "key2")
            ]
        }

        compiled_key_values = COMPLETION_COMPILER.compile_values(options)

        self.assertEqual(compiled_key_values, expected)

    def test_title_key_hint(self):
        """."""
        options = [
            {
                "title": "title",
                "values": [
                    ["key", "hint"]
                ]
            }
        ]

        expected = {
            "title": [("key\thint", "key")]
        }

        compiled_key_values = COMPLETION_COMPILER.compile_values(options)

        self.assertEqual(compiled_key_values, expected)

    def test_title_key_hint_value(self):
        """."""
        options = [
            {
                "title": "title",
                "values": [
                    ["key", "hint", "value"]
                ]
            }
        ]

        expected = {
            "title": [("key\thint", "value")]
        }

        compiled_key_values = COMPLETION_COMPILER.compile_values(options)

        self.assertEqual(compiled_key_values, expected)

    def test_title_multi_key_hint_value(self):
        """."""
        options = [
            {
                "title": "title",
                "values": [
                    ["default_key"],
                    ["hint_key", "hint_hint"],
                    ["value_key", "value_hint", "value_content"]
                ]
            }
        ]

        expected = {
            "title": [
                ("default_key\tDefault", "default_key"),
                ("hint_key\thint_hint", "hint_key"),
                ("value_key\tvalue_hint", "value_content"),
            ]
        }

        compiled_key_values = COMPLETION_COMPILER.compile_values(options)

        self.assertEqual(compiled_key_values, expected)

    def test_invalid_size_low(self):
        """."""
        options = [
            {
                "title": "title",
                "values": [
                    []
                ]
            }
        ]

        expected = {
            "title": [None]
        }

        compiled_key_values = COMPLETION_COMPILER.compile_values(options)

        self.assertEqual(compiled_key_values, expected)

    def test_invalid_size_high(self):
        """."""
        options = [
            {
                "title": "title",
                "values": [
                    ["value_key", "value_hint", "value_content", "INVALID_FORTH"]
                ]
            }
        ]

        expected = {
            "title": [None]
        }

        compiled_key_values = COMPLETION_COMPILER.compile_values(options)

        self.assertEqual(compiled_key_values, expected)

    def test_all(self):
        """."""
        options = [
            {
                "title": "title",
                "values": [
                    ["default_key"],
                    ["hint_key", "hint_hint"],
                    ["value_key", "value_hint", "value_content"]
                ]
            },
            {
                "title": "different_key",
                "values": [
                    ["default_key"],
                    ["hint_key", "hint_hint"],
                    ["value_key", "value_hint", "value_content"]
                ]
            }
        ]

        expected = {
            "title": [
                ("default_key\tDefault", "default_key"),
                ("hint_key\thint_hint", "hint_key"),
                ("value_key\tvalue_hint", "value_content"),
            ],
            "different_key": [
                ("default_key\tDefault", "default_key"),
                ("hint_key\thint_hint", "hint_key"),
                ("value_key\tvalue_hint", "value_content"),
            ],
        }

        compiled_key_values = COMPLETION_COMPILER.compile_values(options)

        self.assertEqual(compiled_key_values, expected)
