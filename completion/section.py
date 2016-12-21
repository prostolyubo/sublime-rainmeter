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
from .yaml_content_reader import YamlContentReader


class SkinSectionAutoCompleter(YamlContentReader): # pylint: disable=R0903; only provide one method
    """Ths class is the logical state holder for the auto completion suggestions.

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

    @staticmethod
    def __get_compiled_key_completions(options):
        """Completion can contain lots of duplicate information.

        For example the trigger is most of the time also the result.
        Only in case of a value attribute is that returned.
        It also takes hints into consideration for compilation.
        """
        keys = []
        for option in options:
            title = option['title'] + "\t" + option['hint']

            if 'value' in option:
                result = option['value']
            else:
                result = option['title']

            pair = (title, result)
            keys.append(pair)

        return keys

    def __lazy_initialize_completions(self):
        # use lazy initialization because else the API is not available yet
        if not self.all_completions:
            self.all_completions = self.__get_completions()
            self.all_key_completions = self.__get_compiled_key_completions(self.all_completions)

    def __filter_completions_by_sec(self, sections):
        # filter by already existing keys
        completions = []

        for completion in self.all_key_completions:
            # trigger is not used here
            _, content = completion

            contained = 0
            # value not used here
            for section in sections:
                if section.casefold() == content.casefold():
                    contained = 1
                    break

            if contained == 0:
                completions.append(completion)

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
        print("--- sections:", sections)
        completions = self.__filter_completions_by_sec(sections)
        print("--- completions:", completions)
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
