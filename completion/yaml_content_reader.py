import os.path
import zipfile

import sublime

from .. import logger


class YamlContentReader:

    def __get_zip_content(self, path_to_zip, resource):
        if not os.path.exists(path_to_zip):
            return None

        ret_value = None

        with zipfile.ZipFile(path_to_zip) as zip_file:
            namelist = zip_file.namelist()
            if resource in namelist:
                ret_value = zip_file.read(resource)
                return ret_value.decode("utf-8")

        logger.error(__file__, "__get_zip_content(self, path_to_zip, resource)", "no zip content with resource '" + resource + "' found in .")
        return ret_value

    def _get_yaml_content(self, dir_of_yaml, yaml_file):
        """
        get yaml content of a yaml file located either in:
        * Installed Packages/Rainmeter.sublime-package
        * Packages/Rainmeter
        Parameters
        ----------

        """

        # try over sublimes find resources first
        # should handle loose and packaged version
        for resource in sublime.find_resources(yaml_file):
            if dir_of_yaml in resource:
                logger.info(
                    __file__,
                    "_get_yaml_content(dir_of_yaml, yaml_file)",
                    "found sublime resource '" + dir_of_yaml + yaml_file + "' in '" + resource + "'"
                )
                return sublime.load_resource(resource)

        # try over absolute paths determined from root e.g. by cloning with git
        rm_root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        # the dir_of_yaml comes in as foo/bar but internally python uses foo\\bar
        norm_dir_of_yaml = os.path.normpath(dir_of_yaml)
        # e.g. Rainmeter + completion/skin + metadata_section.yaml
        yaml_path = os.path.join(rm_root_path, norm_dir_of_yaml, yaml_file)

        if os.path.exists(yaml_path):
            logger.info(
                __file__,
                "_get_yaml_content(dir_of_yaml, yaml_file)",
                "found absolute resource in '" + yaml_path + "'"
            )
            with open(yaml_path, 'r') as yaml_content_stream:
                return yaml_content_stream.read()

        # try searching in Installed Packages e.g. if packaged in .sublime-package
        packages_path = sublime.installed_packages_path()
        sublime_package = "Rainmeter.sublime-package"
        rm_package_path = os.path.join(packages_path, sublime_package)
        if os.path.exists(rm_package_path):
            logger.info(
                __file__,
                "_get_yaml_content(dir_of_yaml, yaml_file)",
                "found packaged resource in '" + rm_package_path + "'"
            )
            resource = dir_of_yaml + yaml_file

            return self.__get_zip_content(rm_package_path, resource)

        logger.error(
            __file__,
            "_get_yaml_content(dir_of_yaml, yaml_file)",
            "found not yaml neither via sublime resources, nor absolute pathing, nor .sublime-package for '" + dir_of_yaml + yaml_file + "'."
        )
        return None
