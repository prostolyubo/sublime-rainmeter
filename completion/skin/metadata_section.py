"""This module is about skin/metadata section completion."""


import yaml

import sublime

# import own libs
from ... import logger
from ..levenshtein import levenshtein
from ..compiler import compile_keys
from ..yaml_content_reader import YamlContentReader


class SkinMetadataSectionAutoComplete(YamlContentReader):  # pylint: disable=R0903; only provide one method
    """This uses the provided YAML files to extract the possible completions."""

    def __get_completions(self):
        try:
            skin_metadata_section_content = self._get_yaml_content(
                "completion/skin/",
                "metadata_section.yaml"
            )
            skin_metadata_section = yaml.load(skin_metadata_section_content)

            return skin_metadata_section

        except yaml.YAMLError as error:
            logger.error(error)
            return []

    def __lazy_initialize_completions(self):
        # use lazy initialization because else the API is not available yet
        if not self.all_completions:
            self.all_completions = self.__get_completions()
            self.all_key_completions = compile_keys(self.all_completions)

    def __filter_completions_by_keys(self, keyvalues):
        """
        In Rainmeter a key can only be used once in a section statement.

        If you declare it twice this is a code smell.
        """
        # filter by already existing keys
        completions = []

        for completion in self.all_key_completions:
            dummy_key, display, content, dummy_unique = completion

            contained = 0
            # value not used here
            for key, _ in keyvalues:
                if key.casefold() == content.casefold():
                    contained = 1
                    break

            if contained == 0:
                completions.append((display, content))

        return completions

    # only show our completion list because nothing else makes sense in this context
    flags = sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS

    all_completions = None
    all_key_completions = None

    def get_key_context_completion(self, prefix, line_content, section, keyvalues):
        """
        Get context completion for a key.

        This implies that it was entered in a non-key row.
        """
        if section.casefold() != "Metadata".casefold():
            return None

        self.__lazy_initialize_completions()
        completions = self.__filter_completions_by_keys(keyvalues)

        # no results, means all keys are used up
        if not completions:
            logger.info("no results, all keys are used up")
            return None

        # only show sorted by distance if something was already typed
        # because distance to empty string makes no sense
        if line_content != "":
            # sort by levenshtein distance
            sorted_completions = sorted(
                completions, key=lambda completion: levenshtein(completion[1], prefix)
            )
            return sorted_completions, self.flags
        else:
            return completions, self.flags
