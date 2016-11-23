"""Module for getting Rainmeter-specific paths"""

import os
import re
import io
import getpass
import platform
import winreg

import sublime
import sublime_plugin

# own dependencies
from . import logger

from .path.program_path_provider import get_cached_program_path
from .path.setting_path_provider import get_cached_setting_path
from .path.program_drive_provider import get_cached_program_drive

from .completion.skin.rainmeter_section import SkinRainmeterSectionKeyAutoComplete


def skins_path() -> str:
	"""Get the cached value of the #SKINSPATH# variable"""

	return _skins_path


def plugins_path() -> str:
	"""Get the cached value of the #PLUGINSPATH# variable"""

	return _plugins_path


def addons_path() -> str:
	"""Get the cached value of the #ADDONSPATH# variable"""

	return _addons_path


def get_skins_path():
	"""Get the value of the #SKINSPATH# variable"""

	# First try to load the value from the "rainmeter_skins_path" setting
	loaded_settings = sublime.load_settings("Rainmeter.sublime-settings")
	skinspath = loaded_settings.get("rainmeter_skins_path", None)

	# if it's found, return it
	# We trust the user to enter something meaningful here
	# and don't check anything.
	if skinspath:
		logger.info(__file__, "get_skins_path", "Skins path found in sublime-settings file.")
		return os.path.normpath(skinspath) + "\\"

	# If it's not set, try to detect it automagically

	rainmeterpath = get_cached_program_path()
	if not rainmeterpath:
		return

	settingspath = get_cached_setting_path()
	if not settingspath:
		return

	# First, try to read the SkinPath setting from Rainmeter.ini
	fhnd = io.open(os.path.join(settingspath, "Rainmeter.ini"))
	lines = fhnd.read()
	fhnd.close()

	# Find the skinspath setting in the file
	match = re.search(r"""(?imsx)

					 # Find the first [Rainmeter] section
					 (^\s*\[\s*Rainmeter\s*\]\s*$)
					 (.*?

						 # Find the "SkinPath" and "="
						 (^\s*SkinPath\s*=\s*

							 # Read until the next line ending and store
							 # in named group
							 (?P<skinpath>[^$]+?)\s*?$
						 )
					 ).*?

					 # All of this needs to happen before the next section
					 (?:^\s*\[\s*[^\[\]\s]+\s*\]\s*$)
					 """, lines)

	# if skinspath setting was found, return it
	if match:
		logger.info(__file__, "get_skins_path", "Skins path found in Rainmeter.ini.")
		return match.group("skinpath").strip().replace("/", "\\")

	# if it's not found in the settings file, try to guess it

	# If program path and setting path are equal, we have a portable
	# installation. In this case, the Skins folder is inside the rainmeter
	# path
	if os.path.samefile(rainmeterpath, settingspath):
		logger.info(__file__, "get_skins_path", "Skin path found in #PROGRAMPATH#" +
			 " because portable installation")
		return os.path.join(rainmeterpath, "Skins") + "\\"

	# If it's not a portable installation, we try looking into the "My
	# Documents" folder Since it could be relocated by the user, we have to
	# query its value from the registry
	try:
		regkey = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
								r"Software\Microsoft\Windows" +
								r"\CurrentVersion\Explorer" +
								r"\User Shell Folders")
		keyval = winreg.QueryValueEx(regkey, "Personal")

		pathrep = keyval[0]

		# The path could (and most likely, will) contain environment
		# variables that have to be expanded first
		pathrep = os.path.expandvars(pathrep)

		logger.info(__file__, "get_skins_path", "Guessed Skin path from My Documents" +
			 " location in registry")
		return os.path.join(pathrep, "Rainmeter\\Skins") + "\\"

	except WindowsError:
		pass

	# If the value could not be retrieved from the registry,
	# we try some educated guesses about default locations
	try:
		username = getpass.getuser()
	except Exception:
		logger.info(__file__, "get_skins_path", "Skins path could not be located." +
			 " Please set the \"skins_path\" setting in your Rainmeter" +
			 " settings file.")
		return
	else:
		# check if windows version is XP
		winversion = platform.version()
		if int(winversion[0]) < 6:
			mydocuments = os.path.join("C:\\Documents and Settings",
									   username,
									   "My Documents") + "\\"

			logger.info(__file__, "get_skins_path", "Found Windows XP or lower." +
				 " Skins path assumed to be " + mydocuments +
				 "Rainmeter\\Skins\\")
		else:
			mydocuments = os.path.join("C:\\Users",
									   username,
									   "Documents") + "\\"

			logger.info(__file__, "get_skins_path", "Found Windows Vista or higher." +
				 " Skins path assumed to be " + mydocuments +
				 "Rainmeter\\Skins\\")

		logger.info(__file__, "get_skins_path", "Skin path guessed from user name" +
			 " and Windows version")
		return os.path.join(mydocuments, "Rainmeter\\Skins") + "\\"


def get_plugins_path():
	"""Get the value of the #PLUGINSPATH# variable"""

	settingspath = get_cached_setting_path()
	if not settingspath:
		return
	return os.path.join(settingspath, "Plugins") + "\\"


def get_addons_path():
	"""Get the value of the #ADDONSPATH# variable"""

	settingspath = get_cached_setting_path()
	if not settingspath:
		return
	return os.path.join(settingspath, "Addons") + "\\"


def get_current_path(filepath):
	"""Get the value of the #CURRENTPATH# variable for the specified path.

	Returns None if the file path is not in the skins folder

	"""

	filepath = os.path.normpath(filepath)

	skinspath = skins_path()
	if not skinspath or not filepath.startswith(skinspath):
		logger.info(__file__, "get_current_path", "current path could not be found because" +
			 " either the skins path could not be found or the current file" +
			 " is not located in the skins path.")
		return

	if os.path.isfile(filepath):
		return os.path.dirname(filepath) + "\\"
	else:
		return filepath + "\\"


def get_root_config_path(filepath):
	"""Get the value of the #ROOTCONFIGPATH# variable for the specified path

	Returns None if the path is not in the skins folder

	"""

	filepath = os.path.normpath(filepath)

	skinspath = skins_path()
	if not skinspath or not filepath.startswith(skinspath):
		logger.info(__file__, "get_root_config_path", "root config path could not be found" +
			 " because either the skins path could not be found or the" +
			 " current file is not located in the skins path.")
		return

	relpath = os.path.relpath(filepath, skinspath)
	logger.info(__file__, "get_root_config_path",
		 os.path.join(skinspath, relpath.split("\\")[0]) + "\\")

	return os.path.join(skinspath, relpath.split("\\")[0]) + "\\"


def get_current_file(filepath):
	"""Get the value of the #CURRENTFILE# variable for the specified path

	Returns None if the path is not in the skins folder

	"""

	filepath = os.path.normpath(filepath)

	skinspath = skins_path()
	if not skinspath or not filepath.startswith(skinspath):
		logger.info(__file__, "get_current_file", "current file could not be found because" +
			 " either the skins path could not be found or the current" +
			 " file is not located in the skins path.")
		return

	if os.path.isfile(filepath):
		return os.path.basename(filepath)
	else:
		logger.info(__file__, "get_current_file", "specified path is not a file.")
		return


def get_current_config(filepath):
	"""Get the value of the #CURRENTCONFIG# variable for the specified path

	Returns None if the path is not in the skins folder

	"""

	filepath = os.path.normpath(filepath)

	skinspath = skins_path()
	if not skinspath or not filepath.startswith(skinspath):
		logger.info(__file__, "get_current_config", "current config could not be found" +
			 " because \either the skins path could not be found or the" +
			 " current file is not located in the skins path.")
		return

	if os.path.isfile(filepath):
		filepath = os.path.dirname(filepath)

	return os.path.relpath(filepath, skinspath)


def get_resources_path(filepath):
	"""Get the value of the #@# variable for the specified path

	Returns None if the path is not in the skins folder

	"""

	rfp = get_root_config_path(filepath)

	if not rfp:
		return
	logger.info(__file__, "get_resources_path", os.path.join(rfp, "@Resources") + "\\")
	return os.path.join(rfp, "@Resources") + "\\"


def replace_variables(string, filepath):
	"""Replace Rainmeter built-in variables and Windows environment variables
	in string.

	Replaces occurrences of the following variables in the string:
	#CURRENTFILE#
	#CURRENTPATH#
	#ROOTCONFIGPATH#
	#CURRENTCONFIG#
	#@#
	#SKINSPATH#
	#SETTINGSPATH#
	#PROGRAMPATH#
	#PROGRAMDRIVE#
	#ADDONSPATH#
	#PLUGINSPATH#
	Any Windows environment variables (like %APPDATA%)
	filepath must be a skin file located in a subdirectory of the skins folder

	"""

	# lambdas for lazy evaluation
	variables = {"#CURRENTFILE#": lambda: get_current_file(filepath),
				 "#CURRENTPATH#": lambda: get_current_path(filepath),
				 "#ROOTCONFIGPATH#": lambda: get_root_config_path(filepath),
				 "#CURRENTCONFIG#": lambda: get_current_config(filepath),
				 "#@#": lambda: get_resources_path(filepath),
				 "#SKINSPATH#": lambda: skins_path(),
				 "#SETTINGSPATH#": lambda: get_cached_setting_path(),
				 "#PROGRAMPATH#": lambda: get_cached_program_path(),
				 "#PROGRAMDRIVE#": lambda: get_cached_program_drive(),
				 "#ADDONSPATH#": lambda: addons_path(),
				 "#PLUGINSPATH#": lambda: plugins_path()}

	pattern = re.compile("(?i)" + "|".join(list(variables.keys())))
	# replace Rainmeter variables
	repl = pattern.sub(lambda x: variables[x.group().upper()](),
					   string)
	# expand windows environment variables
	repl = os.path.expandvars(repl)
	return repl


def make_path(string, filepath):
	"""Make the string into an absolute path of an existing file or folder,

	replacing Rainmeter built-in variables relative to the file specified in
	filepath (see replace_variables()) will return None if the file or folder
	doesn't exist, or if string is None or empty.

	"""

	if not string:
		return None

	repl = replace_variables(string, filepath)
	norm = os.path.normpath(repl)

	# For relative paths, try folder of current file first

	if not os.path.isabs(norm):
		curpath = get_current_path(filepath)
		if curpath:
			abso = os.path.join(curpath, norm)
		else:
			abso = os.path.join(os.path.dirname(filepath), norm)

		if os.path.exists(abso):
			return abso

		# if that doesn't work, try relative to skins path
		# (for #CURRENTCONFIG#)
		abso = os.path.join(skins_path(), norm)
		if os.path.exists(abso):
			return abso
	# for absolute paths, try opening containing folder if file does not exist
	else:
		if os.path.exists(norm):
			return norm

		if os.path.exists(os.path.dirname(norm)):
			return os.path.dirname(norm)

	return


# Initialize Module
# Global Variables
settings = None

_skins_path = None
_plugins_path = None
_addons_path = None


# Called automatically from ST3 if plugin is loaded
# Is required now due to async call and ignoring sublime.* from main routine
def plugin_loaded():
	# define variables from the global scope
	global settings

	global _skins_path
	global _plugins_path
	global _addons_path

	settings = sublime.load_settings("Rainmeter.sublime-settings")

	# Cache the paths
	_skins_path = get_skins_path()
	_plugins_path = get_plugins_path()
	_addons_path = get_addons_path()

	logger.info(__file__, "plugin_loaded()", "#PROGRAMPATH#:\t" + get_cached_program_path())
	logger.info(__file__, "plugin_loaded()", "#PROGRAMDRIVE#:\t" + get_cached_program_drive())
	logger.info(__file__, "plugin_loaded()", "#SETTINGSPATH#:\t" + get_cached_setting_path())
	logger.info(__file__, "plugin_loaded()", "#SKINSPATH#:\t\t" + skins_path())
	logger.info(__file__, "plugin_loaded()", "#PLUGINSPATH#:\t\t" + plugins_path())
	logger.info(__file__, "plugin_loaded()", "#ADDONSPATH#:\t\t" + addons_path())

class MeterAutoComplete(sublime_plugin.EventListener):

	# only show our completion list because nothing else makes sense in this context
	flags = sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS
	scope = "source.rainmeter"

	comment_exp = re.compile(r'^\s*;.*')
	meter_exp = re.compile(r'^\s*')

	completions = [
		# measures
		(re.compile(r'^\s*Measure\s*=\s*'), [
			# key, value
			["Calc", "Calc"],
			["CPU", "CPU"],
			["FreeDiskSpace", "FreeDiskSpace"],
			["Loop", "Loop"],

			# memory measure
			["Memory", "Memory"],
			["PhysicalMemory", "PhysicalMemory"],
			["SwapMemory", "SwapMemory"],

			# net measure
			["NetIn", "NetIn"],
			["NetOut", "NetOut"],
			["NetTotal", "NetTotal"],

			["Plugin", "Plugin"],
			["Registry", "Registry"],
			["Script", "Script"],
			["String", "String"],
			["Time", "Time"],
			["Uptime", "Uptime"]
		]),

		# meters
		(re.compile(r'^\s*Meter\s*=\s*'), [
			# key, value
			["Bar", "Bar"],
			["Bitmap", "Bitmap"],
			["Button", "Button"],
			["Histogram", "Histogram"],
			["Image", "Image"],
			["Line", "Line"],
			["Rotator", "Rotator"],
			["Roundline", "Roundline"],
			["Shape", "Shape"],
			["String", "String"]
		]),
		# general options

		# bar
		# bar orientation
		(re.compile(r'^\s*BarOrientation\s*=\s*'), [
			# key, value
			["Horizontal", "Horizontal"],
			["Vertical\tDefault", "Vertical"]
		]),

		# bar flip
		(re.compile(r'^\s*Flip\s*=\s*'), [
			# key, value
			["0\tDefault", "0"],
			["1\tBar is flipped", "1"]
		]),

		# bitmap

		# button
		# histogram
		# image
		# line
		# rotator
		# roundline
		# shape
		# string

		# plugins
		(re.compile(r'^\s*Plugin\s*=\s*'), [
			# key, value
			["ActionTimer", "ActionTimer"],
			["AdvancedCPU", "AdvancedCPU"],
			["AudioLevel", "AudioLevel"],
			["CoreTemp", "CoreTemp"],
			["FileView", "FileView"],
			["FolderInfo", "FolderInfo"],
			["InputText", "InputText"],
			["iTunes", "iTunesPlugin"],
			["MediaKey", "MediaKey"],
			["NowPlaying", "NowPlaying"],
			["PerfMon", "PerfMon"],
			["Ping", "PingPlugin"],
			["Power", "PowerPlugin"],
			["Process", "Process"],
			["Quote", "QuotePlugin"],
			["RecycleManager", "RecycleManager"],
			["ResMon", "ResMon"],
			["RunCommand", "RunCommand"],
			["SpeedFan", "SpeedFanPlugin"],
			["SysInfo", "SysInfo"],
			["WebParser", "WebParser"],
			["WiFiStatus", "WiFiStatus"],
			["Win7Audio", "Win7AudioPlugin"],
			["WindowMessage", "WindowMessagePlugin"]
		]),

		

	]

	def on_query_completions(self, view, prefix, locations):
		for location in locations:
			# checks if the current scope is correct so it is only called in the files with the correct scope
			# here is scope only rainmeter files
			if view.match_selector(location, self.scope):
				# find last occurance of the [] to determine the ini sections
				line = view.line(location)
				line_contents = view.substr(line)

				# starts with Measure, followed by an equal sign
				for exp, elements in self.completions:
					if exp.search(line_contents):
						return elements, self.flags
		return None

class Bootstrap(sublime_plugin.EventListener):

	# only show our completion list because nothing else makes sense in this context
	flags = sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS

	skin_rainmeter_section = None

	scope = "source.rainmeter"

	# comments are specified by ';'
	comment_exp = re.compile(r'^\s*;.*')

	# enable searching for [] in multiline environment
	bracket_expression = re.compile(r'^\s*\[.+\]\s*$', re.MULTILINE)
	section_expression = re.compile(r'^\s*\[(.+)\]\s*$', re.I)
	key_expression = re.compile(r'^\s*(.+)\s*\=?\s*(.*?)\s*$', re.MULTILINE)
	key_value_expression = re.compile(r'^\s*(.+?)\s*\=\s*(.*?)\s*$', re.MULTILINE)

	def __init__(self):
		self.skin_rainmeter_section = SkinRainmeterSectionKeyAutoComplete()

	def get_lines_of_section_on_cursor(self, view, location, prefix):
		size = view.size()
		start_content = view.substr(sublime.Region(0, location))
		end_content = view.substr(sublime.Region(location, size))

		start_index = self.get_current_section_content_start_index(start_content)
		end_index = self.get_current_section_content_end_index(end_content, location, size)

		section = view.substr(sublime.Region(start_index, end_index))
		lines = section.splitlines()

		return lines

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

	def get_key_value(self, line_content):
		key_value_match = self.key_value_expression.search(line_content)
		if key_value_match:
			logger.info(__file__, "on_query_completions", "key/value found in '" + line_content + "'")
			key_match = key_value_match.group(1)
			value_match = key_value_match.group(2)

			return key_match, value_match

		key_only_match = self.key_expression.search(line_content)
		if key_only_match:
			logger.info(__file__, "on_query_completions", "potential key found in '" + line_content + "'")
			return key_only_match.group(1), None

		return None, None

	def get_key_values(self, lines):
		key_values = []

		for line in lines:
			key, value = self.get_key_value(line)
			if key:
				key_values.append((key, value))

		return key_values

	def on_query_completions(self, view, prefix, locations):
		for location in locations:
			# ignore non scope
			if not view.match_selector(location, self.scope):
				return None

			# ignore on comment lines
			cursor_line = view.line(location)
			line_content = view.substr(cursor_line)
			if self.comment_exp.search(line_content):
				logger.info(__file__, "on_query_completions", "found comment")
				return None

			# find last occurance of the [] to determine the ini sections
			lines = self.get_lines_of_section_on_cursor(view, location, prefix)
			# filter empty lines
			lines = list(filter(None, lines))
			# filter comments
			lines = list(filter(lambda l: not self.comment_exp.search(l), lines))

			if not lines:
				logger.info(__file__, "bootstrap.on_query_completions", "section is empty")
				return None

			# extract section
			first_line = lines[0]
			match = self.section_expression.search(first_line)

			# no section defined
			# TODO section suggestion
			if not match:
				logger.info(__file__, "on_query_completions", "no section found")
				return None
			section = match.group(1)

			key_match, value_match = self.get_key_value(line_content)
			key_values = self.get_key_values(lines)

			if value_match == "":
				logger.info(__file__, "on_query_completions", "after equal trigger in '" + line_content + "'")
				# value trigger
				value_result = self.skin_rainmeter_section.get_value_context_completion(view, prefix, location, line_content, section, key_match, key_values)
				if value_result:
					return value_result
			
			# only do key completion if we are in the key are
			# that means in front of the equal or no equal at all
			else:
				logger.info(__file__, "on_query_completions", "before equal trigger in '" + line_content + "'")
				key_result = self.skin_rainmeter_section.get_key_context_completion(view, prefix, location, line_content, section, key_values)
				if key_result:
					return key_result
			
			return None
