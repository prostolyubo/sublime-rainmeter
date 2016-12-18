"""
This module handles the indention of the rainmeter files.

Default indention is required to allow collapsing of code blocks.
"""


import re

import sublime
import sublime_plugin


class RainmeterIndentCommand(sublime_plugin.TextCommand):
    """
    Indent a Rainmeter file so code folding is possible in a sensible way.

    Double semicolons at the start of a line indent everything until the next
    double semicolon so you can create custom fold markers. If nothing is
    selected, the whole file will be indented. If one or more regions are
    selected, only these lines will be indented without paying attention to
    the surroundings
    """

    # Compile regexs to be used later
    rwhitespace_line = re.compile("^([ \\t]*)(.*)$")
    rfold_comment = re.compile("^([ \\t]*)(;;.*)")
    rsection_head = re.compile("^([ \\t]*)(\\[.*)$")

    def __get_selected_region(self):
        # If nothing is selected, apply to whole buffer
        if self.view.sel()[0].a == self.view.sel()[-1].b:
            regions = [sublime.Region(0, self.view.size())]
        # If something is selected, apply only to selected regions
        else:
            regions = self.view.sel()

        return regions


    def run(self, edit): #pylint: disable=R0201; sublime text API, no need for class reference
        """Called when the command is run."""
        regions = self.__get_selected_region()

        for region in regions:
            # Get numbers of regions' lines
            reg_lines = self.view.lines(region)
            line_nums = map(lambda reg: self.view.rowcol(reg.a)[0], reg_lines)

            # Traverse selected lines
            current_indent = -1
            adjustment = -1

            lines = self.view.lines(sublime.Region(0, self.view.size()))   
            for i in line_nums:
                line = lines[i]
                line_content = self.view.substr(line)

                mfc = self.rfold_comment.search(line_content)
                # If current line is fold comment, extract indentation
                if mfc:
                    current_indent = len(mfc.group(1))
                    adjustment = -1
                # Else indent current line according to last fold comment
                else:
                    # Strip leading whitespace
                    mwl = self.rwhitespace_line.search(line_content)
                    stripped_line = ""
                    if mwl:
                        stripped_line = mwl.group(2)
                    # Indent section heads by one more
                    mse = self.rsection_head.search(stripped_line)
                    if mse:
                        adjustment = 0
                        self.view.replace(
                            edit,
                            line,
                            "\t" * (current_indent + 1) + stripped_line)
                    # Indent key = value line two more
                    else:
                        self.view.replace(
                            edit,
                            line,
                            "\t" * (current_indent + 2 + adjustment) +
                            stripped_line)

    def is_enabled(self): #pylint: disable=R0201; sublime text API, no need for class reference
        """
        Return True if the command is able to be run at this time.

        The default implementation simply always returns True.
        """
        # Check if current syntax is rainmeter
        israinmeter = self.view.score_selector(self.view.sel()[0].a,
                                               "source.rainmeter")

        return israinmeter > 0

    def description(self): #pylint: disable=R0201; sublime text API, no need for class reference
        """
        Return a description of the command with the given arguments.

        Used in the menus, and for Undo/Redo descriptions.

        Return None to get the default description.
        """
        return "Indent Ini for Code Folding"
