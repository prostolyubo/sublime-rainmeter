import os
import re
import yaml

import sublime

from Rainmeter import logger
from Rainmeter.completion.levenshtein import levenshtein

class SkinRainmeterSectionKeyAutoComplete:

	@staticmethod
	def get_completions():
		dir_path = os.path.dirname(os.path.realpath(__file__))

		with open(dir_path + "/skin_rainmeter_section.yaml", 'r') as skin_rainmeter_section_stream, open(dir_path + "/meters_general_image_options.yaml", 'r') as meters_general_image_options_stream:
			try:
				skin_rainmeter_section = yaml.load(skin_rainmeter_section_stream)
				meters_general_image_options = yaml.load(meters_general_image_options_stream)

				skin_rainmeter_section['options'].extend(meters_general_image_options)

				return skin_rainmeter_section

			except yaml.YAMLError as e:
				logger.error(__file__, "get_completions", e)

	@staticmethod
	def get_compiled_completions(options):
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
	scope = "source.rainmeter"
	
	all_completions = get_completions.__func__()

	comment_exp = re.compile(r'^\s*;.*')
	rm_exp = re.compile(r'^\s*\[Rainmeter\]\s*$', re.I)
	all_completions = get_compiled_completions.__func__(all_completions['options'])
	after_equal_exp = re.compile(r'^.*=\s*')

	def __init__(self):
		logger.info(__file__, "__init__()", "SkinRainmeterSectionKeyAutoComplete initialized.")

	def get_key_context_completion(self, view, prefix, location, line_content, section, keyvalues):
		if section != "Rainmeter":
			return None

		# filter by already existing keys
		completions = []

		for completion in self.all_completions:
			trigger, content = completion

			contained = 0
			for key, value in keyvalues:
				if key == content:
					contained = 1
					break

			if contained == 0:
				print("added: " + content)
				completions.append(completion)

		# sort by levenshtein distance
		sorted_completions = sorted(completions, key=lambda completion: levenshtein(completion[1], prefix))

		return sorted_completions, self.flags

	def get_value_context_completion(self, view, prefix, location, line_content, section, keyvalues):

		return None