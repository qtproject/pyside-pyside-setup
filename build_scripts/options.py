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

try:
    from setuptools._distutils import log
    from setuptools import Command
except ModuleNotFoundError:
    # This is motivated by our CI using an old version of setuptools
    # so then the coin_build_instructions.py script is executed, and
    # import from this file, it was failing.
    from distutils import log
    from distutils.cmd import Command
from shutil import which
import sys
import os
import warnings
from pathlib import Path

from .qtinfo import QtInfo
from .utils import memoize


_AVAILABLE_MKSPECS = ["ninja", "msvc", "mingw"] if sys.platform == "win32" else ["ninja", "make"]


# Global options not which are not part of the commands
ADDITIONAL_OPTIONS = """
Additional options:
  --limited-api                        Use Limited API [yes/no]
  ---macos-use-libc++                  Use libc++ on macOS
  --snapshot-build                     Snapshot build
  --package-timestamp                  Package Timestamp
  --cmake-toolchain-file               Path to CMake toolchain to enable cross-compiling
  --shiboken-host-path                 Path to host shiboken package when cross-compiling
  --qt-host-path                       Path to host Qt installation when cross-compiling
"""


def _warn_multiple_option(option):
    warnings.warn(f'Option "{option}" occurs multiple times on the command line.')


def _warn_deprecated_option(option, replacement=None):
    w = f'Option "{option}" is deprecated and may be removed in a future release.'
    if replacement:
        w = f'{w}\nUse "{replacement}" instead.'
    warnings.warn(w)


class Options(object):
    def __init__(self):

        # Dictionary containing values of all the possible options.
        self.dict = {}

    def has_option(self, name, remove=True):
        """ Returns True if argument '--name' was passed on the command
        line. """
        option = f"--{name}"
        count = sys.argv.count(option)
        remove_count = count
        if not remove and count > 0:
            remove_count -= 1
        for _ in range(remove_count):
            sys.argv.remove(option)
        if count > 1:
            _warn_multiple_option(option)
        return count > 0

    def option_value(self, name, short_option_name=None, remove=True):
        """
        Returns the value of a command line option or environment
        variable.

        :param name: The name of the command line option or environment
         variable.

        :param remove: Whether the option and its value should be
         removed from sys.argv. Useful when there's a need to query for
         the value and also pass it along to setuptools for example.

        :return: Either the option value or None.
        """
        option = '--' + name
        short_option = '-' + short_option_name if short_option_name else None
        single_option_prefix = option + '='
        value = None
        for index in reversed(range(len(sys.argv))):
            arg = sys.argv[index]
            if arg == option or short_option and arg == short_option:
                if value:
                    _warn_multiple_option(option)
                else:
                    if index + 1 >= len(sys.argv):
                        raise RuntimeError(f"The option {option} requires a value")
                    value = sys.argv[index + 1]

                if remove:
                    sys.argv[index:index + 2] = []

            elif arg.startswith(single_option_prefix):
                if value:
                    _warn_multiple_option(option)
                else:
                    value = arg[len(single_option_prefix):]

                if remove:
                    sys.argv[index:index + 1] = []

        if value is None:
            value = os.getenv(name.upper().replace('-', '_'))

        self.dict[name] = value
        return value


options = Options()


def has_option(*args, **kwargs):
    return options.has_option(*args, **kwargs)


def option_value(*args, **kwargs):
    return options.option_value(*args, **kwargs)


def _jobs_option_value():
    """Option value for parallel builds."""
    value = option_value('parallel', short_option_name='j')
    if value:
        return '-j' + value if not value.startswith('-j') else value
    return ''


# Declare options which need to be known when instantiating the DistUtils
# commands or even earlier during SetupRunner.run().
OPTION = {
    "BUILD_TYPE": option_value("build-type"),
    "INTERNAL_BUILD_TYPE": option_value("internal-build-type"),
    # number of parallel build jobs
    "JOBS": _jobs_option_value(),
    # Legacy, not used any more.
    "JOM": has_option('jom'),
    "MACOS_USE_LIBCPP": has_option("macos-use-libc++"),
    "QUIET": has_option('quiet', remove=False),
    "SNAPSHOT_BUILD": has_option("snapshot-build"),
    "LIMITED_API": option_value("limited-api"),
    "PACKAGE_TIMESTAMP": option_value("package-timestamp"),
    # This is used automatically by distutils.command.install object, to
    # specify the final installation location.
    "FINAL_INSTALL_PREFIX": option_value("prefix", remove=False),
    "CMAKE_TOOLCHAIN_FILE": option_value("cmake-toolchain-file"),
    "SHIBOKEN_HOST_PATH": option_value("shiboken-host-path"),
    "SHIBOKEN_HOST_PATH_QUERY_FILE": option_value("internal-shiboken-host-path-query-file"),
    "QT_HOST_PATH": option_value("qt-host-path")
    # This is used to identify the template for doc builds
}
_deprecated_option_jobs = option_value('jobs')
if _deprecated_option_jobs:
    _warn_deprecated_option('jobs', 'parallel')
    OPTION["JOBS"] = _deprecated_option_jobs


class DistUtilsCommandMixin(object):
    """Mixin for the DistUtils build/install commands handling the options."""

    _static_class_finalized_once = False

    mixin_user_options = [
        ('avoid-protected-hack', None, 'Force --avoid-protected-hack'),
        ('debug', None, 'Build with debug information'),
        ('relwithdebinfo', None, 'Build in release mode with debug information'),
        ('only-package', None, 'Package only'),
        ('no-strip', None, 'Do not strip package libraries (release mode)'),
        ('standalone', None, 'Standalone build'),
        ('ignore-git', None, 'Do update subrepositories'),
        ('skip-docs', None, 'Skip documentation build'),
        ('no-examples', None, 'Do not build examples'),
        ('no-jom', None, 'Do not use jom (MSVC)'),
        ('build-tests', None, 'Build tests'),
        ('use-xvfb', None, 'Use Xvfb for testing'),
        ('reuse-build', None, 'Reuse existing build'),
        ('compiler-launcher=', None, 'Use a compiler launcher like ccache or sccache for builds'),
        ('skip-cmake', None, 'Skip CMake step'),
        ('skip-make-install', None, 'Skip install step'),
        ('skip-packaging', None, 'Skip packaging step'),
        ('verbose-build', None, 'Verbose build'),
        ('sanitize-address', None, 'Build with address sanitizer'),
        ('shorter-paths', None, 'Use shorter paths'),
        ('doc-build-online', None, 'Build online documentation'),
        ('qtpaths=', None, 'Path to qtpaths'),
        ('qmake=', None, 'Path to qmake (deprecated, use qtpaths)'),
        ('qt=', None, 'Qt version'),
        ('qt-target-path=', None,
         'Path to device Qt installation (use Qt libs when cross-compiling)'),
        ('cmake=', None, 'Path to CMake'),
        ('openssl=', None, 'Path to OpenSSL libraries'),

        # FIXME: Deprecated in favor of shiboken-target-path
        ('shiboken-config-dir=', None, 'shiboken configuration directory'),

        ('shiboken-target-path=', None, 'Path to target shiboken package'),
        ('python-target-path=', None, 'Path to target Python installation / prefix'),
        ('make-spec=', None, 'Qt make-spec'),
        ('macos-arch=', None, 'macOS architecture'),
        ('macos-sysroot=', None, 'macOS sysroot'),
        ('macos-deployment-target=', None, 'macOS deployment target'),
        ('skip-modules=', None, 'Qt modules to be skipped'),
        ('module-subset=', None, 'Qt modules to be built'),
        ('rpath=', None, 'RPATH'),
        ('qt-conf-prefix=', None, 'Qt configuration prefix'),
        ('qt-src-dir=', None, 'Qt source directory'),
        ('no-qt-tools', None, 'Do not copy the Qt tools'),
        ('pyside-numpy-support', None, 'libpyside: Add (experimental) numpy support'),
        ('internal-cmake-install-dir-query-file-path=', None,
         'Path to file where the CMake install path of the project will be saved'),

        # We redeclare plat-name as an option so it's recognized by the
        # install command and doesn't throw an error.
        ('plat-name=', None, 'The platform name for which we are cross-compiling'),
        ]

    def __init__(self):
        self.avoid_protected_hack = False
        self.debug = False
        self.relwithdebinfo = False
        self.no_strip = False
        self.only_package = False
        self.standalone = False
        self.ignore_git = False
        self.skip_docs = False
        self.no_examples = False
        self.no_jom = False
        self.build_tests = False
        self.use_xvfb = False
        self.reuse_build = False
        self.compiler_launcher = None
        self.skip_cmake = False
        self.skip_make_install = False
        self.skip_packaging = False
        self.verbose_build = False
        self.sanitize_address = False
        self.snapshot_build = False
        self.shorter_paths = False
        self.doc_build_online = False
        self.qtpaths = None
        self.qmake = None
        self.has_qmake_option = False
        self.qt = '5'
        self.qt_host_path = None
        self.qt_target_path = None
        self.cmake = None
        self.openssl = None
        self.shiboken_config_dir = None
        self.shiboken_host_path = None
        self.shiboken_host_path_query_file = None
        self.shiboken_target_path = None
        self.python_target_path = None
        self.is_cross_compile = False
        self.cmake_toolchain_file = None
        self.make_spec = None
        self.macos_arch = None
        self.macos_sysroot = None
        self.macos_deployment_target = None
        self.skip_modules = None
        self.module_subset = None
        self.rpath = None
        self.qt_conf_prefix = None
        self.qt_src_dir = None
        self.no_qt_tools = False
        self.pyside_numpy_support = False
        self.plat_name = None
        self.internal_cmake_install_dir_query_file_path = None
        self._per_command_mixin_options_finalized = False

        # When initializing a command other than the main one (so the
        # first one), we need to copy the user options from the main
        # command to the new command options dict. Then
        # Distribution.get_command_obj will pick up the copied options
        # ensuring that all commands that inherit from
        # the mixin, get our custom properties set by the time
        # finalize_options is called.
        if DistUtilsCommandMixin._static_class_finalized_once:
            current_command: Command = self
            dist = current_command.distribution
            main_command_name = dist.commands[0]
            main_command_opts = dist.get_option_dict(main_command_name)
            current_command_name = current_command.get_command_name()
            current_command_opts = dist.get_option_dict(current_command_name)
            mixin_options_set = self.get_mixin_options_set()
            for key, value in main_command_opts.items():
                if key not in current_command_opts and key in mixin_options_set:
                    current_command_opts[key] = value

    @staticmethod
    @memoize
    def get_mixin_options_set():
        keys = set()
        for (name, _, _) in DistUtilsCommandMixin.mixin_user_options:
            keys.add(name.rstrip("=").replace("-", "_"))
        return keys


    def mixin_finalize_options(self):
        # The very first we finalize options, record that.
        if not DistUtilsCommandMixin._static_class_finalized_once:
            DistUtilsCommandMixin._static_class_finalized_once = True

        # Ensure we finalize once per command object, rather than per
        # setup.py invocation. We want to have the option values
        # available in all commands that derive from the mixin.
        if not self._per_command_mixin_options_finalized:
            self._per_command_mixin_options_finalized = True
            self._do_finalize()

    def _do_finalize(self):
        # is_cross_compile must be set before checking for qtpaths/qmake
        # because we DON'T want those to be found when cross compiling.
        # Currently when cross compiling, qt-target-path MUST be used.
        using_cmake_toolchain_file = False
        cmake_toolchain_file = None
        if OPTION["CMAKE_TOOLCHAIN_FILE"]:
            self.is_cross_compile = True
            using_cmake_toolchain_file = True
            cmake_toolchain_file = OPTION["CMAKE_TOOLCHAIN_FILE"]
            self.cmake_toolchain_file = cmake_toolchain_file

        if not self._determine_defaults_and_check():
            sys.exit(-1)
        OPTION['AVOID_PROTECTED_HACK'] = self.avoid_protected_hack
        OPTION['DEBUG'] = self.debug
        OPTION['RELWITHDEBINFO'] = self.relwithdebinfo
        OPTION['NO_STRIP'] = self.no_strip
        OPTION['ONLYPACKAGE'] = self.only_package
        OPTION['STANDALONE'] = self.standalone
        OPTION['IGNOREGIT'] = self.ignore_git
        OPTION['SKIP_DOCS'] = self.skip_docs
        OPTION['NOEXAMPLES'] = self.no_examples
        OPTION['BUILDTESTS'] = self.build_tests
        OPTION['NO_JOM'] = self.no_jom
        OPTION['XVFB'] = self.use_xvfb
        OPTION['REUSE_BUILD'] = self.reuse_build
        OPTION['COMPILER_LAUNCHER'] = self.compiler_launcher
        OPTION['SKIP_CMAKE'] = self.skip_cmake
        OPTION['SKIP_MAKE_INSTALL'] = self.skip_make_install
        OPTION['SKIP_PACKAGING'] = self.skip_packaging
        OPTION['VERBOSE_BUILD'] = self.verbose_build
        if self.verbose_build:
            log.set_verbosity(1)
        OPTION['SANITIZE_ADDRESS'] = self.sanitize_address
        OPTION['SHORTER_PATHS'] = self.shorter_paths
        OPTION['DOC_BUILD_ONLINE'] = self.doc_build_online

        qtpaths_abs_path = None
        if self.qtpaths:
            qtpaths_abs_path = os.path.abspath(self.qtpaths)
            OPTION['QTPATHS'] = qtpaths_abs_path
        # FIXME PYSIDE7: Remove qmake handling
        # make qtinfo.py independent of relative paths.
        qmake_abs_path = None
        if self.qmake:
            qmake_abs_path = os.path.abspath(self.qmake)
            OPTION['QMAKE'] = qmake_abs_path
        OPTION['HAS_QMAKE_OPTION'] = self.has_qmake_option
        OPTION['QT_VERSION'] = self.qt
        self.qt_host_path = OPTION['QT_HOST_PATH']
        OPTION['QT_TARGET_PATH'] = self.qt_target_path

        qt_target_path = None
        if self.qt_target_path:
            qt_target_path = self.qt_target_path

        # We use the CMake project to find host Qt if neither qmake or
        # qtpaths is available. This happens when building the host
        # tools in the overall cross-building process.
        use_cmake = False
        if using_cmake_toolchain_file or \
                (not self.qmake and not self.qtpaths and self.qt_target_path):
            use_cmake = True

        QtInfo().setup(qtpaths_abs_path, self.cmake, qmake_abs_path,
                       self.has_qmake_option,
                       use_cmake=use_cmake,
                       qt_target_path=qt_target_path,
                       cmake_toolchain_file=cmake_toolchain_file)

        try:
            QtInfo().prefix_dir
        except Exception as e:
            if not self.qt_target_path:
                log.error(
                    "\nCould not find Qt. You can pass the --qt-target-path=<qt-dir> option as a "
                    "hint where to find Qt. Error was:\n\n\n")
            else:
                log.error(
                    f"\nCould not find Qt via provided option --qt-target-path={qt_target_path} "
                    "Error was:\n\n\n")
            raise e

        OPTION['CMAKE'] = os.path.abspath(self.cmake)
        OPTION['OPENSSL'] = self.openssl
        OPTION['SHIBOKEN_CONFIG_DIR'] = self.shiboken_config_dir
        if self.shiboken_config_dir:
            _warn_deprecated_option('shiboken-config-dir', 'shiboken-target-path')

        self.shiboken_host_path = OPTION['SHIBOKEN_HOST_PATH']
        self.shiboken_host_path_query_file = OPTION['SHIBOKEN_HOST_PATH_QUERY_FILE']

        if not self.shiboken_host_path and self.shiboken_host_path_query_file:
            try:
                queried_shiboken_host_path = Path(self.shiboken_host_path_query_file).read_text()
                self.shiboken_host_path = queried_shiboken_host_path
                OPTION['SHIBOKEN_HOST_PATH'] = queried_shiboken_host_path
            except Exception as e:
                log.error(
                    f"\n Could not find shiboken host tools via the query file: "
                    f"{self.shiboken_host_path_query_file:} Error was:\n\n\n")
                raise e

        OPTION['SHIBOKEN_TARGET_PATH'] = self.shiboken_target_path
        OPTION['PYTHON_TARGET_PATH'] = self.python_target_path
        OPTION['MAKESPEC'] = self.make_spec
        OPTION['MACOS_ARCH'] = self.macos_arch
        OPTION['MACOS_SYSROOT'] = self.macos_sysroot
        OPTION['MACOS_DEPLOYMENT_TARGET'] = self.macos_deployment_target
        OPTION['SKIP_MODULES'] = self.skip_modules
        OPTION['MODULE_SUBSET'] = self.module_subset
        OPTION['RPATH_VALUES'] = self.rpath
        OPTION['QT_CONF_PREFIX'] = self.qt_conf_prefix
        OPTION['QT_SRC'] = self.qt_src_dir
        OPTION['NO_QT_TOOLS'] = self.no_qt_tools
        OPTION['PYSIDE_NUMPY_SUPPORT'] = self.pyside_numpy_support

        if not self._extra_checks():
            sys.exit(-1)

    def _extra_checks(self):
        if self.is_cross_compile and not self.plat_name:
            log.error(f"No value provided to --plat-name while cross-compiling.")
            return False
        return True

    def _find_qtpaths_in_path(self):
        if not self.qtpaths:
            self.qtpaths = which("qtpaths")
        if not self.qtpaths:
            self.qtpaths = which("qtpaths6")

    def _determine_defaults_and_check(self):
        if not self.cmake:
            self.cmake = which("cmake")
        if not self.cmake:
            log.error("cmake could not be found.")
            return False
        if not os.path.exists(self.cmake):
            log.error(f"'{self.cmake}' does not exist.")
            return False

        # When cross-compiling, we only accept the qt-target-path
        # option and don't rely on auto-searching in PATH or the other
        # qtpaths / qmake options.
        # We also don't do auto-searching if qt-target-path is passed
        # explicitly. This is to help with the building of host tools
        # while cross-compiling.
        if not self.is_cross_compile and not self.qt_target_path:
            # Enforce usage of qmake in QtInfo if it was given explicitly.
            if self.qmake:
                self.has_qmake_option = True
                _warn_deprecated_option('qmake', 'qtpaths')

            # If no option was given explicitly, prefer to find qtpaths
            # in PATH.
            if not self.qmake and not self.qtpaths:
                self._find_qtpaths_in_path()

            # If no tool was specified and qtpaths was not found in PATH,
            # ask to provide a path to qtpaths.
            if not self.qtpaths and not self.qmake and not self.qt_target_path:
                log.error("No value provided to --qtpaths option. Please provide one to find Qt.")
                return False

            # Validate that the given tool path exists.
            if self.qtpaths and not os.path.exists(self.qtpaths):
                log.error(f"The specified qtpaths path '{self.qtpaths}' does not exist.")
                return False

            if self.qmake and not os.path.exists(self.qmake):
                log.error(f"The specified qmake path '{self.qmake}' does not exist.")
                return False
        else:
            # Check for existence, but don't require if it's not set. A
            # check later will be done to see if it's needed.
            if self.qt_target_path and not os.path.exists(self.qt_target_path):
                log.error(f"Provided --qt-target-path='{self.qt_target_path}' path does not exist.")
                return False

        if not self.make_spec:
            self.make_spec = _AVAILABLE_MKSPECS[0]
        if self.make_spec not in _AVAILABLE_MKSPECS:
            log.error(f'Invalid option --make-spec "{self.make_spec}". '
                      f'Available values are {_AVAILABLE_MKSPECS}')
            return False

        if OPTION["JOBS"] and sys.platform == 'win32' and self.no_jom:
            log.error("Option --jobs can only be used with jom on Windows.")
            return False

        return True
