import os
from functools import lru_cache

from Rainmeter import logger
# use absolute path because of re-occuraing imports '.' could not work
from Rainmeter.path.program_path_provider import get_cached_program_path


@lru_cache(maxsize=None)
def get_cached_setting_path():
    """Get the value of the #SETTINGSPATH# variable"""

    rainmeterpath = get_cached_program_path()

    if not rainmeterpath:
        return

    # Check if Rainmeter.ini is in Rainmeter program directory
    if os.path.exists(rainmeterpath + "Rainmeter.ini"):
        logger.info(__file__, "get_cached_settings_path", "Rainmeter.ini found in " + rainmeterpath)
        return rainmeterpath
    else:  # If not, look in %APPDATA%\Rainmeter\
        appdata = os.getenv("APPDATA")
        if os.path.exists(os.path.join(appdata, "Rainmeter\\Rainmeter.ini")):
            logger.info(__file__, "get_cached_settings_path", "Rainmeter.ini found in " +
                        os.path.join(appdata, "Rainmeter") + "\\")
            return os.path.join(appdata, "Rainmeter") + "\\"
        else:
            logger.info(__file__, "get_cached_settings_path", "Rainmeter.ini could not be located.")
            return None
