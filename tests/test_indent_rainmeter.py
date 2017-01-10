"""This module is for testing the indent rainmeter module."""


import sys

from unittest import TestCase

INDENT = sys.modules["Rainmeter.indentrainmeter"]


def indention_depth_from_initial(line):
    """Helper method to start with an initial indention type."""
    return INDENT.calc_line_indention_depth(line, INDENT.IndentType.Initial, 0)


def indention_depth_from_fold(line):
    """Helper method to start with a fold marker indention type."""
    return INDENT.calc_line_indention_depth(line, INDENT.IndentType.FoldMarker, 1)


def indention_depth_from_section(line):
    """Helper method to start with a section indention type."""
    return INDENT.calc_line_indention_depth(line, INDENT.IndentType.Section, 1)


class TestCalcLineIndentionDepthFromInitial(TestCase):
    """
    This test is for showing the behaviour detecting different indenttypes.

    Context depth can increase depending how the document starts.
    It accepts invalid Rainmeter definitions like:

    Key=Value

    at the beginning of your document. This will not fail the indention itself.
    """

    def test_with_empty_line(self):
        """An empty line should be ignored."""
        line = ""
        indention_depth = indention_depth_from_initial(line)
        self.assertEqual(indention_depth, (0, INDENT.IndentType.Initial, 0))

    def test_with_comment(self):
        """A comment will be ignored."""
        line = "; This is a comment"
        indention_depth = indention_depth_from_initial(line)
        self.assertEqual(indention_depth, (0, INDENT.IndentType.Initial, 0))

    def test_with_fold_marker(self):
        """Fold markers increase the indention depth."""
        line = ";; This is a fold marker"
        indention_depth = indention_depth_from_initial(line)
        self.assertEqual(indention_depth, (0, INDENT.IndentType.FoldMarker, 1))

    def test_with_section(self):
        """Section increase the indention depth."""
        line = "[Section]"
        indention_depth = indention_depth_from_initial(line)
        self.assertEqual(indention_depth, (0, INDENT.IndentType.Section, 1))

    def test_with_key_value(self):
        """Key values are actually invalid but they stay at the same indention level."""
        line = "Key = Value"
        indention_depth = indention_depth_from_initial(line)
        self.assertEqual(indention_depth, (0, INDENT.IndentType.Initial, 0))


class TestCalcLineIndentionDepthFromFoldMarker(TestCase):
    """
    This test is to show the behaviour for an indention coming from a fold marker.

    A fold marker is defined by ;;
    and meant to be a synthatic sugar definition to fold multiple sections at once.
    For example you can group all meters together or all about problem X.
    """

    def test_with_empty_line(self):
        """
        Due to the fold marker the indention depth is 1.

        Thus the following indention depth stays at 1
        but the line itself is rendered as zero.
        This prevents a lot of whitespaces in the file
        if you split up your section.
        """
        line = ""
        indention_depth = indention_depth_from_fold(line)
        self.assertEqual(indention_depth, (0, INDENT.IndentType.FoldMarker, 1))

    def test_with_comment(self):
        """Comment are printed in the same indention level as given."""
        line = "; This is a comment"
        indention_depth = indention_depth_from_fold(line)
        self.assertEqual(indention_depth, (1, INDENT.IndentType.FoldMarker, 1))

    def test_with_fold_marker(self):
        """Additional fold marker will be printed at the same level as the previous fold marker."""
        line = ";; This is a fold marker"
        indention_depth = indention_depth_from_fold(line)
        self.assertEqual(indention_depth, (0, INDENT.IndentType.FoldMarker, 1))

    def test_with_section(self):
        """A section increases the depth context."""
        line = "[Section]"
        indention_depth = indention_depth_from_fold(line)
        self.assertEqual(indention_depth, (1, INDENT.IndentType.Section, 2))

    def test_with_key_value(self):
        """
        Special handled case since it is invalid.

        KeyValue pairs stay at level 1.
        """
        line = "Key = Value"
        indention_depth = indention_depth_from_fold(line)
        self.assertEqual(indention_depth, (1, INDENT.IndentType.FoldMarker, 1))


class TestCalcLineIndentionDepthFromSection(TestCase):
    """Section increase the depth level."""

    def test_with_empty_line(self):
        """Empty lines are ignored."""
        line = ""
        indention_depth = indention_depth_from_section(line)
        self.assertEqual(indention_depth, (0, INDENT.IndentType.Section, 1))

    def test_with_comment(self):
        """Comment are printed on same level as key value pairs."""
        line = "; This is a comment"
        indention_depth = indention_depth_from_section(line)
        self.assertEqual(indention_depth, (1, INDENT.IndentType.Section, 1))

    def test_with_fold_marker(self):
        """Invalid construct, but this counts as a simple comment."""
        line = ";; This is a fold marker"
        indention_depth = indention_depth_from_section(line)
        self.assertEqual(indention_depth, (0, INDENT.IndentType.FoldMarker, 1))

    def test_with_section(self):
        """Invalid construct. Section following a section are staying on the same level."""
        line = "[Section]"
        indention_depth = indention_depth_from_section(line)
        self.assertEqual(indention_depth, (0, INDENT.IndentType.Section, 1))

    def test_with_key_value(self):
        """KeyValue Pairs are printed on the next level."""
        line = "Key = Value"
        indention_depth = indention_depth_from_section(line)
        self.assertEqual(indention_depth, (1, INDENT.IndentType.Section, 1))


class TestIndentWholeSection(TestCase):
    """This is about testing a whole function test."""

    def test_one_section(self):
        """Testing a stand alone section."""
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
        """Testing only two consecutive sections."""
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
        """After a divider a section can follow which needs to be fully indented."""
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
        """
        After a divider multiple sections can follow.

        Both sections need to be fully indented.
        """
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
