"""This module handles the whole auto smart completion sublime-rainmeter has to offer."""

# python libs
import re

# st libs
import sublime

# own libs
from .. import logger
from .skin.rainmeter_section import SkinRainmeterSectionAutoComplete
from .skin.metadata_section import SkinMetadataSectionAutoComplete
from .section import SkinSectionAutoCompleter


class ContextSensAutoCompletion(object):
    """
    This represents the internal implementation for the contextual auto completion.

    It uses smart environmental information like section, key, values etc
    to provide smarter auto completion suggestions.
    """

    # only show our completion list because nothing else makes sense in this context
    flags = sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS

    section = None
    skin_rainmeter_section = None
    skin_metadata_section = None

    scope = "source.rainmeter"

    # comments are specified by ';'
    comment_exp = re.compile(r'^\s*;.*')

    # enable searching for [] in multiline environment
    bracket_expression = re.compile(r'^\s*\[.+\]\s*$', re.MULTILINE)
    section_expression = re.compile(r'^\s*\[(.+)\]\s*$', re.I)
    key_expression = re.compile(r'^\s*(.+)\s*=?\s*(.*?)\s*$', re.MULTILINE)
    key_value_expression = re.compile(r'^\s*(.+?)\s*=\s*(.*?)\s*$', re.MULTILINE)

    def __init__(self):
        """Initialize the different completer components."""
        self.section = SkinSectionAutoCompleter()
        self.skin_rainmeter_section = SkinRainmeterSectionAutoComplete()
        self.skin_metadata_section = SkinMetadataSectionAutoComplete()

    def get_lines_of_section_on_cursor(self, view, location):
        """Determine content of current section."""
        size = view.size()
        start_content = view.substr(sublime.Region(0, location))
        end_content = view.substr(sublime.Region(location, size))

        start_index = self.get_start_index_of_section(start_content)
        end_index = self.get_end_index_of_section(end_content, location, size)

        section = view.substr(sublime.Region(start_index, end_index))
        lines = section.splitlines()

        return lines

    def get_start_index_of_section(self, start_content):
        """
        Return the index of the section.

        If no section is found the first index (0) is returned
        """
        matches = list(self.bracket_expression.finditer(start_content))

        if len(matches) > 0:
            last_match = matches[-1]
            return last_match.start()

        # no previous section found, hardly legal but who cares
        else:
            return 0

    def get_end_index_of_section(self, end_content, offset, end_index):
        """
        Return the index of the next section.

        If no next section is found the last index is returned given through the param end_index
        """
        matches = list(self.bracket_expression.finditer(end_content))
        if len(matches) > 0:
            first_match = matches[0]
            return first_match.start() + offset

        # no next section found
        else:
            return end_index

    def get_key_value(self, line_content):
        """
        Extract the key and/or value in a line if existing.

        This is used if a specific completion is only shown
        on special conditions like only show X on measures.

        If nothing is given return (None, None)
        """
        key_value_match = self.key_value_expression.search(line_content)
        if key_value_match:
            key_match = key_value_match.group(1)
            value_match = key_value_match.group(2)
            logger.info(
                "key/value found in '" + line_content +
                "' with ('" + key_match + "', '" + value_match + "')"
            )

            return key_match, value_match

        key_only_match = self.key_expression.search(line_content)
        if key_only_match:
            logger.info("potential key found in '" + line_content + "'")
            return key_only_match.group(1), None

        return None, None

    def get_key_values(self, lines):
        """Extract all key values in the given lines."""
        key_values = []

        for line in lines:
            key, value = self.get_key_value(line)
            if key:
                key_values.append((key, value))

        return key_values

    def on_query_completions(self, view, prefix, locations):
        """"Execute if a auto completion is requested.

        can be either via typing or manual invoked with ctrl+space.

        This provides general variable extractions which are then
        passed to the domain specific worker completions.
        """
        for location in locations:
            # ignore non scope
            if not view.match_selector(location, self.scope):
                return None

            # ignore on comment lines
            cursor_line = view.line(location)
            line_content = view.substr(cursor_line)
            if self.comment_exp.search(line_content):
                logger.info("found comment")
                return None

            # find last occurance of the [] to determine the ini sections
            lines = self.get_lines_of_section_on_cursor(view, location)
            # filter empty lines
            lines = list(filter(None, lines))
            # filter comments
            lines = list(filter(lambda l: not self.comment_exp.search(l), lines))

            if not lines:
                logger.info("section is empty")
                size = view.size()
                content = view.substr(sublime.Region(0, size))
                sections = self.bracket_expression.findall(content)

                return self.section.get_key_context_completion(prefix, line_content, sections)

            # extract section
            first_line = lines[0]
            match = self.section_expression.search(first_line)

            # no section defined
            # TODO section suggestion
            # if not match:
            #     logger.info("no section found")
            #     size = view.size()
            #     content = view.substr(sublime.Region(0, size))
            #     sections = self.bracket_expression.findall(content)

            #     return self.section.get_key_context_completion(prefix, line_content, sections)
            section = match.group(1)

            key_match, value_match = self.get_key_value(line_content)
            key_values = self.get_key_values(lines)

            if value_match == "":
                logger.info("after equal trigger in '" + line_content + "'")
                # value trigger
                value_result = self.skin_rainmeter_section.get_value_context_completion(
                    section,
                    key_match
                )

                if value_result:
                    return value_result

            # only do key completion if we are in the key are
            # that means in front of the equal or no equal at all
            else:
                logger.info("before equal trigger in '" + line_content + "'")
                key_result = self.skin_rainmeter_section.get_key_context_completion(
                    prefix,
                    line_content,
                    section,
                    key_values
                )

                if key_result:
                    return key_result

                key_result = self.skin_metadata_section.get_key_context_completion(
                    prefix,
                    line_content,
                    section,
                    key_values
                )
                if key_result:
                    return key_result

            return None
