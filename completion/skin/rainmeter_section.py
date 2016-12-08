""" This module does blabla """

import yaml

import sublime

# import own libs
from ... import logger
from ...completion.levenshtein import levenshtein
from ...completion.yaml_content_reader import YamlContentReader


class SkinRainmeterSectionAutoComplete(YamlContentReader):

    def __get_completions(self):
        try:
            rainmeter_section_content = self._get_yaml_content("completion/skin/", "rainmeter_section.yaml")
            skin_rainmeter_section = yaml.load(rainmeter_section_content)

            general_image_options_content = self._get_yaml_content("completion/meter/", "general_image_options.yaml")
            meters_general_image_options = yaml.load(general_image_options_content)

            skin_rainmeter_section.extend(meters_general_image_options)

            return skin_rainmeter_section

        except yaml.YAMLError as error:
            logger.error(__file__, "get_completions", error)
            return []

    def __get_compiled_key_completions(self, options):
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

    @staticmethod
    def get_compiled_value_completions(key, options):
        values = []

        for option in options:
            option_key = option['title']

            if option_key == key:
                if 'values' in option:
                    option_values = option['values']
                    for option_value in option_values:
                        length = len(option_value)

                        # case 1 is if only the key is provided, is generally the default case.
                        # Meaning is generally explained in the key
                        if length == 1:
                            pair = (option_value[0] + "\tDefault", option_value[0])
                            values.append(pair)

                        # case 2 is if only the key and the special hint is given
                        # means that the key is the value too
                        elif length == 2:
                            open_value_key, option_value_hint = option_value
                            pair = (open_value_key + "\t" + option_value_hint, open_value_key)
                            values.append(pair)
                        elif length == 3:
                            open_value_key, option_value_hint, option_value_value = option_value
                            pair = (open_value_key + "\t" + option_value_hint, option_value_value)
                            values.append(pair)
                        else:
                            logger.error(__file__,
                                         "get_compiled_value_completions",
                                         "unexpected length of '" + length + "' for option key '" + option_key + "'")

        return values

    # only show our completion list because nothing else makes sense in this context
    flags = sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS

    all_completions = None
    all_key_completions = None

    def get_key_context_completion(self, view, prefix, location, line_content, section, keyvalues):
        if section.casefold() != "Rainmeter".casefold():
            return None

        # use lazy initialization because else the API is not available yet
        if not self.all_completions:
            self.all_completions = self.__get_completions()
            self.all_key_completions = self.__get_compiled_key_completions(self.all_completions)

        # filter by already existing keys
        completions = []

        for completion in self.all_key_completions:
            trigger, content = completion

            contained = 0
            for key, value in keyvalues:
                if key.casefold() == content.casefold():
                    contained = 1
                    break

            if contained == 0:
                completions.append(completion)

        # no results, means all keys are used up
        if not completions:
            return None

        # only show sorted by distance if something was already typed because distance to empty string makes no sense
        if line_content != "":
            # sort by levenshtein distance
            sorted_completions = sorted(completions, key=lambda completion: levenshtein(completion[1], prefix))
            return sorted_completions, self.flags
        else:
            return completions, self.flags

    def get_value_context_completion(self, view, prefix, location, line_content, section, key_match, keyvalues):
        if section != "Rainmeter":
            return None

        # use lazy initialization because else the API is not available yet
        if not self.all_completions:
            self.all_completions = self.__get_completions()

        value_completions = SkinRainmeterSectionAutoComplete.get_compiled_value_completions(key_match, self.all_completions)
        if not value_completions:
            return None
        else:
            return value_completions, self.flags
