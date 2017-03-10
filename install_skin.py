import os.path
# import shutil
# import tempfile
# import zipfile

import sublime
import sublime_plugin

# from .logger import info, error

from .http.online_checker import is_gh_online
# from .http.content_downloader import download_from_to
from .install import from_folder
from .install import from_zip
# from .path.skin_path_provider import get_cached_skin_path


GITHUB_ACCESS_TOKEN = "3e2e92777aab20a3352c058f9a8eb10e5ff5fd61"


# def install_zip_into_skins_folder(zip_file):
#     with zipfile.ZipFile(zip_file) as zipped_skin:
#         skins_path = get_cached_skin_path()
#         info("Found skins path in '" + skins_path + "'.")

#         zip_name = zip_file.rsplit('/', 1)[-1]

#         folder_name, dummy_ext = os.path.splitext(zip_name)
#         info("Skin folder name will be '" + folder_name + "'.")

#         skin_path = os.path.join(skins_path, folder_name)
#         skin_path = minify_folder(skin_path)
#         info("Extracting zip from '" + zip_file + "' to '" + skin_path + "'.")

#         zipped_skin.extractall(skin_path)

#         sublime.message_dialog("Successfully installed skin into '" + skin_path + "'!")

#         return True


# def minify_folder(folder_path):
#     """
#     Reduce unnecessary depth of folder structures for skins.

#     If you install a skin via a ZIP if could be that in the zip
#     an additional folder is already wrapped around like via Github
#     and thus we can remove that layer to reduce the depth to the real skin files.
#     """
#     content_names = os.listdir(folder_path)
#     while len(content_names) == 1:
#         content_path = os.path.join(folder_path, content_names[0])

#         if os.path.isdir(content_path):
#             content_paths = [os.path.join(content_path, file_name) for file_name in os.listdir(content_path)]

#             for f in content_paths:
#                 shutil.move(f, folder_path)

#             os.rmdir(content_path)

#         # reset for while recursion
#         content_names = os.listdir(folder_path)

#     return folder_path


# def count_folders_in_folder(folder_path):
#     """Non-recursive version of os.walk for directories."""
#     return sum(os.path.isdir(os.path.join(folder_path, f)) for f in os.listdir(folder_path))


# def count_files_in_folder(folder_path):
#     """Non-recursive version of os.walk for files."""
#     return sum(os.path.isfile(os.path.join(folder_path, f)) for f in os.listdir(folder_path))


# class InstallSkinCommand(sublime_plugin.ApplicationCommand):

#     def run(self):
#         """
#         Could install from direct repo URL, zip file or github release or even branch."""
#         pass


# class RainmeterInstallSkinFromZipCommand(sublime_plugin.ApplicationCommand):

#     def on_zipped_skin_url_entered(self, url):
#         info("Found url '" + url + "' of zip.")
#         sublime.set_timeout_async(lambda: self.on_zipped_skin_url_entered_async(url), 0)

#     def on_zipped_skin_url_entered_async(self, url):
#         with tempfile.TemporaryDirectory() as temp_path:
#             info("Downloading zip to temp folder '" + temp_path + "'.")
#             zip_name = url.rsplit('/', 1)[-1]

#             temp_file = os.path.join(temp_path, zip_name)
#             download_from_to(url, temp_file)
#             info("Downloaded zip to temp file '" + temp_file + "'.")

#             if not zipfile.is_zipfile(temp_file):
#                 message = "The file from '" + url + "' is not a valid ZIP file. Invalid files can not be extracted. Aborting Operation."

#                 error(message)
#                 sublime.error_message(message)

#                 return False

#             return install_zip_into_skins_folder(temp_file)

#     def run(self):
#         maybe_clipboard = sublime.get_clipboard()
#         default_url = maybe_clipboard if maybe_clipboard else "https://skin.zip"

#         sublime.active_window().show_input_panel(
#             "Enter URL to zipped Skin:",
#             default_url,
#             self.on_zipped_skin_url_entered, None, None
#         )


# class InstallSkinFromGithubCommand(sublime_plugin.ApplicationCommand):

#     def on_github_skin_url_entered(self, url):
#         # skin_path = get_cached_skin_path()

#         with tempfile.TemporaryDirectory() as temp_path:
#             zip_name = url.rsplit('/', 1)[-1]

#             temp_file = os.path.join(temp_path, zip_name)
#             download_from_to(url, temp_file)
#             print(temp_file)

#         print(url)

#     def run(self):
#         if not is_gh_online():
#             message = "Could not access github.com. Please check your connection and try again or look if github.com is down."

#             error(message)
#             sublime.error_message(message)

#         sublime.active_window().show_input_panel(
#             "Enter Github Project URL to Rainmeter Skin:",
#             "https://github.com/<user>/<project>",
#             self.on_github_skin_url_entered, None, None
#         )


class RainmeterInstallSkinFromFolderCommand(sublime_plugin.ApplicationCommand):

    def run(self):
        # check cache first to determine the default path shown to the user
        install_cache_path = os.path.join(sublime.cache_path(), "Rainmeter", "install", "last_entered_folder.cache")
        if os.path.exists(install_cache_path) and os.path.isfile(install_cache_path):
            with open(install_cache_path, 'r') as cache_handler:
                cache_content = cache_handler.read()
                default_path = cache_content

        else:
            user = os.path.expanduser("~")
            downloads = os.path.join(user, "Downloads")

            if os.path.exists(downloads) and os.path.isdir(downloads):
                default_path = downloads
            else:
                default_path = None

        sublime.active_window().show_input_panel(
            "Enter skin folder location:",
            default_path,
            self.on_folder_path_entered, None, None
        )

    def on_folder_path_entered(self, path):
        if not os.path.exists(path):
            sublime.error_message("The entered path '" + path + "' is not valid. Please check your input.")
            return

        if not os.path.isdir(path):
            sublime.error_message("The entered path '" + path + "' is not a directory. Please check your input.")
            return

        if not from_folder.find_inis_in_folder(path):
            sublime.error_message("The entered path '" + path + "' is not a valid Rainmeter skin. Please check your input.")
            return

        # we expect the user to enter a new path which we need to persist
        install_cache_path = os.path.join(sublime.cache_path(), "Rainmeter", "install", "last_entered_folder.cache")
        if os.path.exists(install_cache_path):
            write_mode = 'w'
        else:
            write_mode = 'x'
            os.makedirs(os.path.dirname(install_cache_path))

        with open(install_cache_path, write_mode) as cache_handler:
            cache_handler.write(path)

        dest_folder = from_folder.install_skin_folder_into_skins_folder(path)
        sublime.message_dialog("Skin was successfully installed into \n\n" + dest_folder)


class RainmeterInstallSkinFromZipCommand(sublime_plugin.ApplicationCommand):

    def run(self):
        # check cache first to determine the default path shown to the user
        install_cache_path = os.path.join(sublime.cache_path(), "Rainmeter", "install", "last_entered_zip.cache")
        if os.path.exists(install_cache_path) and os.path.isfile(install_cache_path):
            with open(install_cache_path, 'r') as cache_handler:
                cache_content = cache_handler.read()
                default_path = cache_content

        else:
            # show some default location from which the user can search from
            user = os.path.expanduser("~")
            downloads = os.path.join(user, "Downloads")

            if os.path.exists(downloads) and os.path.isdir(downloads):
                default_path = downloads
            else:
                default_path = None

        sublime.active_window().show_input_panel(
            "Enter skin zip location:",
            default_path,
            self.on_zip_path_entered, None, None
        )

    def on_zip_path_entered(self, path):
        if not os.path.exists(path):
            sublime.error_message("The entered path '" + path + "' is not valid. Please check your input.")
            return

        if not os.path.isfile(path):
            sublime.error_message("The entered path '" + path + "' is not a file. Please check your input.")
            return

        if not path.endswith(".zip"):
            sublime.error_message("The entered path '" + path + "' is not a zip file. Please check your input.")
            return

        # we expect the user to enter a new path which we need to persist
        install_cache_path = os.path.join(sublime.cache_path(), "Rainmeter", "install", "last_entered_zip.cache")
        if os.path.exists(install_cache_path):
            write_mode = 'w'
        else:
            write_mode = 'x'
            os.makedirs(os.path.dirname(install_cache_path))

        with open(install_cache_path, write_mode) as cache_handler:
            cache_handler.write(path)

        from_zip.install_skin_zip_into_skins_folder(path)
        sublime.status_message("Skin was successfully installed!")


class RainmeterInstallSkinFromGitCommand(sublime_plugin.ApplicationCommand):

    def run(self):
        pass

    def on_git_path_entered(self, path):
        pass


class RainmeterInstallSkinFromGithubCommand(sublime_plugin.ApplicationCommand):

    def run(self):
        default_path = "https://github.com/<user>/<repository>"
        sublime.active_window().show_input_panel(
            "Enter skin zip location:",
            default_path,
            self.on_github_path_entered, None, None
        )

    def on_github_path_entered(self, path):
        if is_gh_online():
            print("Github is online")
