"""This module handles the business logic to install skins from zip files."""


def install_skin_zip(skin_zip):
    """
    Install a zipped skin into the Rainmeter skins folder.

    Main entry point for this module.
    Expects a valid filepath to a zip file.
    The zip file is determined by its extension.
    The skin will be extracted and handled by the from_folder module.
    """
    print(skin_zip)
