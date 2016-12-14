"""
This module provides methods for determine the addon path.

Rainmeter has an built-in variable called #ADDONSPATH#.
With this you can directly route to the drive in which Rainmeter is contained.
If by some chance people use @Include on #ADDONSPATH# it is still able to resolve
the path and open the include for you.
"""

import os.path
from functools import lru_cache

from .. import logger

from .setting_path_provider import get_cached_setting_path


@lru_cache(maxsize=None)
def get_cached_addon_path():
    """Get the value of the #ADDONSPATH# variable."""
    settingspath = get_cached_setting_path()
    if not settingspath:
        logger.error(
            __file__,
            "get_cached_addon_path()",
            "#SETTINGSPATH# resolution required but was not found"
        )
        return
    return os.path.join(settingspath, "Addons") + "\\"
