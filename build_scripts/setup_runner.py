#############################################################################
##
## Copyright (C) 2018 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of Qt for Python.
##
## $QT_BEGIN_LICENSE:LGPL$
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## GNU Lesser General Public License Usage
## Alternatively, this file may be used under the terms of the GNU Lesser
## General Public License version 3 as published by the Free Software
## Foundation and appearing in the file LICENSE.LGPL3 included in the
## packaging of this file. Please review the following information to
## ensure the GNU Lesser General Public License version 3 requirements
## will be met: https://www.gnu.org/licenses/lgpl-3.0.html.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 2.0 or (at your option) the GNU General
## Public license version 3 or any later version approved by the KDE Free
## Qt Foundation. The licenses are as published by the Free Software
## Foundation and appearing in the file LICENSE.GPL2 and LICENSE.GPL3
## included in the packaging of this file. Please review the following
## information to ensure the GNU General Public License requirements will
## be met: https://www.gnu.org/licenses/gpl-2.0.html and
## https://www.gnu.org/licenses/gpl-3.0.html.
##
## $QT_END_LICENSE$
##
#############################################################################

import os
import sys
import tempfile
import textwrap

from setuptools import setup  # Import setuptools before distutils
from setuptools._distutils import log

from build_scripts.config import config
from build_scripts.main import (cmd_class_dict, get_package_version,
                                get_setuptools_extension_modules)
from build_scripts.options import ADDITIONAL_OPTIONS, OPTION
from build_scripts.utils import run_process


class SetupRunner(object):
    def __init__(self, orig_argv):
        self.invocations_list = []

        # Keep the original args around in case we ever need to pass
        # modified arguments to the sub invocations.
        self.orig_argv = orig_argv
        self.sub_argv = list(orig_argv)

        self.setup_script_dir = os.getcwd()

    @staticmethod
    def cmd_line_argument_is_in_args(argument, args):
        """ Check if command line argument was passed in args. """
        return any(arg for arg in list(args) if "--" + argument in arg)

    @staticmethod
    def get_cmd_line_argument_in_args(argument, args):
        """ Gets the value of a cmd line argument passed in args. """
        for arg in list(args):
            if "--" + argument in arg:
                prefix = f"--{argument}"
                prefix_len = len(prefix) + 1
                return arg[prefix_len:]
        return None

    @staticmethod
    def remove_cmd_line_argument_in_args(argument, args):
        """ Remove command line argument from args. """
        return [arg for arg in list(args) if "--" + argument not in arg]

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

        # Prepare initial config.
        config.init_config(build_type=OPTION["BUILD_TYPE"],
                           internal_build_type=OPTION["INTERNAL_BUILD_TYPE"],
                           cmd_class_dict=cmd_class_dict,
                           package_version=get_package_version(),
                           ext_modules=get_setuptools_extension_modules(),
                           setup_script_dir=self.setup_script_dir,
                           cmake_toolchain_file=OPTION["CMAKE_TOOLCHAIN_FILE"],
                           quiet=OPTION["QUIET"])

        # Enable logging for both the top-level invocation of setup.py
        # as well as for child invocations. We we now use
        # setuptools._distutils.log instead of distutils.log, and this
        # new log object does not have its verbosity set by default
        # when setuptools instantiates a distutils Distribution object,
        # which calls
        # dist.parse_command_line() -> log.set_verbosity(self.verbose)
        # on the old distutils log object.
        # So we do it explicitly here.
        if not OPTION["QUIET"]:
            log.set_verbosity(log.INFO)

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
