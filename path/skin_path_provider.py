"""This module is about path resolving for the skin path.

This is particular useful if you for example try create new skins
or open an existing one.
"""

import getpass
import io
import os
import platform
import re
import winreg
from functools import lru_cache

import sublime

from .. import logger

from .program_path_provider import get_cached_program_path
from .setting_path_provider import get_cached_setting_path


@lru_cache(maxsize=None)
def get_cached_skin_path():
    """Get the value of the #SKINSPATH# variable."""
    # First try to load the value from the "rainmeter_skins_path" setting
    loaded_settings = sublime.load_settings("Rainmeter.sublime-settings")
    skinspath = loaded_settings.get("rainmeter_skins_path", None)

    # if it's found, return it
    # We trust the user to enter something meaningful here
    # and don't check anything.
    if skinspath:
        logger.info(
            __file__,
            "get_skins_path",
            "Skins path '" + skinspath + "' found in sublime-settings file."
        )
        return os.path.normpath(skinspath) + "\\"

    # If it's not set, try to detect it automagically
    rainmeterpath = get_cached_program_path()
    settingspath = get_cached_setting_path()
    if not rainmeterpath or not settingspath:
        return

    # First, try to read the SkinPath setting from Rainmeter.ini
    fhnd = io.open(os.path.join(settingspath, "Rainmeter.ini"))
    lines = fhnd.read()
    fhnd.close()

    # Find the skinspath setting in the file
    match = re.search(r"""(?imsx)

                     # Find the first [Rainmeter] section
                     (^\s*\[\s*Rainmeter\s*\]\s*$)
                     (.*?

                         # Find the "SkinPath" and "="
                         (^\s*SkinPath\s*=\s*

                             # Read until the next line ending and store
                             # in named group
                             (?P<skinpath>[^$]+?)\s*?$
                         )
                     ).*?

                     # All of this needs to happen before the next section
                     (?:^\s*\[\s*[^\[\]\s]+\s*\]\s*$)
                     """, lines)

    # if skinspath setting was found, return it
    if match:
        logger.info(__file__, "get_skins_path", "Skins path found in Rainmeter.ini.")
        return match.group("skinpath").strip().replace("/", "\\")

    # if it's not found in the settings file, try to guess it

    # If program path and setting path are equal, we have a portable
    # installation. In this case, the Skins folder is inside the rainmeter
    # path
    if os.path.samefile(rainmeterpath, settingspath):
        logger.info(__file__, "get_skins_path", "Skin path found in #PROGRAMPATH#" +
                    " because portable installation")
        return os.path.join(rainmeterpath, "Skins") + "\\"

    # If it's not a portable installation, we try looking into the "My
    # Documents" folder Since it could be relocated by the user, we have to
    # query its value from the registry
    try:
        regkey = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Software\Microsoft\Windows" +
                                r"\CurrentVersion\Explorer" +
                                r"\User Shell Folders")
        keyval = winreg.QueryValueEx(regkey, "Personal")

        pathrep = keyval[0]

        # The path could (and most likely, will) contain environment
        # variables that have to be expanded first
        pathrep = os.path.expandvars(pathrep)

        logger.info(__file__, "get_skins_path", "Guessed Skin path from My Documents" +
                    " location in registry")
        return os.path.join(pathrep, "Rainmeter\\Skins") + "\\"

    except OSError:
        pass

    # If the value could not be retrieved from the registry,
    # we try some educated guesses about default locations
    try:
        username = getpass.getuser()
    except Exception:
        logger.info(__file__, "get_skins_path", "Skins path could not be located." +
                    " Please set the \"skins_path\" setting in your Rainmeter" +
                    " settings file.")
        return
    else:
        # check if windows version is XP
        winversion = platform.version()
        if int(winversion[0]) < 6:
            mydocuments = os.path.join("C:\\Documents and Settings",
                                       username,
                                       "My Documents") + "\\"

            logger.info(__file__, "get_skins_path", "Found Windows XP or lower." +
                        " Skins path assumed to be " + mydocuments +
                        "Rainmeter\\Skins\\")
        else:
            mydocuments = os.path.join("C:\\Users",
                                       username,
                                       "Documents") + "\\"

            logger.info(__file__, "get_skins_path", "Found Windows Vista or higher." +
                        " Skins path assumed to be " + mydocuments +
                        "Rainmeter\\Skins\\")

        logger.info(__file__, "get_skins_path", "Skin path guessed from user name" +
                    " and Windows version")
        return os.path.join(mydocuments, "Rainmeter\\Skins") + "\\"
