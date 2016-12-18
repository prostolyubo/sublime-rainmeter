"""
This module is about path resolving for the program path.

This is required to execute Rainmeter.exe for example to refresh the current skin.
"""

import os
from functools import lru_cache
import winreg

import sublime

from .. import logger


def get_rm_path_from_default_path():
    r"""
    Default location is "C:\Program Files\Rainmeter" in windows.

    We can get "C:\Program Files" through the environmental variables
    %PROGRAMFILES%
    """
    programfiles = os.getenv("PROGRAMFILES")
    rainmeterpath = os.path.join(programfiles, "Rainmeter")

    return rainmeterpath


def _get_rainmeter_registry_key():
    r"""
    Throw FileNotFoundException if Software\WOW6432Node\Rainmeter does not exist.

    not much we can do to handle that
    """
    return winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\WOW6432Node\\Rainmeter")


def get_rm_path_from_registry():
    """Registry."""
    rainmeter_key = _get_rainmeter_registry_key()
    rainmeter_path = winreg.QueryValue(rainmeter_key, None)

    return rainmeter_path


def __executable_exists(rm_path):
    """Check if Rainmeter executable exists."""
    # normalize path
    rainmeter_exe = os.path.join(rm_path, "Rainmeter.exe")
    if not os.path.exists(rainmeter_exe):
        message = """Rainmeter path was found, but no Rainmeter.exe found.
                     Check if you have installed Rainmeter correctly."""
        logger.error(__file__, "get_cached_program_path()", message)
        sublime.error_message(message)
        return False

    return True

@lru_cache(maxsize=None)
def get_cached_program_path():
    """Try to retrieve the program path of RM through magic.

    Possible options are:

    * It is given through settings
    * It is in the default installation path
    * It is registered in the registry
    * Ask the user for the path
    """
    # Load setting
    settings = sublime.load_settings("Rainmeter.sublime-settings")
    rm_path = settings.get("rainmeter_path", None)

    # If setting is not set, try default location
    if not rm_path:
        logger.info(
            __file__,
            "get_cached_program_path()",
            "rainmeter_path not found in settings. Trying default location."
        )
        rm_path = get_rm_path_from_default_path()

    # if it is not even specified by default,
    # try using the registry to retrieve the installation path
    if not os.path.isdir(rm_path):
        rm_path = get_rm_path_from_registry()

    # Check if path exists and contains Rainmeter.exe
    if not os.path.isdir(rm_path):
        message = """Path to Rainmeter.exe could neither be found:
                     
                     * in the settings,
                     * in the standard directory,
                     * nor via registry.

                     Check your \"rainmeter_path\" setting."""
        logger.info(__file__, "get_cached_program_path()", message)
        sublime.error_message(message)
        return

    if not __executable_exists(rm_path):
        return

    logger.info(__file__, "get_cached_program_path()", "Rainmeter found in " + rm_path)
    return rm_path + "\\"
