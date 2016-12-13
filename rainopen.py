"""Module for opening paths containing Rainmeter-specific or Windows environment variables."""

import os
import re
import threading

import sublime
import sublime_plugin

from . import rainmeter
from . import logger


# Files to open with sublime instead of the system default
SETTINGS = sublime.load_settings("Rainmeter.sublime-settings")
DEF_EXTS = SETTINGS.get("rainmeter_default_open_sublime_extensions", "")

if DEF_EXTS is not None:
    DEF_EXTS = DEF_EXTS.strip().strip(r"|").strip()
else:
    DEF_EXTS = ""

ADD_EXTS = SETTINGS.get("rainmeter_open_sublime_extensions", "")

if ADD_EXTS is not None:
    ADD_EXTS = ADD_EXTS.strip().strip(r"|").strip()
else:
    ADD_EXTS = ""

SUBLIME_FILES = re.compile("(?i).*\\.(" + ADD_EXTS + "|" + DEF_EXTS + ")\\b")


def open_path(path, transient=False):
    """Try to open a path.

    A path could be opened either as:

    * a file or folder path or
    * URL in the system default application, or
    * in Sublime if it's a text file.

    Use transient=True to open a file in Sublime without assigning it a tab.
    A tab will be created once the buffer is modified.

    Will return False if the path doesn't exist in the file system, and
    True otherwise.
    """
    if not path:
        return False

    if not os.path.exists(path):
        return False

    sublime.set_timeout(lambda: sublime.status_message("Opening " + path), 10)
    if SUBLIME_FILES.search(path):
        if transient:
            sublime.set_timeout(
                lambda: sublime.active_window().open_file(path,
                                                          sublime.TRANSIENT),
                10)
        else:
            sublime.set_timeout(
                lambda: sublime.active_window().open_file(path),
                10)
    else:
        os.startfile(path)

    return True


def open_url(url):
    """Try opening a url with the system default for urls.

    Will return False if it's not a url, and True otherwise.
    """
    if re.match(r"(?i)(https?|ftp)://", url.strip()):
        os.startfile(url)
        sublime.set_timeout(lambda: sublime.status_message("Opening " + url),
                            10)
        return True
    else:
        return False


class TryOpenThread(threading.Thread):
    """A wrapper method to handle threading for opening line embedded URLs."""

    def __init__(self, line, region, opn):
        """Construct a thread for opening URL embedded in a line."""
        self.line = line
        self.region = region
        self.opn = opn
        threading.Thread.__init__(self)

    def run(self):
        """Run the thread."""
        # 1. Selected text
        selected = self.line[self.region.a:self.region.b]
        if self.opn(selected):
            logger.info(
                __file__,
                "TryOpenThread.run(self)",
                "Open selected text"
            )
            return

        # 2. String enclosed in double quotes

        # Find the quotes before the current point (if any)
        lastquote = self.region.a - 1
        while lastquote >= 0 and self.line[lastquote] != "\"":
            lastquote -= 1

        if not lastquote < 0 and self.line[lastquote] == "\"":
            # Find the quote after the current point (if any)
            nextquote = self.region.b
            while nextquote == len(self.line) or self.line[nextquote] != "\"":
                nextquote += 1

            if not nextquote == len(self.line) \
                    and self.line[nextquote] == "\"":
                string = self.line[lastquote: nextquote].strip("\"")
                if self.opn(string):
                    logger.info(
                        __file__,
                        "TryOpenThread.run",
                        "Open string enclosed in quotes: " + string
                    )
                    return

        # 3. Region from last whitespace to next whitespace

        # Find the space before the current point (if any)
        lastspace = self.region.a - 1
        while lastspace >= 0 \
                and self.line[lastspace] != " " \
                and self.line[lastspace] != "\t":
            lastspace -= 1

        # Set to zero if nothing was found until the start of the line
        if lastspace < 0:
            lastspace = 0

        if lastspace == 0 \
                or self.line[lastspace] == " " \
                or self.line[lastspace] == "\t":
            # Find the space after the current point (if any)
            nextspace = self.region.b
            while nextspace < len(self.line) \
                    and self.line[nextspace] != " " \
                    and self.line[nextspace] != "\t":
                nextspace += 1

            if nextspace >= len(self.line) \
                    or self.line[nextspace] == " " \
                    or self.line[nextspace] == "\t":
                string = self.line[lastspace: nextspace].strip()
                if self.opn(string):
                    logger.info(
                        __file__,
                        "TryOpenThread.run",
                        "Open string enclosed in whitespace: " + string
                    )
                    return

        # 4. Everything after the first \"=\" until the end
        # of the line (strip quotes)
        mtch = re.search(r"=\s*(.*)\s*$", self.line)
        if mtch and self.opn(mtch.group(1).strip("\"")):
            logger.info(
                __file__,
                "TryOpenThread.run",
                "Open text after \"=\": " +
                mtch.group(1).strip("\"")
            )
            return

        # 5. Whole line (strip comment character at start)
        stripmatch = re.search(r"^[ \t;]*?([^ \t;].*)\s*$", self.line)
        if self.opn(stripmatch.group(1)):
            logger.info(
                __file__,
                "TryOpenThread.run",
                "Open whole line: " +
                stripmatch.group(1)
            )
            return


class RainmeterOpenPathsCommand(sublime_plugin.TextCommand):
    """Try to open paths on lines in the current selection.

    Will try to open paths to files, folders or URLs on each line in the
    current selection. To achieve this, the following substrings of each line
    intersecting the selection are tested:

    1. The string inside the selection
    2. The string between possible quotes preceding and following the
       selection, if any
    3. The string between the preceding and following whitespace
    4. Everything after the first "=" on the line until the end of the line
    5. The whole line, stripped of preceding semicolons
    """

    def __split_selection_by_new_lines(self, selection):
        # Split all regions into individual segments on lines (using nicely
        # confusing python syntax).
        return [
            j for i in [
                self.view.split_by_newlines(region)
                for region in selection
            ]
            for j in i
        ]

    def __open_each_line_by_thread(self, lines):
        """Identify segments in selected lines and tries to open them each in a new thread.

        This can be resource intensive.
        """
        fnm = self.view.file_name()

        def opn(string):
            """Simple callback method to apply multiple opening operations.

            An URL can be either external or internal and thus is opened differently.
            """
            opened = open_path(rainmeter.make_path(string, fnm)) or open_url(string)
            if opened:
                logger.info(
                    __file__,
                    "run(self, edit)",
                    "found file or url '" + string + "' to open"
                )

        for linereg in lines:
            wholeline = self.view.line(linereg)
            thread = TryOpenThread(self.view.substr(wholeline),
                                   sublime.Region(linereg.a - wholeline.a,
                                                  linereg.b - wholeline.a),
                                   opn)
            thread.start()

    def run(self, _):
        """Detect various scenarios of file paths and try to open them one after the other.

        @param edit unused
        """
        selection = self.view.sel()
        lines = self.__split_selection_by_new_lines(selection)

        loaded_settings = sublime.load_settings("Rainmeter.sublime-settings")
        max_open_lines = loaded_settings.get("rainmeter_max_open_lines", 40)

        # Refuse if too many lines selected to avoid freezing

        if len(lines) > max_open_lines:
            accept = sublime.ok_cancel_dialog(
                "You are trying to open " +
                str(len(lines)) + " lines.\n" +
                "That's a lot, and could take some time. Try anyway?")
            if not accept:
                return

        self.__open_each_line_by_thread(lines)

    def is_enabled(self):
        """Check if current syntax is rainmeter."""
        israinmeter = self.view.score_selector(self.view.sel()[0].a,
                                               "source.rainmeter")

        return israinmeter > 0

    def is_visible(self):
        """It is visible if it is in Rainmeter scope."""
        return self.is_enabled()
