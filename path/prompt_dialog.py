"""This module is handling native calls to user file and folder selection."""

import os.path
import subprocess
import threading

import sublime

from .. import logger


def popen_and_call(callback, *popen_args, **popen_kwargs):
    """
    Runs a subprocess.Popen, and then calls the function onExit when the
    subprocess completes.

    Use it exactly the way you'd normally use subprocess.Popen, except include a
    callable to execute as the first argument. onExit is a callable object, and
    *popenArgs and **popenKWArgs are simply passed up to subprocess.Popen.
    """
    def run_in_thread(callback, popen_args, popen_kwargs):
        """
        This is a wrapped method call with a direct callback upon finishing the process.

        You use this because the user input will halt the processing if not started in a new thread.
        """
        proc = subprocess.Popen(*popen_args, **popen_kwargs)
        output_channel, error_channel = proc.communicate()
        message = output_channel.decode("utf-8")
        message = message.replace("\r\n", "")

        proc.wait()

        # checking for errors first
        error = error_channel.decode("utf-8", errors="replace")
        if error is not None and len(error) != 0:
            error = error.replace("\r\n", "\n")
            logger.error("Error in thread for '" + str(callback) + "':" + error)
            return

        callback(message)

        return

    thread = threading.Thread(target=run_in_thread,
                              args=(callback, popen_args, popen_kwargs))
    thread.start()

    # returns immediately after the thread starts
    return thread


def call_file_and_callback(file_basename, callback):
    """."""
    packages = sublime.packages_path()
    prompt_dir = os.path.join(packages, "User", "Rainmeter", "path")
    script_path = os.path.join(prompt_dir, file_basename)

    popen_args = [
        'powershell.exe',
        '-NoProfile',
        '-NonInteractive',
        '-NoLogo',
        '-ExecutionPolicy', 'RemoteSigned',
        '-windowstyle', 'hidden',
        '-File', script_path
    ]

    st_inf = subprocess.STARTUPINFO()
    st_inf.dwFlags = st_inf.dwFlags | subprocess.STARTF_USESHOWWINDOW

    thread = popen_and_call(
        callback,
        popen_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False,
        startupinfo=st_inf
    )

    return thread


def browse_file(callback):
    """."""
    return call_file_and_callback("open_file_dialog.ps1", callback)


def browse_folder(callback):
    """."""
    return call_file_and_callback("open_folder_dialog.ps1", callback)


def prompt_open_file_dialog():

    packages = sublime.packages_path()
    prompt_dir = os.path.join(packages, "User", "Rainmeter", "path")

    open_file_dialog_bat = os.path.join(prompt_dir, "open_file_dialog.ps1")

    st_inf = subprocess.STARTUPINFO()
    st_inf.dwFlags = st_inf.dwFlags | subprocess.STARTF_USESHOWWINDOW

    dialog = subprocess.Popen(
        [
            'powershell.exe',
            '-NoProfile',
            '-NonInteractive',
            '-NoLogo',
            '-ExecutionPolicy', 'RemoteSigned',
            '-windowstyle', 'hidden',
            '-File', open_file_dialog_bat
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False,
        startupinfo=st_inf
    )
    output_channel, error_channel = dialog.communicate()
    raw_output = output_channel.decode("utf-8")

    # need to wait on the powershell script to execute and user interaction
    dialog.wait()
    # TODO need to rework it with http://stackoverflow.com/a/5209746/2787159
    # concurrent callback when finished

    # checking for errors first
    error = error_channel.decode("utf-8")
    if error is not None and len(error) != 0:
        logger.error("Color Picker Error:\n" + error)
        return

    return raw_output
