import yaml

import sublime

from .. import logger
from .levenshtein import levenshtein
from .yaml_content_reader import YamlContentReader


class SkinSectionAutoCompleter(YamlContentReader):

    def __get_completions(self):
        try:
            section_content = self._get_yaml_content("completion/", "section.yaml")
            section = yaml.load(section_content)

            return section

        except yaml.YAMLError as error:
            logger.error(__file__, "__get_completions(self)", error)
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

    # only show our completion list because nothing else makes sense in this context
    flags = sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS

    all_completions = None
    all_key_completions = None

    def get_key_context_completion(self, prefix, line_content, sections):
        # if section.casefold() != "Metadata".casefold():
        #     return None

        # use lazy initialization because else the API is not available yet
        if not self.all_completions:
            self.all_completions = self.__get_completions()
            self.all_key_completions = self.__get_compiled_key_completions(self.all_completions)

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
