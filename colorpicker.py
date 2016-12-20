"""This module is about the integration with the color picker.

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
        self.view.replace(edit, region, output)


class RainmeterColorPickCommand(sublime_plugin.TextCommand): # pylint: disable=R0903; we only need one method
    """Sublime Text integration running this through an action."""

    def run(self, _):
        """
        Method is provided by Sublime Text through the super class TextCommand.

        This is run automatically if you initialize the command
        through an "command": "rainmeter_color_pick" command.
        """
        sublime.set_timeout_async(self.delegate_async, 0)

    def delegate_async(self):
        """Proxy for calling multiple methods."""
        self.__run_picker()

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

    def __get_selected_color_or_none(self):
        """Return None in case of not finding the color aka no color is selected."""
        caret = self.__get_first_selection().begin()
        line_index = self.__get_selected_line_index()
        line_content = self.__get_selected_line_content()

        dec_color_exp = re.compile(
            r"(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*(?:,\s*(\d{1,3}))?"
        )

        # catch case with multiple colors in same line
        for match in dec_color_exp.finditer(line_content):
            low = line_index + match.start()
            high = line_index + match.end()

            # need to shift the caret to the current line
            if low <= caret <= high:
                rgba_raw = match.groups()
                rgba = [int(color) for color in rgba_raw if color is not None]
                hexes = converter.rgbs_to_hexes(rgba)
                hex_string = converter.hexes_to_string(hexes)
                with_alpha = self.__convert_hex_to_hex_with_alpha(hex_string)
                has_alpha = len(rgba) == 4

                return low, high, with_alpha, True, False, has_alpha

        # if no match was iterated we process furthere starting here
        hex_color_exp = re.compile(r"(?:[0-9a-fA-F]{2}){3,4}")

        # we can find multiple color values in the same row
        # after iterating through the single elements
        # we can use start() and end() of each match to determine the length
        # and thus the area the caret had to be in,
        # to identify th1e one we are currently in
        for match in hex_color_exp.finditer(line_content):
            low = line_index + match.start()
            high = line_index + match.end()

            if low <= caret <= high:
                hex_values = match.group(0)
                is_lower = hex_values.islower()
                # color picker requires RGBA
                with_alpha = self.__convert_hex_to_hex_with_alpha(hex_values)
                has_alpha = len(hex_values) == 8

                return low, high, with_alpha, False, is_lower, has_alpha
            else:
                logger.info(__file__, "__get_selected_color_or_none(self)", low)
                logger.info(__file__, "__get_selected_color_or_none(self)", high)
                logger.info(__file__, "__get_selected_color_or_none(self)", caret)

        return None, None, None, None, None

    @staticmethod
    def __convert_hex_to_hex_with_alpha(hexes):
        """If no alpha value is provided it defaults to FF."""
        if len(hexes) == 6:
            return hexes + "FF"
        else:
            return hexes

    @staticmethod
    def __convert_hex_str_to_rgba_str(hex_string, has_alpha):
        """Provided 'FFFFFFFF' it should return 255, 255, 255, 255."""
        hexes = [hex_string[i:i+2] for i in range(0, len(hex_string), 2)]
        rgba = converter.hexes_to_rgbs(hexes)
        alpha = rgba[-1]
        if alpha is 255 and not has_alpha:
            rgba = rgba[:-1]
        rgba_str = converter.rgbs_to_string(rgba)

        return rgba_str

    def __run_picker(self):
        low, high, maybe_color, is_dec, is_lower, has_alpha = self.__get_selected_color_or_none()

        # no color selected, we call the color picker and insert the color at that position
        color = "FFFFFFFF" if maybe_color is None else maybe_color

        project_root = os.path.dirname(__file__)
        picker_path = os.path.join(project_root, "color", "picker", "ColorPicker_win.exe")
        picker = subprocess.Popen(
            [picker_path, color],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False
        )
        output_channel, error_channel = picker.communicate()
        raw_output = output_channel.decode("utf-8")
        logger.info(__file__, "__run_picker(self)", "output: " + raw_output)

        # checking for errors first
        error = error_channel.decode("utf-8")
        if error is not None and len(error) != 0:
            logger.error(__file__, "__run_picker(self)", "Color Picker Error:\n" + error_channel)
            return

        # len is 9 because of RGBA and '#' resulting into 9 characters
        if raw_output is not None and len(raw_output) == 9 and raw_output != 'CANCEL':
            logger.info(__file__, "__write_back(self)", "can write back: " + raw_output)

            # cut output from the '#' because Rainmeter does not use # for color codes
            output = raw_output[1:]
            if is_dec:
                output = self.__convert_hex_str_to_rgba_str(output, has_alpha)

            # in case of hexadecimial representation 
            # it can be either originally in lower or upper case
            elif is_lower:
                output = output.lower()
                if not has_alpha:
                    output = output[:-2]

            self.view.run_command(
                "rainmeter_replace_color",
                {
                    "low": low,
                    "high": high,
                    "output": output
                }
            )
            # TODO can convert it back to decimal?
            # TODO convert it back without alpha channel or with
            # TODO spacing of decimal
