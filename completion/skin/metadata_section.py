import os.path
import yaml
import zipfile

import sublime

# import own libs
from Rainmeter import logger
from Rainmeter.completion.levenshtein import levenshtein


class SkinMetadataSectionAutoComplete:

    def __get_zip_content(self, path_to_zip, resource):
        if not os.path.exists(path_to_zip):
            return None

        ret_value = None

        with zipfile.ZipFile(path_to_zip) as zip_file:
            namelist = zip_file.namelist()
            if resource in namelist:
                ret_value = zip_file.read(resource)
                return ret_value.decode("utf-8")

        logger.error(__file__, "__get_zip_content(self, path_to_zip, resource)", "no zip content with resource '" + resource + "' found in .")
        return ret_value

    def __get_completions(self):
        try:
            skin_metadata_section_content = self.__get_metadata_section_content()
            skin_metadata_section = yaml.load(skin_metadata_section_content)

            return skin_metadata_section

        except yaml.YAMLError as error:
            logger.error(__file__, "get_completions", error)

    def __get_metadata_section_content(self):
        # trying git mode first
        parent_path = os.path.dirname(os.path.realpath(__file__))
        metadata_section_path = os.path.join(os.path.dirname(parent_path), "metadata_section.yaml")

        if os.path.exists(metadata_section_path):
            with open(metadata_section_path, 'r') as metadata_section_options_stream:
                return metadata_section_options_stream.read()

        # running in package mode
        else:
            packages_path = sublime.installed_packages_path()
            sublime_package = "Rainmeter.sublime-package"
            rm_package_path = os.path.join(packages_path, sublime_package)
            if os.path.exists(rm_package_path):
                resource = "completion/skin/metadata_section.yaml"
                return self.__get_zip_content(rm_package_path, resource)

        logger.error(__file__, "get_completions", "skin metadata section completion expected 'completion/skin/metadata_section.yaml' but does not exist in neither git nor package mode.")
        return None

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
                            logger.error(__file__, "get_compiled_value_completions", "unexpected length of '" + length + "' for option key '" + option_key + "'")

        return values

    def __init__(self):
        logger.info(__file__, "__init__(self)", "SkinMetadataSectionAutoComplete initialized.")

    # only show our completion list because nothing else makes sense in this context
    flags = sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS

    all_completions = None
    all_key_completions = None

    def get_key_context_completion(self, view, prefix, location, line_content, section, keyvalues):
        if section.casefold() != "Metadata".casefold():
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
        return None
