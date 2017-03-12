"""This module handles the skin section auto completion.

This provides the means to automatically add the base rainmeter sections
upon auto complete request with:

* [Rainmeter]
* [Metadata]
* [Variables]
* [Measure]
* [Meter]
* [MeterStyle]

This only activates if the file is empty or at least 2 new lines above the current caret.
"""

import yaml

import sublime

from .. import logger
from .levenshtein import levenshtein
from .compiler import compile_keys
from .yaml_content_reader import YamlContentReader


def str_equal_case_ignore(str1, str2):
    """Compare two strings ignoring the case."""
    return str1.casefold() == str2.casefold()


def sections_contain_section_id(sections, section_id):
    """Iterates through the sections container and checks if the section_id is in that container."""

    # value not used here
    for section in sections:
        if str_equal_case_ignore(section, section_id):
            return True

    return False


class SkinSectionAutoCompleter(YamlContentReader):  # pylint: disable=R0903; only provide one method

    """
    Ths class is the logical state holder for the auto completion suggestions.

    Upon the request the respective yaml file is parsed and converted into a logical
    representation of the completions. Depending on the prior information the completions
    can be filtered containing less entries.
    """

    def __get_completions(self):
        """IO access to the yaml file.

        Uses a yaml loader to parse it into a python object.
        """
        try:
            section_content = self._get_yaml_content("completion/", "section.yaml")
            section = yaml.load(section_content)

            return section

        except yaml.YAMLError as error:
            logger.error(error)
            return []

    def __lazy_initialize_completions(self):
        # use lazy initialization because else the API is not available yet
        if not self.all_completions:
            self.all_completions = self.__get_completions()
            self.all_key_completions = compile_keys(self.all_completions)

    def __filter_completions_by_sec(self, sections):
        # filter by already existing keys
        completions = []

        settings = sublime.load_settings("Rainmeter.sublime-settings")
        allow_duplicates = settings.get("allow_completion_section_duplicates", False)

        for completion in self.all_key_completions:
            # trigger is not used here
            section_id, display, content, unique = completion

            # we only need to search for duplicates
            # if we are having a unique section like [Rainmeter]
            # and not allow duplicates
            if unique and not allow_duplicates:
                contained = sections_contain_section_id(sections, section_id)

                if not contained:
                    completions.append((display, content))
            else:
                completions.append((display, content))

        return completions

    # only show our completion list because nothing else makes sense in this context
    flags = sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS

    all_completions = None
    all_key_completions = None

    def get_key_context_completion(self, prefix, line_content, sections):
        """Provide all possible sections without duplicates of unique ones."""
        # if section.casefold() != "Metadata".casefold():
        #     return None

        self.__lazy_initialize_completions()
        completions = self.__filter_completions_by_sec(sections)
        # no results, means all keys are used up
        if not completions:
            return None

        # only show sorted by distance if something was already typed
        # because distance to empty string makes no sense
        if line_content != "":
            # sort by levenshtein distance
            sorted_completions = sorted(
                completions,
                key=lambda completion: levenshtein(completion[1], prefix)
            )
            return sorted_completions, self.flags
        else:
            return completions, self.flags
