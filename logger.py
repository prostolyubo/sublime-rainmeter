from datetime import datetime
import os

import sublime

__log = None

'''
Called automatically from ST3 if plugin is loaded
# Is required now due to async call and ignoring sublime.* from main routine
'''

setting_key = "rainmeter_enable_logging"


def plugin_loaded():
    settings = __load_settings()
    settings.add_on_change(setting_key, __load_settings)

    info(__file__, "plugin_loaded()", "Logger succesfully loaded.")


def __load_settings():
    settings = sublime.load_settings("Rainmeter.sublime-settings")
    key = "rainmeter_enable_logging"

    global __log
    __log = settings.get(key, False)

    return settings


def info(file_path, function, string):
    if __log:
        _log("info", file_path, function, string)


def error(file_path, function, string):
    _log("error", file_path, function, string)


def _log(error_type, file_path, function, string):
    now = datetime.now()
    timestamp = now.strftime("%H:%M:%S.%f")[:-3]

    filename = os.path.basename(file_path)
    withoutext = os.path.splitext(filename)[0]

    print("[" + timestamp + "]", "[" + error_type + "]", withoutext + "." + function + ':', string)
