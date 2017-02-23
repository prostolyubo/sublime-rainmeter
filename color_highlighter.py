import codecs
import colorsys
import os
import re

import sublime
import sublime_plugin

from . import logger
from .color import converter


def __create_if_not_exists(path):
    """
    create directory if not exists

    Parameter:
    ----------
    path: os.path conform string
    """
    if not os.path.exists(path):
        os.makedirs(path)
        logger.info(__file__, "__create_if_not_exists(path)", "created path '" + path + "' because it did not exist.")


def plugin_loaded():
    user_theme_path = os.path.join(sublime.packages_path(), "User", "Rainmeter", "theme")

    __create_if_not_exists(user_theme_path)


def plugin_unloaded():
    print("unloaded")


class ColorHighlighterEventListener(sublime_plugin.EventListener):

    def on_new(self, view):
        pass

    def on_clone(self, view):
        pass

    def on_load(self, view):
        pass

    def on_close(self, view):
        pass

    def on_selection_modified(self, view):
        pass

    def on_modified(self, view):
        pass

    def on_post_save(self, view):
        pass

    def on_activated(self, view):
        pass

    def on_query_context(self, view, key, op, operand, match_all):
        pass


class ColorCache(object):

    def __init__(self):
        self.color_cache = {}
        self.color_cache_candidates = []

    def __register_color_cache_candidate(self, color):
        """
        Register color as a color cache candidate.

        This is an abstraction to hide the internal collection.
        """

    def add_colors(self, colors):
        for color in colors:
            self.__register_color_cache_candidate(color)

        return self.__flush_changes()

    def __found_color_changes(self):
        any_found = False
        for candidate in self.color_cache_candidates:
            if candidate in self.color_cache.keys():
                continue

            self.color_cache[candidate] = self.__push_lumiosity(candidate)
            any_found = True

        return any_found

    def __push_lumiosity(rgb_hex_color):
        r = int(rgb_hex_color[1:3], 16) / 255.0
        g = int(rgb_hex_color[3:5], 16) / 255.0
        b = int(rgb_hex_color[5:7], 16) / 255.0
        (h, l, s) = colorsys.rgb_to_hls(r, g, b)

        pushed_lumiosity = max(l, .15)

        pushed_rgbs = colorsys.hls_to_rgb(h, pushed_lumiosity, s)
        pushed_hexes = converter.rgbs_to_hexes(pushed_rgbs)

        return converter.hexes_to_string(pushed_hexes)

    def __flush_changes(self):
        """."""
        if self.__found_color_changes():
            # load color scheme
            # search for
            pass


class ColorHighlighter(sublime_plugin.EventListener):

    # def on_activated_async(self):
    #     current_pos = view.sel()[0].begin()

    #     # only handle rainmeter files
    #     if not view.match_selector(current_pos, "source.rainmeter"):
    #         return

    #     self.__update_color_scheme()

    # def __update_color_scheme(self):
        # scheme_path, scheme_name = self.current_color_scheme()
        # print(self.__get_current_color_scheme())

    def __colors_to_xml(self, colors):
        """
        converts a iterable colors to a string containing the new definitions

        Parameters:
        -----------
        :colors: to be converted iterable colors
        """
        xml = []

        for color in colors:
            xml.append(self.__color_to_xml(color))

        return "".join(xml)

    def __color_to_xml(self, color):
        return '''
        <dict>
            <key>scope</key>
            <string>constant.numeric.color.{foreground}</string>
            <key>settings</key>
            <dict>
                <key>foreground</key>
                <string>#{foreground}</string>
            </dict>
        </dict>
        '''.format(foreground=color)

    def __get_current_color_scheme(self, view):
        """
        Returns (absolute color scheme path, scheme name).
        """
        scheme_relative_path = view.settings().get('color_scheme')
        scheme_name, _ = os.path.splitext(os.path.basename(scheme_relative_path))
        sublime_base_path = os.path.dirname(sublime.packages_path())
        scheme_path = os.path.join(sublime_base_path, scheme_relative_path)

        return scheme_path, scheme_name

    def on_load_async(self, view):
        current_pos = view.sel()[0].begin()
        if not view.match_selector(current_pos, "source.rainmeter"):
            return

        print("---", "loaded:", view)

    def on_activated_async(self, view):
        if len(view.sel()) > 0:
            current_pos = view.sel()[0].begin()
            if not view.match_selector(current_pos, "source.rainmeter"):
                return

        # print("---", "activated:", view, "buffer-id:", view.buffer_id())

    def on_modified(self, view):
        # only handle rainmeter files
        current_pos = view.sel()[0].begin()
        if not view.match_selector(current_pos, "source.rainmeter"):
            return

        # print("---", "modified:", view)

    def on_selection_modified_async(self, view):
        """
        User interaction: user selects something in the :view: view
        """

        # selections generally mean something different, we only handle clicks
        if not view.sel()[0].empty():
            return

        # only handle rainmeter files
        current_pos = view.sel()[0].begin()
        if not view.match_selector(current_pos, "source.rainmeter"):
            return
        # print(view.match_selector(current_pos, "source.rainmeter"))

        # print("---", "selection_modified", view, ", view name:", view.name(), ", view id:", view.id(), ", view buffer id:", view.buffer_id(), ", view primary?:", view.is_primary())
        view.erase_regions("test")
        # print("self", self)
        # print

        # can be either decimal colors or hexadecimal colors with or without alpha channel
        # alpha channel seems be unimportant right now
        dec_color_exp = re.compile(r"(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*(,\s*\d{1,3})?")
        line = view.line(current_pos)
        content = view.substr(line)

        match = dec_color_exp.search(content)
        if match:
            logger.info("found color in '" + content + "'" + str(self))
            red_channel_dec = int(match.group(1))
            green_channel_dec = int(match.group(2))
            blue_channel_dec = int(match.group(3))
            if red_channel_dec > 255:
                logger.error("found invalid definition of red: '" + str(red_channel_dec) + "'")
            if green_channel_dec > 255:
                logger.error("found invalid definition of green: '" + str(green_channel_dec) + "'")
            if blue_channel_dec > 255:
                logger.error("found invalid definition of blue: '" + str(blue_channel_dec) + "'")

            red_channel_hex = hex(red_channel_dec)[2:]
            green_channel_hex = hex(green_channel_dec)[2:]
            blue_channel_hex = hex(blue_channel_dec)[2:]

            # use .zfill instead of '{:0>2}' or '{0:02d}' for ints in case of strings
            formatted_red_channel_hex = '{:0>2}'.format(red_channel_hex)
            formatted_green_channel_hex = '{:0>2}'.format(green_channel_hex)
            formatted_blue_channel_hex = '{:0>2}'.format(blue_channel_hex)

            rgb_hex = formatted_red_channel_hex + formatted_green_channel_hex + formatted_blue_channel_hex

            found_region = view.find(r"(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*(,\s*\d{1,3})?", line.a)

            # if user did not actually selected the colors then do not display
            # for example a user could have clicked a statement in that line
            if not found_region.contains(current_pos):
                return

            scheme_path, scheme_name = self.__get_current_color_scheme(view)
            with codecs.open(scheme_path, 'r', 'utf-8') as scheme_file:
                scheme_xml = scheme_file.read()

            # Cut out our old colors, if any.
            scheme_xml = re.sub(r'\t<!-- rainmeter -->.+<!-- /rainmeter -->\n\t', '', scheme_xml, flags=re.DOTALL)

            # Insert our updated colors.
            rm_color_def = '\t<!-- rainmeter -->{}<!-- /rainmeter -->'.format(self.__color_to_xml(rgb_hex))
            scheme_xml = re.sub('</array>', rm_color_def + '\n\t</array>', scheme_xml)

            new_scheme_path = os.path.join(sublime.packages_path(), "User", "Rainmeter", "theme", scheme_name + ".hidden-tmTheme")
            if not os.path.exists(new_scheme_path):
                codecs.open(new_scheme_path, 'x', 'utf-8')

            with codecs.open(new_scheme_path, 'w', 'utf-8') as scheme_file:
                scheme_file.write(scheme_xml)

            # print("path:", new_path)
            # with codecs.open(scheme_path, 'w', 'utf-8') as scheme_file:
            #     scheme_file.write(scheme_xml)
            # print(os.path.join("Packages", "User", "Rainmeter", "theme", scheme_name + ".hidden-tmTheme").replace("\\", "/"))

            # might need to set the current color scheme to the link of the new mirrored theme file
            prefs = sublime.load_settings('Preferences.sublime-settings')
            maybe_color_scheme = prefs.get('color_scheme', None)
            if maybe_color_scheme == "Packages/User/Rainmeter/theme/" + scheme_name + ".hidden-tmTheme":
                pass
            else:
                prefs.set('color_scheme', "Packages/User/Rainmeter/theme/" + scheme_name + ".hidden-tmTheme")

            view.add_regions("test", [found_region], scope="constant.numeric.color." + rgb_hex, flags=sublime.DRAW_NO_OUTLINE)
            # view.add_regions("test", [found_region], scope="constant.numeric.color.", flags=sublime.DRAW_NO_OUTLINE)
            # print(rgb_hex)

            # print(rgb_hex)

# add circle if only 1 color in line
# sublime.windows()[0].views()[0].add_regions("bla", [sublime.Region(0,10)], "constant.numeric.color.blue", "circle", sublime.DRAW_NO_OUTLINE)
