import os
import winreg

from functools import lru_cache

import sublime

from .. import logger


def _get_rainmeter_path_from_default_path():
    """
    Default location is "C:\Program Files\Rainmeter" in windows
    we can get "C:\Program Files" through the environmental variables
    %PROGRAMFILES%
    """
    programfiles = os.getenv("PROGRAMFILES")
    rainmeterpath = os.path.join(programfiles, "Rainmeter")

    return rainmeterpath


def _get_rainmeter_registry_key():
    try:
        return winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\WOW6432Node\\Rainmeter")
    except FileNotFoundError:
        import sys

        is_64bits = sys.maxsize > 2**32
        if is_64bits:
            other_view_flag = winreg.KEY_WOW64_32KEY
        else:
            other_view_flag = winreg.KEY_WOW64_64KEY

        try:
            return winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\WOW6432Node\\Rainmeter", access=winreg.KEY_READ | other_view_flag)
        except FileNotFoundError:
            """
            We really could not find the key in both views.
            """
            return None


def _get_rainmeter_path_from_registry():
    """
    Registry
    """
    rainmeter_key = _get_rainmeter_registry_key()
    if rainmeter_key:
        rainmeter_path = winreg.QueryValue(rainmeter_key, None)

        return rainmeter_path

        # sub_key_size and last_modified not required
        # _, value_size, _ = winreg.QueryInfoKey(regkey)
        # print("---", value_size)
        # print("---", winreg.EnumKey(regkey, 0))
        # for entry_index in range(0, entry_size):
        #     key_name = winreg.EnumKey(regkey, entry_index)
        #     key = winreg.OpenKey(regkey, key_name)
        #     try:
        #         print(winreg.QueryValueEx(key, 'DisplayName')[0])
        #     except OSError as e:
        #         print(e)
        #         pass
        #     finally:
        #         key.close()

        # keyval = winreg.QueryValueEx(regkey, "Personal")

        # for i in range(1024):
        #     try:
        #         asubkey_name = winreg.EnumKey(keyval, i)
        #         asubkey = winreg.OpenKey(keyval, asubkey_name)
        #         rainmeterpath = winreg.QueryValueEx(asubkey, "DisplayName")
        #         logger.info(__file__, "get_cached_program_path()", "found rainmeter path through registry: " + rainmeterpath)
        #         if rainmeterpath:
        #             return rainmeterpath
        #     except EnvironmentError:
        #         break

    return None


@lru_cache(maxsize=None)
def get_cached_program_path():
    # Load setting
    settings = sublime.load_settings("Rainmeter.sublime-settings")
    rainmeterpath = settings.get("rainmeter_path", None)

    # If setting is not set, try default location
    if not rainmeterpath:
        logger.info(
            __file__,
            "get_cached_program_path()",
            "rainmeter_path not found in settings. Trying default location."
        )
        rainmeterpath = _get_rainmeter_path_from_default_path()

    # if it is not even specified by default, try using the registry to retrieve the installation path
    if not os.path.isdir(rainmeterpath):
        rainmeterpath = _get_rainmeter_path_from_registry()

    # Check if path exists and contains Rainmeter.exe
    if not os.path.isdir(rainmeterpath):
        message = "Path to Rainmeter.exe could neither be found in the standard directory nor via registry. Check your \"rainmeter_path\" setting."
        logger.info(__file__, "get_cached_program_path()", message)
        sublime.error_message(message)
        return

    # normalize path
    rainmeter_exe = os.path.join(rainmeterpath, "Rainmeter.exe")
    if not os.path.exists(rainmeter_exe):
        message = "Rainmeter path was found, but no Rainmeter.exe found. Check if you have correctly installed Rainmeter."
        logger.error(__file__, "get_cached_program_path()", message)
        sublime.error_message(message)
        return

    logger.info(__file__, "get_cached_program_path()", "Rainmeter found in " + rainmeterpath)
    return rainmeterpath + "\\"
