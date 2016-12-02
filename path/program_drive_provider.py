import os
from functools import lru_cache

from .. import logger
# use absolute path because of re-occuraing imports '.' could not work
from .program_path_provider import get_cached_program_path


@lru_cache(maxsize=None)
def get_cached_program_drive():
    """Get the value of the #PROGRAMDRIVE# variable"""

    rainmeterpath = get_cached_program_path()

    if not rainmeterpath:
        logger.info(__file__, "get_cached_program_drive", "Rainmeter program path not found.")
        return

    probe_drive = os.path.splitdrive(rainmeterpath)
    if not probe_drive:
        logger.info(__file__, "get_cached_program_drive", "Drive could not be extracted from '" + rainmeterpath + "'.")
        return

    # can be either a drive like C:\
    # or an UNC Mount Point like //host/computer
    return probe_drive[0]
