# def find_
import os
import re
import shutil

from ..path.skin_path_provider import get_cached_skin_path


def check_skin_folder_already_exists(skin_folder):
    skins_folder = get_cached_skin_path()
    inis = find_inis_in_folder(skin_folder)
    skin_name = os.path.basename(common_path(inis))
    target_skin_folder = os.path.join(skins_folder, skin_name)

    return os.path.exists(target_skin_folder)


def install_skin_folder_into_skins_folder(skin_folder, overwrite=False):
    skins_folder = get_cached_skin_path()

    inis = find_inis_in_folder(skin_folder)
    skin_name = os.path.basename(common_path(inis))
    resources_folders = find_resources_folders_in_folder(skin_folder)

    paths = []
    paths.extend(inis)
    paths.extend(resources_folders)

    target_skin_folder = os.path.join(skins_folder, skin_name)

    transposed_paths = transpose_paths(paths, target_skin_folder)

    return transposed_paths


# todo: problem because I mix files and folders -> easier to just transpose folders thus we need only copytree
def transpose_paths(paths, target):
    commoner = common_path(paths)

    return shutil.copytree(commoner, target)


def common_path(paths):
    """
    Find skin root folder.

    The root folder is defined as the parent folder of the @Resources folder.
    Since this one is optional the next solution would be to use the least common parent from all inis
    """
    return os.path.dirname(os.path.commonprefix([p + os.path.sep for p in paths]))


def find_resources_folders_in_folder(folder):
    resources = []
    for root, dirs, files in os.walk(folder):
        for dir in dirs:
            if dir.lower() == "@resources":
                resources.append(os.path.join(os.path.abspath(root), dir))

    return resources


def find_resources_folder_in_folder(folder):
    for root, dirs, files in os.walk(folder):
        for dir in dirs:
            if dir.lower() == "@resources":
                return os.path.join(os.path.abspath(root), dir)


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

    for root, dirs, files in os.walk(folder):
        for fil in files:
            if fil.endswith('.ini'):
                inis.append(os.path.join(os.path.abspath(root), fil))

    return inis
