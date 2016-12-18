"""This module provides general methods for logging puprposes.

Basic operations are:

* info
* error

with these operations it is easier to track from where the information is printed
"""

import os

from datetime import datetime

import sublime

__LOG = None

'''
Called automatically from ST3 if plugin is loaded
# Is required now due to async call and ignoring sublime.* from main routine
'''

__SETTING_KEY = "rainmeter_enable_logging"


def plugin_loaded():
    """Will be called when sublime API is ready to use."""
    settings = __load_settings()
    settings.add_on_change(__SETTING_KEY, __load_settings)

    info(__file__, "plugin_loaded()", "Logger succesfully loaded.")


def __load_settings():
    settings = sublime.load_settings("Rainmeter.sublime-settings")

    global __LOG
    __LOG = settings.get(__SETTING_KEY, False)

    return settings


def info(file_path, function, string):
    """
    Display information about the current state it is in.

    Only shown if logging is enabled.
    """
    if __LOG:
        _log("info", file_path, function, string)


def error(file_path, function, string):
    """
    Display error states.

    Always shown because supposed not to reach that level.
    """
    _log("error", file_path, function, string)


def _log(error_type, file_path, function, string):
    now = datetime.now()
    timestamp = now.strftime("%H:%M:%S.%f")[:-3]

    filename = os.path.basename(file_path)
    withoutext = os.path.splitext(filename)[0]

    print("[" + timestamp + "]", "[" + error_type + "]", withoutext + "." + function + ':', string)
