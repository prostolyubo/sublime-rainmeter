"""This module is about the skin/rainmeter section handling."""


import yaml

import sublime

# import own libs
from ... import logger
from ..levenshtein import levenshtein
from ..compiler import compile_keys, compile_values
from ..yaml_content_reader import YamlContentReader


class SkinRainmeterSectionAutoComplete(YamlContentReader):  # pylint: disable=R0903; only provide one method
    """This uses the provided YAML files to extract the possible completions."""

    def __get_completions(self):
        try:
            rainmeter_section_content = self._get_yaml_content(
                "completion/skin/",
                "rainmeter_section.yaml"
            )
            skin_rainmeter_section = yaml.load(rainmeter_section_content)

            general_image_options_content = self._get_yaml_content(
                "completion/meter/",
                "general_image_options.yaml"
            )
            meters_general_image_options = yaml.load(general_image_options_content)

            skin_rainmeter_section.extend(meters_general_image_options)

            return skin_rainmeter_section

        except yaml.YAMLError as error:
            logger.error(error)
            return []

    # only show our completion list because nothing else makes sense in this context
    flags = sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS

    all_completions = None
    all_key_completions = None
    all_value_completions = None

    def get_key_context_completion(self, prefix, line_content, section, keyvalues):
        """Get a list of keys for the current context."""
        if section.casefold() != "Rainmeter".casefold():
            return None

        # use lazy initialization because else the API is not available yet
        if not self.all_completions:
            self.all_completions = self.__get_completions()
            self.all_key_completions = compile_keys(self.all_completions)

        # filter by already existing keys
        completions = []

        for completion in self.all_key_completions:
            dummy_key, display, content, dummy_unique = completion

            contained = 0
            # value not needed
            for key, _ in keyvalues:
                if key.casefold() == content.casefold():
                    contained = 1
                    break

            if contained == 0:
                completions.append((display, content))

        # no results, means all keys are used up
        if not completions:
            return None

        # only show sorted by distance if something was already typed
        # because distance to empty string makes no sense
        if line_content != "":
            # sort by levenshtein distance
            sorted_completions = sorted(
                completions, key=lambda c: levenshtein(c[1], prefix)
            )

            return sorted_completions, self.flags
        else:
            return completions, self.flags

    def get_value_context_completion(self, section, key_match):
        """Get context completion for a specified found key."""
        if section != "Rainmeter":
            return None

        # use lazy initialization because else the API is not available yet
        if not self.all_completions:
            self.all_completions = self.__get_completions()

        if not self.all_value_completions:
            self.all_value_completions = compile_values(self.all_completions)

        value_completions = self.all_value_completions[key_match]

        if not value_completions:
            logger.info("found no Rainmeter value completions for key '" + key_match + "' thus returning None")
            return None
        else:
            return value_completions, self.flags
