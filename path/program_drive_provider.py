"""
This module provides methods for determine the program drive.

Rainmeter has an built-in variable called #PROGRAMDRIVE#.
With this you can directly route to the drive in which Rainmeter is contained.
If by some chance people use @Include on #PROGRAMDRIVE# it is still able to resolve
the path and open the include for you.
"""

import os
from functools import lru_cache

from .. import logger
# use absolute path because of re-occuraing imports '.' could not work
from .program_path_provider import get_cached_program_path


@lru_cache(maxsize=None)
def get_cached_program_drive():
    """Get the value of the #PROGRAMDRIVE# variable."""
    rainmeterpath = get_cached_program_path()

    if not rainmeterpath:
        logger.info("Rainmeter program path not found.")
        return

    probe_drive = os.path.splitdrive(rainmeterpath)
    if not probe_drive:
        logger.info("Drive could not be extracted from '" + rainmeterpath + "'.")
        return

    # can be either a drive like C:\
    # or an UNC Mount Point like //host/computer
    return probe_drive[0]
