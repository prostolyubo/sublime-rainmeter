import os
import re
import yaml
import difflib

import sublime
import sublime_plugin

from Rainmeter import logger
from Rainmeter.completion.levenshtein import levenshtein

# abstract classs
class SectionAutoComplete:
	bracket_expression = re.compile(r'^\s*\[.+\]\s*$', re.MULTILINE)

	def get_current_section_content_start_index(self, start_content):
		matches = list(self.bracket_expression.finditer(start_content))

		if len(matches) > 0:
			last_match = matches[-1]
			return last_match.start()

		# no previous section found, hardly legal but who cares
		else:
			return 0

	def get_current_section_content_end_index(self, end_content, offset, end_index):
		matches = list(self.bracket_expression.finditer(end_content))
		if len(matches) > 0:
			first_match = matches[0]
			return first_match.start() + offset

		# no next section found
		else:
			return end_index


class SkinRainmeterSectionKeyAutoComplete(sublime_plugin.EventListener, SectionAutoComplete):
	
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
				print(e)

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
		logger.log(__file__, "__init__()", "SkinRainmeterSectionKeyAutoComplete initialized.")

	def get_lines_of_section_on_cursor(self, view, location):
		size = view.size()
		start_content = view.substr(sublime.Region(0, location))
		end_content = view.substr(sublime.Region(location, size))

		start_index = self.get_current_section_content_start_index(start_content)
		end_index = self.get_current_section_content_end_index(end_content, location, size)
		
		section = view.substr(sublime.Region(start_index, end_index))
		lines = section.splitlines()

		return lines

	def on_query_completions(self, view, prefix, locations):
		for location in locations:
			# checks if the current scope is correct so it is only called in the files with the correct scope
			# here is scope only rainmeter files
			if not view.match_selector(location, self.scope):
				return None

			# ignore on comment lines
			cursor_line = view.line(location)
			line_contents = view.substr(cursor_line)
			if self.comment_exp.search(line_contents):
				logger.log(__file__, "on_query_completions", "found comment")
				return None

			# find last occurance of the [] to determine the ini sections
			lines = self.get_lines_of_section_on_cursor(view, location)
			# filter empty lines
			lines = list(filter(None, lines))
			# filter comments
			lines = list(filter(lambda l: not self.comment_exp.search(l), lines))

			if not lines:
				logger.log(__file__, "on_query_completions", "section is empty")
				return None
		
			first_line = lines[0]

			# currently in the [rainmeter] section
			if not self.rm_exp.search(first_line):
				logger.log(__file__, "on_query_completions", "not in rainmeter section")
				return None

			# only do key completion if we are in the key are
			# that means in front of the equal or no equal at all
			if self.after_equal_exp.search(line_contents):
				# do value completion
				# TODO fix with cursor location
				logger.log(__file__, "on_query_completions", "after equal sign")
				return None

			# filter by already existing keys
			completions = []

			add_equal_to_completion = False
			for completion in self.all_completions:
				trigger, content = completion

				contained = 0
				
				for line in lines:
					regex = r"\s*(" + re.escape(content) + r")\s*\=?.*$"
					
					if re.match(regex, line, re.I):
						contained = 1
						break

				if contained == 0:
					completions.append(completion)

				# if cursor is on a completion key
				# then check for equals sign
				# if an equals sign already exists on that line
				# then check on position of cursor
				# if before the equals sign, wie only offer key suggestions
				# without the current key
				# if after the equals sign, we only offer value suggestions
				# if there is no equal sign and the prefix is a valid key,
				# then we offer an equal sign for auto completion
				
				# TODO does not work because of missing delimiter?
				# content_without_equal = r"\s*(" + re.escape(content) + r")\s*$"
				# content_with_equal = r"\s*(" + re.escape(content) + r")\s*=.*$"
				# no equal sign
				# if re.match(content_without_equal, line_contents, re.I) and not re.match(content_with_equal, line_contents, re.I):
				# 	logger.log(__file__, "equal detection", "found key '"+line_contents+"' on cursor without equal sign")
				# 	add_equal_to_completion = True

			# matches key, but no equal in line
			# if add_equal_to_completion:
			# 	equal_pair = [content + "=", content + "="]
			# 	completions.insert(0, equal_pair)
			# 	completions.insert(0, ["=", "="])
			# 	logger.log(__file__, "equal insertion", "please insert the equal sign in first place")
			
			# sort by levenshtein distance
			# diff = difflib.get_close_matches(prefix, completions, len(completions), 0)	
			sorted_completions = sorted(completions, key = lambda completion: levenshtein(completion[1], prefix))

			return sorted_completions, self.flags

		return None
