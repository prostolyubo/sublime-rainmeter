"""
This plugin is the entry point to the smart completion module.

Basic functionalities are kontext detection and offer only meaningful auto completion options
instead of every of them.
"""


import re

import sublime
import sublime_plugin

from .completion.completion import ContextSensAutoCompletion


class MeterAutoComplete(sublime_plugin.EventListener):
    # pylint: disable=R0903; Ignore too few methods because we have a super class.
    """
    This class is an implementation of the sublime plugin EventListener.

    This is a temporary solution for the completion module.
    It provides some basic smart completions like:

    * measures
    * plugins
    * meters
    * some attributes
    """

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
            ["MediaKey", "MediaKey"],

            # memory measure
            ["Memory", "Memory"],
            ["PhysicalMemory", "PhysicalMemory"],
            ["SwapMemory", "SwapMemory"],

            # net measure
            ["NetIn", "NetIn"],
            ["NetOut", "NetOut"],
            ["NetTotal", "NetTotal"],

            ["NowPlaying", "NowPlaying"],
            ["Plugin", "Plugin"],
            ["RecycleManager", "RecycleManager"],
            ["Registry", "Registry"],
            ["Script", "Script"],
            ["String", "String"],
            ["Time", "Time"],
            ["Uptime", "Uptime"],
            ["WebParser", "WebParser"]
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
            ["PerfMon", "PerfMon"],
            ["Ping", "PingPlugin"],
            ["Power", "PowerPlugin"],
            ["Process", "Process"],
            ["Quote", "QuotePlugin"],
            ["ResMon", "ResMon"],
            ["RunCommand", "RunCommand"],
            ["SpeedFan", "SpeedFanPlugin"],
            ["SysInfo", "SysInfo"],
            ["WiFiStatus", "WiFiStatus"],
            ["Win7Audio", "Win7AudioPlugin"],
            ["WindowMessage", "WindowMessagePlugin"]
        ]),
    ]

    def on_query_completions(self, view, _, locations):
        """
        Called upon auto completion request.

        :param view: current view upon the text buffer
        :param _: unused prefix
        :param locations: selected regions
        """
        for location in locations:
            # checks if the current scope is correct
            # so it is only called in the files with the correct scope
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
    # pylint: disable=R0903; Ignore too few methods because we have a super class.
    """
    Proxy the sublime plugin EventListener to the internal completion module.

    The module handles all the request and routes them to the correct submodules.
    This prevents all the single modules from polluting the root directory.
    """

    def __init__(self):
        """Initialize the proxy."""
        self.proxied_completion = ContextSensAutoCompletion()

    def on_query_completions(self, view, prefix, locations):
        """Pass query completion to proxy."""
        return self.proxied_completion.on_query_completions(view, prefix, locations)
