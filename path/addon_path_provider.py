import os.path
from functools import lru_cache

from .. import logger

from .setting_path_provider import get_cached_setting_path


@lru_cache(maxsize=None)
def get_cached_addon_path():
    """
    Get the value of the #ADDONSPATH# variable
    """

    settingspath = get_cached_setting_path()
    if not settingspath:
        logger.error(
            __file__,
            "get_cached_addon_path()",
            "#SETTINGSPATH# resolution required but was not found"
        )
        return
    return os.path.join(settingspath, "Addons") + "\\"
