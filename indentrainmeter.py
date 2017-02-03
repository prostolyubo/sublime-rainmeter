"""
This module handles the indention of the rainmeter files.

Default indention is required to allow collapsing of code blocks.
"""


import re

import sublime
import sublime_plugin


FOLD_MARKER_EXP = re.compile("^([ \\t]*)(;;.*)$")
SECTION_EXP = re.compile("^([ \\t]*)(\\[.*)$")
EMPTY_LINE_EXP = re.compile("^\\s*$")
COMMENT_EXP = re.compile("^\\s*(;.*)")


class IndentType(object):  # pylint: disable=R0903; enum
    """Enum to store the several types of area blocks you can have in a rainmeter skin."""

    # lvl 0, lvl 1,      lvl 1 or 2
    Initial, FoldMarker, Section = range(1, 4)


def calc_section_indention_depth(context, context_depth):
    """."""
    if context == IndentType.Section:
        return context_depth - 1, IndentType.Section, context_depth
    else:
        return context_depth, IndentType.Section, context_depth + 1


def calc_line_indention_depth(line, context, context_depth):
    """."""
    empty_line_match = EMPTY_LINE_EXP.match(line)
    if empty_line_match:
        return 0, context, context_depth

    folder_marker_match = FOLD_MARKER_EXP.match(line)
    if folder_marker_match:
        return 0, IndentType.FoldMarker, 1

    comment_match = COMMENT_EXP.match(line)
    if comment_match:
        return context_depth, context, context_depth

    section_match = SECTION_EXP.match(line)
    if section_match:
        return calc_section_indention_depth(context, context_depth)

    # key value case
    return context_depth, context, context_depth


def get_line_replacement(line, context_depth):
    """Replace the current line with the given indention level."""
    stripped = line.lstrip()
    replacement = "\t" * context_depth + stripped

    return replacement


def indent_text_by_tab_size(text):
    """Main entry point for indenting text."""
    lines = text.split("\n")
    context = IndentType.Initial
    context_depth = 0

    result = []

    for line in lines:
        depth, context, context_depth = calc_line_indention_depth(line, context, context_depth)
        replacement = get_line_replacement(line, depth)
        result.append(replacement)

    return "\n".join(result)


class RainmeterIndentCommand(sublime_plugin.TextCommand):
    """
    Indent a Rainmeter file so code folding is possible in a sensible way.

    Double semicolons at the start of a line indent everything until the next
    double semicolon so you can create custom fold markers. If nothing is
    selected, the whole file will be indented. If one or more regions are
    selected, only these lines will be indented without paying attention to
    the surroundings
    """

    def __get_selected_region(self):
        # If nothing is selected, apply to whole buffer
        if self.view.sel()[0].a == self.view.sel()[-1].b:
            regions = [sublime.Region(0, self.view.size())]
        # If something is selected, apply only to selected regions
        else:
            regions = self.view.sel()

        return regions

    def run(self, edit):  # pylint: disable=R0201; sublime text API, no need for class reference
        """Called when the command is run."""
        regions = self.__get_selected_region()

        for region in regions:
            text = self.view.substr(region)
            indented_text = indent_text_by_tab_size(text)
            self.view.replace(edit, region, indented_text)

    def is_enabled(self):  # pylint: disable=R0201; sublime text API, no need for class reference
        """
        Return True if the command is able to be run at this time.

        The default implementation simply always returns True.
        """
        # Check if current syntax is rainmeter
        israinmeter = self.view.score_selector(self.view.sel()[0].a, "source.rainmeter")

        return israinmeter > 0

    def description(self):  # pylint: disable=R0201; sublime text API, no need for class reference
        """
        Return a description of the command with the given arguments.

        Used in the menus, and for Undo/Redo descriptions.

        Return None to get the default description.
        """
        return "Indent Ini for Code Folding"
