"""
This module is about the integration with the color picker.

The color picker can detect a color in a substring
and launch a tool to display the current color,
change it and thus also replace the old color.

It supports both ways Rainmeter defines color.

* RRGGBB
* RRGGBBAA
* RRR,GGG,BBB
* RRR,GGG,BBB,AAA

which is hexadecimal and decimal format.
"""

# TO DO spacing of decimal if required, but maybe too much overhead

import os
import re
import subprocess

import sublime
import sublime_plugin

from . import logger
from .color import converter

class RainmeterReplaceColorCommand(sublime_plugin.TextCommand): # pylint: disable=R0903; we only need one method
    """
    Replace a region with a text.

    This command is required because the edit objects passed to TextCommand
    are not transferable. We have to call this from the other command
    to get a valid edit object.
    """

    def run(self, edit, **args):
        """
        Method is provided by Sublime Text through the super class TextCommand.

        This is run automatically if you initialize the command
        through an "command": "rainmeter_replace_color" command
        with additional arguments:

        * low: start of the region to replace
        * high: end of the region to replace
        * output: text which will replace the region
        """
        low = args["low"]
        high = args["high"]
        output = args["output"]

        region = sublime.Region(low, high)
        original_str = self.view.substr(region)
        self.view.replace(edit, region, output)

        logger.info("Replacing '" + original_str + "' with '" + output + "'")

# encodes RRR,GGG,BBB,AAA with optional alpha channel and supporting all numbers from 0 to 999
# converter will check for 255
# numbers can be spaced anyway
DEC_COLOR_EXP = re.compile(r"(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*(?:,\s*(\d{1,3}))?")
# support lower and upper case hexadecimal with optional alpha channel
HEX_COLOR_EXP = re.compile(r"(?:[0-9a-fA-F]{2}){3,4}")


class RainmeterColorPickCommand(sublime_plugin.TextCommand): # pylint: disable=R0903; we only need one method
    """Sublime Text integration running this through an action."""

    def run(self, edit, **args):
        """
        Method is provided by Sublime Text through the super class TextCommand.

        This is run automatically if you initialize the command
        through an "command": "rainmeter_color_pick" command.
        """
        sublime.set_timeout_async(self.__run_picker, 0)

    def __get_first_selection(self):
        selections = self.view.sel()
        first_selection = selections[0]

        return first_selection

    def __get_selected_line_index(self):
        first_selection = self.__get_first_selection()
        selection_start = first_selection.begin()
        line_cursor = self.view.line(selection_start)
        line_index = line_cursor.begin()

        return line_index

    def __get_selected_line_content(self):
        first_selection = self.__get_first_selection()
        selection_start = first_selection.begin()
        line_cursor = self.view.line(selection_start)
        line_content = self.view.substr(line_cursor)

        return line_content

    @staticmethod
    def __get_selected_dec_or_none(caret, line_index, line_content):
        # catch case with multiple colors in same line
        for match in DEC_COLOR_EXP.finditer(line_content):
            low = line_index + match.start()
            high = line_index + match.end()

            # need to shift the caret to the current line
            if low <= caret <= high:
                rgba_raw = match.groups()
                rgba = [int(color) for color in rgba_raw if color is not None]
                hexes = converter.rgbs_to_hexes(rgba)
                hex_string = converter.hexes_to_string(hexes)
                with_alpha = converter.convert_hex_to_hex_with_alpha(hex_string)
                has_alpha = len(rgba) == 4

                return low, high, with_alpha, True, False, has_alpha

        return None

    @staticmethod
    def __get_selected_hex_or_none(caret, line_index, line_content):
        # we can find multiple color values in the same row
        # after iterating through the single elements
        # we can use start() and end() of each match to determine the length
        # and thus the area the caret had to be in,
        # to identify th1e one we are currently in
        for match in HEX_COLOR_EXP.finditer(line_content):
            low = line_index + match.start()
            high = line_index + match.end()

            if low <= caret <= high:
                hex_values = match.group(0)
                is_lower = hex_values.islower()
                # color picker requires RGBA
                with_alpha = converter.convert_hex_to_hex_with_alpha(hex_values)
                has_alpha = len(hex_values) == 8

                return low, high, with_alpha, False, is_lower, has_alpha
            else:
                logger.info(low)
                logger.info(high)
                logger.info(caret)

        return None

    def __get_selected_color_or_none(self):
        """Return None in case of not finding the color aka no color is selected."""
        caret = self.__get_first_selection().begin()
        line_index = self.__get_selected_line_index()
        line_content = self.__get_selected_line_content()

        # catch case with multiple colors in same line
        selected_dec_or_none = self.__get_selected_dec_or_none(caret, line_index, line_content)
        if selected_dec_or_none is not None:
            return selected_dec_or_none

        # if no match was iterated we process furthere starting here
        selected_hex_or_none = self.__get_selected_hex_or_none(caret, line_index, line_content)
        if selected_hex_or_none is not None:
            return selected_hex_or_none

        return None, None, None, None, None, None


    @staticmethod
    def __get_picker_path():
        # project_root = os.path.dirname(__file__)
        packages = sublime.packages_path()
        picker_path = os.path.join(
            packages,
            "User",
            "Rainmeter",
            "color",
            "picker",
            "ColorPicker_win.exe"
        )
        if not os.path.exists(picker_path):
            logger.error("color picker was suposed to be copied to '" + picker_path + "'")

        logger.info("found picker in '" + picker_path + "'")

        return picker_path

    def __run_picker(self):
        maybe_none = self.__get_selected_color_or_none()
        low, high, maybe_color, is_dec, is_lower, has_alpha = maybe_none

        # no color selected, we call the color picker and insert the color at that position
        color = "FFFFFFFF" if maybe_color is None else maybe_color

        picker_path = self.__get_picker_path()
        picker = subprocess.Popen(
            [picker_path, color],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False
        )
        output_channel, error_channel = picker.communicate()
        raw_output = output_channel.decode("utf-8")
        logger.info("output: " + raw_output)

        # checking for errors first
        error = error_channel.decode("utf-8")
        if error is not None and len(error) != 0:
            logger.error("Color Picker Error:\n" + error)
            return

        # len is 9 because of RGBA and '#' resulting into 9 characters
        if raw_output is not None and len(raw_output) == 9 and raw_output != 'CANCEL':
            logger.info("can write back: " + raw_output)

            # if no color is selected we need to modify the low and high to match the caret
            if all(value is None for value in maybe_none):
                caret = self.__get_first_selection().begin()
                low = caret
                high = caret
                output = raw_output[1:]
            else:
                output = self.__transform_raw_to_original_fmt(
                    raw_output,
                    is_dec,
                    has_alpha,
                    is_lower
                )

            self.view.run_command(
                "rainmeter_replace_color",
                {
                    "low": low,
                    "high": high,
                    "output": output
                }
            )

    @staticmethod
    def __transform_raw_to_original_fmt(raw, is_dec, has_alpha, is_lower):
        # cut output from the '#' because Rainmeter does not use # for color codes
        output = raw[1:]
        if is_dec:
            output = converter.convert_hex_str_to_rgba_str(output, has_alpha)

        # in case of hexadecimial representation
        else:
            # doing alpha calculation first so we do not need to catch ff and FF
            alpha = output[-2:]
            if not has_alpha and alpha is "FF":
                output = output[:-2]

            # it can be either originally in lower or upper case
            if is_lower:
                output = output.lower()

        return output

    def is_enabled(self, **args): #pylint: disable=R0201; sublime text API, no need for class reference
        """
        Return True if the command is able to be run at this time.

        The default implementation simply always returns True.
        """
        # Check if current syntax is rainmeter
        israinmeter = self.view.score_selector(self.view.sel()[0].a,
                                               "source.rainmeter")

        return israinmeter > 0

    def is_visible(self, **args):
        """."""
        if self.is_enabled():
            return True

        env = args.get("call_env", "")

        return env != "context"

def __require_path(path):
    if not os.path.exists(path):
        os.makedirs(path)

def plugin_loaded():
    packages = sublime.packages_path()
    colorpicker_dir = os.path.join(packages, "User", "Rainmeter", "color", "picker")

    __require_path(colorpicker_dir)

    colorpicker_exe = os.path.join(colorpicker_dir, "ColorPicker_win.exe")

    # could be already copied on a previous run
    need_picker_exe = not os.path.exists(colorpicker_exe)
    binary_picker = sublime.load_binary_resource(
        "Packages/Rainmeter/color/picker/ColorPicker_win.exe"
    )

    # could be a newer version of the color picker be there
    # only check if no newer is required since expensive
    # generally happens in consecutive calls without updates
    if not need_picker_exe:
        need_picker_exe = os.path.getsize(colorpicker_exe) != len(binary_picker)
    if need_picker_exe:
        logger.info(
            "Newer version of color picker found. Copying data over to '" + colorpicker_exe + "'"
        )
        with open(colorpicker_exe, "wb") as file:
            file.write(binary_picker)
    else:
        logger.info(
            "You are using the most current version of color picker. Continue loading..."
        )
