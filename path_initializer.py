"""This module is to initialize common paths required for other plugins to work."""

import os.path

import sublime

# own dependencies
from . import logger

from .path.program_path_provider import get_cached_program_path
from .path.setting_path_provider import get_cached_setting_path
from .path.program_drive_provider import get_cached_program_drive
from .path.plugin_path_provider import get_cached_plugin_path
from .path.addon_path_provider import get_cached_addon_path
from .path.skin_path_provider import get_cached_skin_path
from .path.prompt_dialog import browse_file, browse_folder


def __require_path(path):
    if not os.path.exists(path):
        os.makedirs(path)


def __copy_on_absence_or_newer(user_path, binary_path):
    """
    .

    user_path: path of the file in the user directory
    binary_path: Packages/Rainmeter/xxx path inside the package
    """
    # could be already copied on a previous run
    need_update = not os.path.exists(user_path)
    binary = sublime.load_binary_resource(binary_path)

    # could be a newer version there
    # only check if no newer is required since expensive
    # generally happens in consecutive calls without updates
    if not need_update:
        need_update = os.path.getsize(user_path) != len(binary)
    if need_update:
        logger.info("Newer version of color picker found. Copying data over to '" + user_path + "'")
        with open(user_path, "wb") as file_handler:
            file_handler.write(binary)
    else:
        logger.info("You are using the most current version of '" + binary_path + "'. Continue loading...")


def __handle_program_path_init():
    program_path = get_cached_program_path()
    if not program_path:
        # Open dialog and set program path.
        # Due to cache this might be annoying
        # since I cant call cached stuff
        # before I can assure that the path is correct
        # or just reset the cache.

        def on_rainmeter_exe_browsed(message):
            """
            If file is browsed we need to verify that this is the Rainmeter.exe.
            If it is we need to reset the cache via.
            """
            if os.path.exists(message):
                # If file is browsed
                # - verify Rainmeter.exe.
                # - reset cache
                # - save new path in settings

                logger.info("Verified existence of Rainmeter.exe in '" + message + "'.")
                settings = sublime.load_settings("Rainmeter.sublime-settings")
                rm_dir = os.path.dirname(message)
                normed_rm_dir = os.path.normpath(rm_dir)

                settings.set("rainmeter_path", normed_rm_dir)
                sublime.save_settings("Rainmeter.sublime-settings")
                logger.info("Rewrote settings to include rainmeter path.")
                sublime.message_dialog("Successfully set the Rainmeter application path to '" + normed_rm_dir + "'.")

                # we have to reset every cache because all are dependent on the program path
                # at least transitively
                get_cached_program_path.cache_clear()
                get_cached_program_drive.cache_clear()
                get_cached_setting_path.cache_clear()
                get_cached_skin_path.cache_clear()
                get_cached_addon_path.cache_clear()
                get_cached_plugin_path.cache_clear()
                logger.info("Cleared cache.")

            elif message == "-1":
                logger.info("User canceled Rainmeter.exe input.")

            else:
                # retry by recalling it again.
                logger.info("No valid Rainmeter.exe found. Retrying again.")
                browse_file(on_rainmeter_exe_browsed)

        browse_file(on_rainmeter_exe_browsed)


def __handle_skin_path_init():
    skin_path = get_cached_skin_path()
    if not skin_path:
        # Open folder dialog and set skin path.

        def on_skins_folder_browsed(skin_dir):
            """."""
            logger.info("skin_dir: " + skin_dir)
            if os.path.exists(skin_dir):
                # If folder is browsed:
                # - verify skin folder
                # - reset cache
                # - save new path in settings

                logger.info("Verified existence of Rainmeter Skin folder in '" + skin_dir + "'.")
                settings = sublime.load_settings("Rainmeter.sublime-settings")
                normed_skin_dir = os.path.normpath(skin_dir)

                settings.set("rainmeter_skins_path", normed_skin_dir)
                sublime.save_settings("Rainmeter.sublime-settings")
                logger.info("Rewrote settings to include skin path.")
                sublime.message_dialog("Successfully set the Rainmeter Skins path to '" + skin_dir + "'.")

                # we have to reset every cache because all are dependent on the program path
                # at least transitively
                get_cached_skin_path.cache_clear()
                logger.info("Cleared cache.")

            elif skin_dir == "-1":
                logger.info("User canceled Rainmeter Skin folder input.")

            else:
                # retry by recalling it again.
                logger.info("No valid Rainmeter Skin folder found. Retrying again.")
                browse_folder(on_skins_folder_browsed)

        browse_folder(on_skins_folder_browsed)


def plugin_loaded():
    """
    Called automatically from ST3 if plugin is loaded.

    Is required now due to async call and ignoring sublime.* from main routine
    """

    packages = sublime.packages_path()
    prompt_dir = os.path.join(packages, "User", "Rainmeter", "path")

    __require_path(prompt_dir)

    open_file_dialog_bat = os.path.join(prompt_dir, "open_file_dialog.ps1")
    open_folder_dialog_bat = os.path.join(prompt_dir, "open_folder_dialog.ps1")

    __copy_on_absence_or_newer(open_file_dialog_bat, "Packages/Rainmeter/path/open_file_dialog.ps1")
    __copy_on_absence_or_newer(open_folder_dialog_bat, "Packages/Rainmeter/path/open_folder_dialog.ps1")

    __handle_program_path_init()
    __handle_skin_path_init()

    padding = 16
    logger.info("#PROGRAMPATH#:".ljust(padding) + get_cached_program_path())  # Rainmeter.exe
    logger.info("#PROGRAMDRIVE#:".ljust(padding) + get_cached_program_drive())
    logger.info("#SETTINGSPATH#:".ljust(padding) + get_cached_setting_path())  # Rainmeter.ini
    logger.info("#SKINSPATH#:".ljust(padding) + get_cached_skin_path())  # Rainmeter/Skins path
    logger.info("#PLUGINSPATH#:".ljust(padding) + get_cached_plugin_path())
    logger.info("#ADDONSPATH#:".ljust(padding) + get_cached_addon_path())
