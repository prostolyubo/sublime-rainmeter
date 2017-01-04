"""This module is for testing the indent rainmeter module."""


import sys

from unittest import TestCase

INDENT = sys.modules["Rainmeter.indentrainmeter"]


def indention_depth_from_initial(line):
    return INDENT.calc_line_indention_depth(line, INDENT.IndentType.Initial, 0)


def indention_depth_from_fold(line):
    return INDENT.calc_line_indention_depth(line, INDENT.IndentType.FoldMarker, 1)


def indention_depth_from_section(line):
    return INDENT.calc_line_indention_depth(line, INDENT.IndentType.Section, 1)


class TestCalcLineIndentionDepthFromInitial(TestCase):
    """."""

    def test_with_empty_line(self):
        line = ""
        indention_depth = indention_depth_from_initial(line)
        self.assertEqual(indention_depth, (0, INDENT.IndentType.Initial, 0))

    def test_with_comment(self):
        line = "; This is a comment"
        indention_depth = indention_depth_from_initial(line)
        self.assertEqual(indention_depth, (0, INDENT.IndentType.Initial, 0))

    def test_with_fold_marker(self):
        line = ";; This is a fold marker"
        indention_depth = indention_depth_from_initial(line)
        self.assertEqual(indention_depth, (0, INDENT.IndentType.FoldMarker, 1))

    def test_with_section(self):
        line = "[Section]"
        indention_depth = indention_depth_from_initial(line)
        self.assertEqual(indention_depth, (0, INDENT.IndentType.Section, 1))

    def test_with_key_value(self):
        line = "Key = Value"
        indention_depth = indention_depth_from_initial(line)
        self.assertEqual(indention_depth, (0, INDENT.IndentType.Initial, 0))


class TestCalcLineIndentionDepthFromFoldMarker(TestCase):
    """."""

    def test_with_empty_line(self):
        line = ""
        indention_depth = indention_depth_from_fold(line)
        self.assertEqual(indention_depth, (0, INDENT.IndentType.FoldMarker, 1))

    def test_with_comment(self):
        line = "; This is a comment"
        indention_depth = indention_depth_from_fold(line)
        self.assertEqual(indention_depth, (1, INDENT.IndentType.FoldMarker, 1))

    def test_with_fold_marker(self):
        line = ";; This is a fold marker"
        indention_depth = indention_depth_from_fold(line)
        self.assertEqual(indention_depth, (0, INDENT.IndentType.FoldMarker, 1))

    def test_with_section(self):
        line = "[Section]"
        indention_depth = indention_depth_from_fold(line)
        self.assertEqual(indention_depth, (1, INDENT.IndentType.Section, 2))

    def test_with_key_value(self):
        line = "Key = Value"
        indention_depth = indention_depth_from_fold(line)
        self.assertEqual(indention_depth, (1, INDENT.IndentType.FoldMarker, 1))


class TestCalcLineIndentionDepthFromSection(TestCase):
    """."""

    def test_with_empty_line(self):
        line = ""
        indention_depth = indention_depth_from_section(line)
        self.assertEqual(indention_depth, (0, INDENT.IndentType.Section, 1))

    def test_with_comment(self):
        line = "; This is a comment"
        indention_depth = indention_depth_from_section(line)
        self.assertEqual(indention_depth, (1, INDENT.IndentType.Section, 1))

    def test_with_fold_marker(self):
        line = ";; This is a fold marker"
        indention_depth = indention_depth_from_section(line)
        self.assertEqual(indention_depth, (0, INDENT.IndentType.FoldMarker, 1))

    def test_with_section(self):
        line = "[Section]"
        indention_depth = indention_depth_from_section(line)
        self.assertEqual(indention_depth, (0, INDENT.IndentType.Section, 1))

    def test_with_key_value(self):
        line = "Key = Value"
        indention_depth = indention_depth_from_section(line)
        self.assertEqual(indention_depth, (1, INDENT.IndentType.Section, 1))


class TestIndentWholeSection(TestCase):
    """This is about testing a whole function test."""

    def test_one_section(self):
        """."""
        content = '''
[Rainmeter]
Update=1000
DynamicWindowSize=1
DefaultUpdateDivider=1000
AccurateText=1
OnWakeAction=[!Refresh "(Config)"]'''

        result = '''
[Rainmeter]
\tUpdate=1000
\tDynamicWindowSize=1
\tDefaultUpdateDivider=1000
\tAccurateText=1
\tOnWakeAction=[!Refresh "(Config)"]'''

        reference = INDENT.indent_text_by_tab_size(content)

        self.assertEqual(reference, result)

    def test_two_sections(self):
        """."""
        content = '''
[Rainmeter]
Update=1000
DynamicWindowSize=1
DefaultUpdateDivider=1000
AccurateText=1
OnWakeAction=[!Refresh "(Config)"]


[Metadata]
Name=TestEnvironment
Author=thatsIch
Information=PlayGround for Metadata
Version=0.0.1
License=MIT'''

        result = '''
[Rainmeter]
\tUpdate=1000
\tDynamicWindowSize=1
\tDefaultUpdateDivider=1000
\tAccurateText=1
\tOnWakeAction=[!Refresh "(Config)"]


[Metadata]
\tName=TestEnvironment
\tAuthor=thatsIch
\tInformation=PlayGround for Metadata
\tVersion=0.0.1
\tLicense=MIT'''

        reference = INDENT.indent_text_by_tab_size(content)

        self.assertEqual(reference, result)

    def test_section_with_divider(self):
        """."""
        content = '''
;;====================================================
;;  Rainmeter Section
;;====================================================
[Rainmeter]
Update=1000
DynamicWindowSize=1
DefaultUpdateDivider=1000
AccurateText=1
OnWakeAction=[!Refresh "(Config)"]'''

        result = '''
;;====================================================
;;  Rainmeter Section
;;====================================================
\t[Rainmeter]
\t\tUpdate=1000
\t\tDynamicWindowSize=1
\t\tDefaultUpdateDivider=1000
\t\tAccurateText=1
\t\tOnWakeAction=[!Refresh "(Config)"]'''

        reference = INDENT.indent_text_by_tab_size(content)

        self.assertEqual(reference, result)

    def test_divider_with_two_sections(self):
        """."""
        content = '''
;;====================================================
;;  Rainmeter Section
;;====================================================
[Rainmeter]
Update=1000
DynamicWindowSize=1
DefaultUpdateDivider=1000
AccurateText=1
OnWakeAction=[!Refresh "(Config)"]


[Metadata]
Name=TestEnvironment
Author=thatsIch
Information=PlayGround for Metadata
Version=0.0.1
License=MIT'''

        result = '''
;;====================================================
;;  Rainmeter Section
;;====================================================
\t[Rainmeter]
\t\tUpdate=1000
\t\tDynamicWindowSize=1
\t\tDefaultUpdateDivider=1000
\t\tAccurateText=1
\t\tOnWakeAction=[!Refresh "(Config)"]


\t[Metadata]
\t\tName=TestEnvironment
\t\tAuthor=thatsIch
\t\tInformation=PlayGround for Metadata
\t\tVersion=0.0.1
\t\tLicense=MIT'''

        reference = INDENT.indent_text_by_tab_size(content)

        self.assertEqual(reference, result)
