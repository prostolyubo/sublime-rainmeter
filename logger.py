from datetime import datetime
import os

import sublime

__log = None 

# Called automatically from ST3 if plugin is loaded
# Is required now due to async call and ignoring sublime.* from main routine
def plugin_loaded():
	global __log

	key = "rainmeter_enable_logging"

	settings = sublime.load_settings("Rainmeter.sublime-settings")
	__log = settings.get(key, False)
	settings.add_on_change(key, __load_settings)

	_log(__file__, "plugin_loaded()", "Logger succesfully loaded.")

def __load_settings():
	settings = sublime.load_settings("Rainmeter.sublime-settings")
	key = "rainmeter_enable_logging"

	global __log
	__log = settings.get(key, False)

def info(file, function, string):
	if __log:
		_log("info", file, function, string)

def error(file, function, string):
	_log("error", file, function, string)

def _log(type, file, function, string):
	now = datetime.now()
	timestamp = now.strftime("%H:%M:%S.%f")[:-3]

	filename = os.path.basename(file)
	withoutext = os.path.splitext(filename)[0]

	print("[" + timestamp + "]", "[" + type + "]" , withoutext + "." + function + ':', string)