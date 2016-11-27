import os

import sublime

# import own libs
from Rainmeter import yaml
from Rainmeter import logger

class SkinMetadataSectionAutoComplete:

	@staticmethod
	def get_completions():
		dir_path = os.path.dirname(os.path.realpath(__file__))

		with open(dir_path + "/metadata_section.yaml", 'r') as skin_metadata_section_stream:
			try:
				skin_metadata_section = yaml.load(skin_metadata_section_stream)

				return skin_metadata_section

			except yaml.YAMLError as e:
				logger.error(__file__, "get_completions", e)

	@staticmethod
	def get_compiled_key_completions(options):
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
		# metadata_section = sublime.find_resources("metadata-section.yaml")
		# print(metadata_section)
		logger.info(__file__, "__init__(self)", "SkinMetadataSectionAutoComplete initialized.")

	# only show our completion list because nothing else makes sense in this context
	flags = sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS
	
	all_completions = get_completions.__func__()
	all_key_completions = get_compiled_key_completions.__func__(all_completions)

	def get_key_context_completion(self, view, prefix, location, line_content, section, keyvalues):
		if section.casefold() != "Metadata".casefold():
			return None

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