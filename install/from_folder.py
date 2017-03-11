"""This module handles the business logic to install skins from a local directory."""

import os
import re
import shutil

from ..path.skin_path_provider import get_cached_skin_path


def folder_already_exists(skin_folder):
    """
    Checks if the folder already exists.

    This is to check if a skin is already installed determined by the skin folder.
    This enables us to switch in case the user does not want to overwrite the current skin.
    """
    skins_folder = get_cached_skin_path()
    inis = find_inis_in_folder(skin_folder)
    skin_name = os.path.basename(common_path(inis))
    target_skin_folder = os.path.join(skins_folder, skin_name)

    return os.path.exists(target_skin_folder)


def install_into_skins_folder(skin_folder):
    """
    Install skin folder into Rainmeter skins folder.

    Main entry point to the from_folder module.
    """
    skins_folder = get_cached_skin_path()

    inis = find_inis_in_folder(skin_folder)
    skin_name = os.path.basename(common_path(inis))
    resources_folders = find_resources_folders(skin_folder)

    paths = []
    paths.extend(inis)
    paths.extend(resources_folders)

    target_skin_folder = os.path.join(skins_folder, skin_name)

    transposed_paths = transpose_paths(paths, target_skin_folder)

    return transposed_paths


def transpose_paths(paths, target):
    """
    Transpose a subtree to a new location.

    With that we can determine a root node which acts as a source folder
    and from which we can copy everything recursively to the target folder.
    """
    commoner = common_path(paths)

    return shutil.copytree(commoner, target)


def common_path(paths):
    """
    Find skin root folder.

    The root folder is defined as the parent folder of the @Resources folder.
    Since this one is optional the next solution would be to use the least common parent from all inis
    """
    return os.path.dirname(os.path.commonprefix([p + os.path.sep for p in paths]))


def find_resources_folders(folder):
    """
    Find @Resources folders in the given folder.

    Is case insensitive.
    Will search for every @Resources folder found in the folder (e.g. in case of multi skin config).
    """
    resources = []
    for root, directories, dummy_files in os.walk(folder):
        for directory in directories:
            if directory.lower() == "@resources":
                resources.append(os.path.join(os.path.abspath(root), directory))

    return resources


def find_resources_folder_in_folder(folder):
    """
    Find a single @Resources folder in the given folder.
    """
    for root, directories, dummy_files in os.walk(folder):
        for directory in directories:
            if directory.lower() == "@resources":
                return os.path.join(os.path.abspath(root), directory)


NAME_PATTERN = re.compile(r"^\s*Name=(.+)$", re.IGNORECASE)


def find_skin_name_in_inis(inis):
    """
    Retrieve skin name in a configuration.

    A configuration can contain multiple skins.
    Each of them can contain a metadata with its real name,
    since due to the copying or zipping it could be skewed
    with informations like master or versioning.
    """
    for ini in inis:
        with open(ini, 'r') as ini_file_handler:
            for line in ini_file_handler:
                match = NAME_PATTERN.match(line)
                if match:
                    return match.group(1)


def find_inis_in_folder(folder):
    """
    Retrieve path of every file ending with .ini in folder.

    Returns the absolute path of each found file.
    """
    inis = []

    for root, dummy_dirs, files in os.walk(folder):
        for fil in files:
            if fil.endswith('.ini'):
                inis.append(os.path.join(os.path.abspath(root), fil))

    return inis
