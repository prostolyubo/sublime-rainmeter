"""This module is about reading YAML files for Rainmeter related definition files."""


import os.path
import zipfile

import sublime

from .. import logger


class YamlContentReader(object):  # pylint: disable=R0903; this is an abstract class
    """
    Use this to read the content of yamls inside of sublime text packages.

    supports multiple ways to access them:
    * .sublime-package
    * .zip
    * folder
    """

    @classmethod
    def __get_zip_content(cls, path_to_zip, resource):
        if not os.path.exists(path_to_zip):
            return None

        ret_value = None

        with zipfile.ZipFile(path_to_zip) as zip_file:
            namelist = zip_file.namelist()
            if resource in namelist:
                ret_value = zip_file.read(resource)
                return ret_value.decode("utf-8")

        logger.error("no zip content with resource '" + resource + "' found in .")

        return ret_value

    def __get_yaml_content_in_package(self, package, dir_of_yaml, yaml_file):
        # try searching in Installed Packages e.g. if packaged in .sublime-package
        packages_path = sublime.installed_packages_path()
        sublime_package = package + ".sublime-package"
        rm_package_path = os.path.join(packages_path, sublime_package)
        if os.path.exists(rm_package_path):
            logger.info("found packaged resource in '" + rm_package_path + "'")
            resource = dir_of_yaml + yaml_file

            return self.__get_zip_content(rm_package_path, resource)

        return None

    def __get_yaml_content_by_sublime_api(self, dir_of_yaml, yaml_file):
        # try over sublimes find resources first
        # should handle loose and packaged version
        for resource in sublime.find_resources(yaml_file):
            if dir_of_yaml in resource:
                logger.info(
                    "found sublime resource '" + dir_of_yaml + yaml_file + "' in '" + resource + "'"
                )
                return sublime.load_resource(resource)

    def __get_yaml_content_by_git_path(self, dir_of_yaml, yaml_file):
        # try over absolute paths determined from root e.g. by cloning with git
        rm_root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        # the dir_of_yaml comes in as foo/bar but internally python uses foo\\bar
        norm_dir_of_yaml = os.path.normpath(dir_of_yaml)
        # e.g. Rainmeter + completion/skin + metadata_section.yaml
        yaml_path = os.path.join(rm_root_path, norm_dir_of_yaml, yaml_file)

        if os.path.exists(yaml_path):
            logger.info("found absolute resource in '" + yaml_path + "'")
            with open(yaml_path, 'r') as yaml_content_stream:
                return yaml_content_stream.read()

    def __fail(self, dir_of_yaml, yaml_file):
        logger.error(
            "found not yaml neither via sublime resources, nor absolute pathing, " +
            "nor .sublime-package for '" + dir_of_yaml + yaml_file + "'."
        )
        return None

    def _get_yaml_content(self, dir_of_yaml, yaml_file):
        """
        Get yaml content of a yaml file.

        It is located either in:
        * Installed Packages/Rainmeter.sublime-package
        * Packages/Rainmeter
        Parameters
        ----------
        """
        return self.__get_yaml_content_by_sublime_api(dir_of_yaml, yaml_file) or \
            self.__get_yaml_content_by_git_path(dir_of_yaml, yaml_file) or \
            self.__get_yaml_content_in_package("Rainmeter", dir_of_yaml, yaml_file) or \
            self.__fail(dir_of_yaml, yaml_file)
