import os
import winreg

from functools import lru_cache

import sublime

from .. import logger


@lru_cache(maxsize=None)
def get_cached_program_path():
    # Load setting
    settings = sublime.load_settings("Rainmeter.sublime-settings")
    rainmeterpath = settings.get("rainmeter_path", None)

    # If setting is not set, try default location
    if not rainmeterpath:
        logger.info(__file__, "get_cached_program_path()",
                    "rainmeter_path not found in settings. Trying default location.")
        # Default: "C:\Program Files\Rainmeter"
        programfiles = os.getenv("PROGRAMFILES")
        rainmeterpath = os.path.join(programfiles, "Rainmeter") + "\\"

        # if it is not even specified by default, try using the registry to retrieve the installation path
        if not os.path.isdir(rainmeterpath):
            regkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Rainmeter")
            keyval = winreg.QueryValueEx(regkey, "Personal")

            for i in range(1024):
                try:
                    asubkey_name = winreg.EnumKey(keyval, i)
                    asubkey = winreg.OpenKey(keyval, asubkey_name)
                    val = winreg.QueryValueEx(asubkey, "DisplayName")
                    logger.info(__file__, "get_cached_program_path()", "found rainmeter path through registry: " + val)
                except EnvironmentError:
                    break

    # normalize path
    rainmeterpath = os.path.normpath(rainmeterpath) + "\\"

    # Check if path exists and contains Rainmeter.exe
    if not os.path.exists(rainmeterpath + "Rainmeter.exe"):
        message = "Path to Rainmeter.exe could neither be found in the standard directory nor via registry. Check your \"rainmeter_path\" setting."
        logger.info(__file__, "get_cached_program_path()", message)
        sublime.error_message(message)
        return

    logger.info(__file__, "get_cached_program_path()", "Rainmeter found in " + rainmeterpath)
    return rainmeterpath
