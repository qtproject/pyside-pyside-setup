# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import time
from pathlib import Path
from sysconfig import get_config_var, get_platform

from packaging.version import parse as parse_version
from setuptools.errors import SetupError

from .options import OPTION
from .qtinfo import QtInfo
from .utils import memoize, parse_cmake_conf_assignments_by_key
from . import PYSIDE


@memoize
def get_package_timestamp():
    """ In a Coin CI build the returned timestamp will be the
        Coin integration id timestamp. For regular builds it's
        just the current timestamp or a user provided one."""
    option_value = OPTION["PACKAGE_TIMESTAMP"]
    return option_value if option_value else int(time.time())


def get_qt_version():
    qtinfo = QtInfo()
    qt_version = qtinfo.version

    if not qt_version:
        raise SetupError("Failed to query the Qt version with qmake {qtinfo.qmake_command}")

    if parse_version(qtinfo.version) < parse_version("5.7"):
        raise SetupError(f"Incompatible Qt version detected: {qt_version}. "
                         "A Qt version >= 5.7 is required.")

    return qt_version


@memoize
def get_package_version():
    """ Returns the version string for the PySide6 package. """
    setup_script_dir = Path.cwd()
    pyside_project_dir = setup_script_dir / "sources" / PYSIDE
    d = parse_cmake_conf_assignments_by_key(pyside_project_dir)
    major_version = d['pyside_MAJOR_VERSION']
    minor_version = d['pyside_MINOR_VERSION']
    patch_version = d['pyside_MICRO_VERSION']

    final_version = f"{major_version}.{minor_version}.{patch_version}"
    release_version_type = d.get('pyside_PRE_RELEASE_VERSION_TYPE')
    pre_release_version = d.get('pyside_PRE_RELEASE_VERSION')

    if release_version_type and not release_version_type.startswith("comm") and pre_release_version:
        final_version = f"{final_version}{release_version_type}{pre_release_version}"
    if release_version_type and release_version_type.startswith("comm"):
        final_version = f"{final_version}+{release_version_type}"

    # Add the current timestamp to the version number, to suggest it
    # is a development snapshot build.
    if OPTION["SNAPSHOT_BUILD"]:
        final_version = f"{final_version}.dev{get_package_timestamp()}"
    return final_version


def macos_qt_min_deployment_target():
    target = QtInfo().macos_min_deployment_target

    if not target:
        raise SetupError("Failed to query for Qt's QMAKE_MACOSX_DEPLOYMENT_TARGET.")
    return target


@memoize
def macos_pyside_min_deployment_target():
    """
    Compute and validate PySide6 MACOSX_DEPLOYMENT_TARGET value.
    Candidate sources that are considered:
        - setup.py provided value
        - maximum value between minimum deployment target of the
          Python interpreter and the minimum deployment target of
          the Qt libraries.
    If setup.py value is provided, that takes precedence.
    Otherwise use the maximum of the above mentioned two values.
    """
    python_target = get_config_var('MACOSX_DEPLOYMENT_TARGET') or None
    qt_target = macos_qt_min_deployment_target()
    setup_target = OPTION["MACOS_DEPLOYMENT_TARGET"]

    qt_target_split = [int(x) for x in qt_target.split('.')]
    if python_target:
        # macOS Big Sur returns a number not a string
        python_target_split = [int(x) for x in str(python_target).split('.')]
    if setup_target:
        setup_target_split = [int(x) for x in setup_target.split('.')]

    message = ("Can't set MACOSX_DEPLOYMENT_TARGET value to {} because "
               "{} was built with minimum deployment target set to {}.")
    # setup.py provided OPTION["MACOS_DEPLOYMENT_TARGET"] value takes
    # precedence.
    if setup_target:
        if python_target and setup_target_split < python_target_split:
            raise SetupError(message.format(setup_target, "Python", python_target))
        if setup_target_split < qt_target_split:
            raise SetupError(message.format(setup_target, "Qt", qt_target))
        # All checks clear, use setup.py provided value.
        return setup_target

    # Setup.py value not provided,
    # use same value as provided by Qt.
    if python_target:
        maximum_target = '.'.join([str(e) for e in max(python_target_split, qt_target_split)])
    else:
        maximum_target = qt_target
    return maximum_target


@memoize
def macos_plat_name():
    deployment_target = macos_pyside_min_deployment_target()
    # Example triple "macosx-10.12-x86_64".
    plat = get_platform().split("-")
    plat_name = f"{plat[0]}-{deployment_target}-{plat[2]}"
    return plat_name
