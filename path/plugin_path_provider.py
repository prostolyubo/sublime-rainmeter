"""
Provides a cached method to obtain the rainmeter plugin path.

This is only possible if Rainmeter is installed.
Plugins are stored in the settings path and thus only available
if settings are successfully loaded and installed.
"""

import os.path
from functools import lru_cache

from .. import logger

from .setting_path_provider import get_cached_setting_path


@lru_cache(maxsize=None)
def get_cached_plugin_path():
    """Get the value of the #PLUGINSPATH# variable."""
    settingspath = get_cached_setting_path()
    if not settingspath:
        logger.error(
            __file__,
            "get_cached_plugin_path()",
            "#SETTINGSPATH# resolution required but was not found"
        )
        return
    return os.path.join(settingspath, "Plugins") + "\\"
