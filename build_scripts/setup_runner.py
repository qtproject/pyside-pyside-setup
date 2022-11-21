# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import os
import sys
import tempfile
import textwrap
import logging

from pathlib import Path
from setuptools import setup

from build_scripts.config import config
from build_scripts.main import (cmd_class_dict, get_package_version,
                                get_setuptools_extension_modules)
from build_scripts.options import ADDITIONAL_OPTIONS, OPTION
from build_scripts.utils import run_process
from build_scripts.log import log, LogLevel


class SetupRunner(object):
    def __init__(self, orig_argv):
        self.invocations_list = []

        # Keep the original args around in case we ever need to pass
        # modified arguments to the sub invocations.
        self.orig_argv = orig_argv
        self.sub_argv = list(orig_argv)

        self.setup_script_dir = Path.cwd()

    @staticmethod
    def cmd_line_argument_is_in_args(argument, args):
        """ Check if command line argument was passed in args. """
        return any(arg for arg in list(args) if f"--{argument}" in arg)

    @staticmethod
    def get_cmd_line_argument_in_args(argument, args):
        """ Gets the value of a cmd line argument passed in args. """
        for arg in list(args):
            if f"--{argument}" in arg:
                prefix = f"--{argument}"
                prefix_len = len(prefix) + 1
                return arg[prefix_len:]
        return None

    @staticmethod
    def remove_cmd_line_argument_in_args(argument, args):
        """ Remove command line argument from args. """
        return [arg for arg in list(args) if f"--{argument}" not in arg]

    @staticmethod
    def construct_cmd_line_argument(name, value=None):
        """ Constructs a command line argument given name and value. """
        if not value:
            return f"--{name}"
        return f"--{name}={value}"

    @staticmethod
    def construct_internal_build_type_cmd_line_argument(internal_build_type):
        return SetupRunner.construct_cmd_line_argument("internal-build-type", internal_build_type)

    def enqueue_setup_internal_invocation(self, setup_cmd):
        self.invocations_list.append(setup_cmd)

    def add_setup_internal_invocation(self, build_type, reuse_build=False, extra_args=None):
        setup_cmd = self.new_setup_internal_invocation(build_type, reuse_build, extra_args)
        self.enqueue_setup_internal_invocation(setup_cmd)

    def new_setup_internal_invocation(self, build_type,
                                      reuse_build=False,
                                      extra_args=None,
                                      replace_command_with=None):
        """ Creates a script sub-invocation to be executed later. """
        internal_build_type_arg = self.construct_internal_build_type_cmd_line_argument(build_type)

        command_index = 0
        command = self.sub_argv[command_index]
        if command == 'setup.py' and len(self.sub_argv) > 1:
            command_index = 1
            command = self.sub_argv[command_index]

        # Make a copy
        modified_argv = list(self.sub_argv)

        if replace_command_with:
            modified_argv[command_index] = replace_command_with

        setup_cmd = [sys.executable] + modified_argv + [internal_build_type_arg]

        if extra_args:
            for (name, value) in extra_args:
                setup_cmd.append(self.construct_cmd_line_argument(name, value))

        # Add --reuse-build option if requested and not already present.
        if (reuse_build and command in ('bdist_wheel', 'build', 'build_rst_docs', 'install')
                and not self.cmd_line_argument_is_in_args("reuse-build", modified_argv)):
            setup_cmd.append(self.construct_cmd_line_argument("reuse-build"))
        return setup_cmd

    def add_host_tools_setup_internal_invocation(self, initialized_config):
        extra_args = []
        extra_host_args = []

        # When cross-compiling, build the host shiboken generator tool
        # only if a path to an existing one was not provided.
        if not self.cmd_line_argument_is_in_args("shiboken-host-path", self.sub_argv):
            handle, initialized_config.shiboken_host_query_path = tempfile.mkstemp()
            os.close(handle)

            # Tell the setup process to create a file with the location
            # of the installed host shiboken as its contents.
            extra_host_args.append(
                ("internal-cmake-install-dir-query-file-path",
                 initialized_config.shiboken_host_query_path))

            # Tell the other setup invocations to read that file and use
            # the read path as the location of the host shiboken.
            extra_args.append(
                ("internal-shiboken-host-path-query-file",
                 initialized_config.shiboken_host_query_path)
            )

            # This is specifying shiboken_module_option_name
            # instead of shiboken_generator_option_name, but it will
            # actually build the generator.
            host_cmd = self.new_setup_internal_invocation(
                initialized_config.shiboken_module_option_name,
                extra_args=extra_host_args,
                replace_command_with="build")

            # To build the host tools, we reuse the initial target
            # command line arguments, but we remove some options that
            # don't make sense for the host build.

            # Drop the toolchain arg.
            host_cmd = self.remove_cmd_line_argument_in_args("cmake-toolchain-file",
                                                             host_cmd)

            # Drop the target plat-name arg if there is one.
            if self.cmd_line_argument_is_in_args("plat-name", host_cmd):
                host_cmd = self.remove_cmd_line_argument_in_args("plat-name", host_cmd)

            # Drop the python-target-path arg if there is one.
            if self.cmd_line_argument_is_in_args("python-target-path", host_cmd):
                host_cmd = self.remove_cmd_line_argument_in_args("python-target-path", host_cmd)

            # Drop the target build-tests arg if there is one.
            if self.cmd_line_argument_is_in_args("build-tests", host_cmd):
                host_cmd = self.remove_cmd_line_argument_in_args("build-tests", host_cmd)

            # Make sure to pass the qt host path as the target path
            # when doing the host build. And make sure to remove any
            # existing qt target path.
            if self.cmd_line_argument_is_in_args("qt-host-path", host_cmd):
                qt_host_path = self.get_cmd_line_argument_in_args("qt-host-path", host_cmd)
                host_cmd = self.remove_cmd_line_argument_in_args("qt-host-path", host_cmd)
                host_cmd = self.remove_cmd_line_argument_in_args("qt-target-path", host_cmd)
                host_cmd.append(self.construct_cmd_line_argument("qt-target-path",
                                                                 qt_host_path))

            self.enqueue_setup_internal_invocation(host_cmd)
        return extra_args

    def run_setup(self):
        """
        Decide what kind of build is requested and then execute it.
        In the top-level invocation case, the script
            will spawn setup.py again (possibly multiple times).
        In the internal invocation case, the script
            will run setuptools.setup().
        """

        # PYSIDE-1746: We prevent the generation of .pyc/.pyo files during installation.
        #              These files are generated anyway on their import.
        sys.dont_write_bytecode = True
        qt_install_path = OPTION["QTPATHS"]
        if qt_install_path:
            qt_install_path = Path(qt_install_path).parents[1]

        # Prepare initial config.
        config.init_config(build_type=OPTION["BUILD_TYPE"],
                           internal_build_type=OPTION["INTERNAL_BUILD_TYPE"],
                           cmd_class_dict=cmd_class_dict,
                           package_version=get_package_version(),
                           ext_modules=get_setuptools_extension_modules(),
                           setup_script_dir=self.setup_script_dir,
                           cmake_toolchain_file=OPTION["CMAKE_TOOLCHAIN_FILE"],
                           log_level=OPTION["LOG_LEVEL"],
                           qt_install_path=qt_install_path)

        # Enable logging for both the top-level invocation of setup.py
        # as well as for child invocations. We we now use
        if OPTION["LOG_LEVEL"] == LogLevel.VERBOSE:
            log.setLevel(logging.DEBUG)
        elif OPTION["LOG_LEVEL"] == LogLevel.QUIET:
            log.setLevel(logging.ERROR)
        elif OPTION["LOG_LEVEL"] == LogLevel.INFO:
            log.setLevel(logging.INFO)

        # This is an internal invocation of setup.py, so start actual
        # build.
        if config.is_internal_invocation():
            if config.internal_build_type not in config.get_allowed_internal_build_values():
                raise RuntimeError(f"Invalid '{config.internal_build_type}' option given to "
                                   "--internal-build-type. ")
            self.run_setuptools_setup()
            return

        # This is a top-level invocation of setup.py, so figure out what
        # modules we will build and depending on that, call setup.py
        # multiple times with different arguments.
        if config.build_type not in config.get_allowed_top_level_build_values():
            raise RuntimeError(f"Invalid '{config.build_type}' option given to --build-type. ")

        # Build everything: shiboken6, shiboken6-generator and PySide6.
        help_requested = '--help' in self.sub_argv or '-h' in self.sub_argv

        if help_requested:
            self.add_setup_internal_invocation(config.pyside_option_name)

        elif config.is_top_level_build_all():
            extra_args = []

            # extra_args might contain the location of the built host
            # shiboken, which needs to be passed to the other
            # target invocations.
            if config.is_cross_compile():
                extra_args = self.add_host_tools_setup_internal_invocation(config)

            self.add_setup_internal_invocation(
                config.shiboken_module_option_name,
                extra_args=extra_args)

            # Reuse the shiboken build for the generator package instead
            # of rebuilding it again.
            # Don't build it in a cross-build though.
            if not config.is_cross_compile():
                self.add_setup_internal_invocation(
                    config.shiboken_generator_option_name,
                    reuse_build=True)

            self.add_setup_internal_invocation(config.pyside_option_name,
                                               extra_args=extra_args)

        elif config.is_top_level_build_shiboken_module():
            self.add_setup_internal_invocation(config.shiboken_module_option_name)

        elif config.is_top_level_build_shiboken_generator():
            self.add_setup_internal_invocation(config.shiboken_generator_option_name)

        elif config.is_top_level_build_pyside():
            self.add_setup_internal_invocation(config.pyside_option_name)

        for cmd in self.invocations_list:
            cmd_as_string = " ".join(cmd)
            exit_code = run_process(cmd)
            if exit_code != 0:
                msg = textwrap.dedent(f"""
                    setup.py invocation failed with exit code: {exit_code}.\n\n
                    setup.py invocation was: {cmd_as_string}
                    """)
                raise RuntimeError(msg)

        if help_requested:
            print(ADDITIONAL_OPTIONS)

        # Cleanup temp query file.
        if config.shiboken_host_query_path:
            os.remove(config.shiboken_host_query_path)

    @staticmethod
    def run_setuptools_setup():
        """
        Runs setuptools.setup() once in a single setup.py
        sub-invocation.
        """

        kwargs = config.setup_kwargs
        setup(**kwargs)
