"""Module for getting Rainmeter-specific paths"""

import os
import re

import sublime
import sublime_plugin

# own dependencies
from . import logger

from .path.program_path_provider import get_cached_program_path
from .path.setting_path_provider import get_cached_setting_path
from .path.program_drive_provider import get_cached_program_drive
from .path.plugin_path_provider import get_cached_plugin_path
from .path.addon_path_provider import get_cached_addon_path
from .path.skin_path_provider import get_cached_skin_path

from .completion.completion import ContextSensAutoCompletion


def get_current_path(filepath):
    """Get the value of the #CURRENTPATH# variable for the specified path.

    Returns None if the file path is not in the skins folder

    """

    filepath = os.path.normpath(filepath)

    skinspath = get_cached_skin_path()
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

    skinspath = get_cached_skin_path()
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

    skinspath = get_cached_skin_path()
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

    skinspath = get_cached_skin_path()
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
                 "#SKINSPATH#": get_cached_skin_path,
                 "#SETTINGSPATH#": get_cached_setting_path,
                 "#PROGRAMPATH#": get_cached_program_path,
                 "#PROGRAMDRIVE#": get_cached_program_drive,
                 "#ADDONSPATH#": get_cached_addon_path,
                 "#PLUGINSPATH#": get_cached_plugin_path}

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
        abso = os.path.join(get_cached_skin_path(), norm)
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


# Called automatically from ST3 if plugin is loaded
# Is required now due to async call and ignoring sublime.* from main routine
def plugin_loaded():
    # define variables from the global scope
    global settings

    settings = sublime.load_settings("Rainmeter.sublime-settings")

    logger.info(__file__, "plugin_loaded()", "#PROGRAMPATH#:\t\t" + get_cached_program_path())
    logger.info(__file__, "plugin_loaded()", "#PROGRAMDRIVE#:\t" + get_cached_program_drive())
    logger.info(__file__, "plugin_loaded()", "#SETTINGSPATH#:\t" + get_cached_setting_path())
    logger.info(__file__, "plugin_loaded()", "#SKINSPATH#:\t\t" + get_cached_skin_path())
    logger.info(__file__, "plugin_loaded()", "#PLUGINSPATH#:\t\t" + get_cached_plugin_path())
    logger.info(__file__, "plugin_loaded()", "#ADDONSPATH#:\t\t" + get_cached_addon_path())


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

    def on_query_completions(self, view, _, locations):
        """
        @param view
        @param prefix unused
        @param locations
        """
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


class CompletionProxy(sublime_plugin.EventListener):

    proxied_completion = None

    def __init__(self):
        self.proxied_completion = ContextSensAutoCompletion()

    def on_query_completions(self, view, prefix, locations):
        return self.proxied_completion.on_query_completions(view, prefix, locations)
