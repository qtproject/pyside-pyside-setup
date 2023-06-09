# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
import calendar
import datetime
import logging
import os
import os.path
import site
import sys

from build_scripts.log import log
from build_scripts.options import has_option, option_value
from build_scripts.utils import (expand_clang_variables, get_ci_qtpaths_path,
                                 get_qtci_virtualEnv,
                                 parse_cmake_conf_assignments_by_key, remove_tree,
                                 run_instruction)

log.setLevel(logging.INFO)

# Values must match COIN thrift
CI_HOST_OS = option_value("os")
CI_TARGET_OS = option_value("targetOs")
CI_HOST_ARCH = option_value("hostArch")
CI_TARGET_ARCH = option_value("targetArch")
CI_HOST_OS_VER = option_value("osVer")
CI_ENV_INSTALL_DIR = option_value("instdir")
CI_ENV_AGENT_DIR = option_value("agentdir")
CI_COMPILER = option_value("compiler")
CI_USE_SCCACHE = option_value("compiler-launcher")
CI_INTEGRATION_ID = option_value("coinIntegrationId") or str(calendar.timegm(datetime.datetime.now().timetuple()))
CI_FEATURES = []
_ci_features = option_value("features")
if _ci_features is not None:
    for f in _ci_features.split(', '):
        CI_FEATURES.append(f)
CI_RELEASE_CONF = has_option("packaging")
CI_TEST_PHASE = option_value("phase")
if CI_TEST_PHASE not in ["ALL", "BUILD", "WHEEL"]:
    CI_TEST_PHASE = "ALL"


def get_current_script_path():
    """ Returns the absolute path containing this script. """
    try:
        this_file = __file__
    except NameError:
        this_file = sys.argv[0]
    this_file = os.path.abspath(this_file)
    return os.path.dirname(this_file)


def is_snapshot_build():
    """
    Returns True if project needs to be built with --snapshot-build

    This is true if the version found in .cmake.conf is not a
    pre-release version (no alphas, betas).

    This eliminates the need to remove the --snapshot-build option
    on a per-release branch basis (less things to remember to do
    for a release).
    """
    setup_script_dir = get_current_script_path()
    pyside_project_dir = os.path.join(setup_script_dir, "sources", "pyside6")

    d = parse_cmake_conf_assignments_by_key(pyside_project_dir)
    release_version_type = d.get('pyside_PRE_RELEASE_VERSION_TYPE')
    pre_release_version = d.get('pyside_PRE_RELEASE_VERSION')
    if pre_release_version and release_version_type:
        return True
    return False


def call_setup(python_ver, phase):
    print("call_setup")
    print("python_ver", python_ver)
    print("phase", phase)
    _pExe, _env, env_pip, env_python = get_qtci_virtualEnv(python_ver, CI_HOST_OS, CI_HOST_ARCH, CI_TARGET_ARCH)

    if phase in ["BUILD"]:
        remove_tree(_env, True)
        # Pinning the virtualenv before creating one
        # Use pip3 if possible while pip seems to install the virtualenv to wrong dir in some OS
        python3 = "python3"
        if sys.platform == "win32":
            python3 = os.path.join(os.getenv("PYTHON3_PATH"), "python.exe")
        run_instruction([python3, "-m", "pip", "install", "--user", "virtualenv==20.7.2"], "Failed to pin virtualenv")
        # installing to user base might not be in PATH by default.
        env_path = os.path.join(site.USER_BASE, "bin")
        v_env = os.path.join(env_path, "virtualenv")
        if sys.platform == "win32":
            env_path = os.path.join(site.USER_BASE, "Scripts")
            v_env = os.path.join(env_path, "virtualenv.exe")
        try:
            run_instruction([str(v_env), "--version"], "Using default virtualenv")
        except Exception as e:
            log.info("Failed to use the default virtualenv")
            log.info(f"{type(e).__name__}: {e}")
            v_env = "virtualenv"
        run_instruction([str(v_env), "-p", str(_pExe), str(_env)], "Failed to create virtualenv")
        # When the 'python_ver' variable is empty, we are using Python 2
        # Pip is always upgraded when CI template is provisioned, upgrading it in later phase may cause perm issue
        run_instruction([str(env_pip), "install", "-r", "requirements.txt"], "Failed to install dependencies")

    cmd = [env_python, "-u", "setup.py"]
    if phase in ["BUILD"]:
        cmd += ["build", "--standalone", "--unity"]
    elif phase in ["WHEEL"] or CI_RELEASE_CONF:
        cmd += ["bdist_wheel", "--reuse-build", "--standalone", "--skip-cmake", "--skip-make-install", "--only-package"]

    cmd += ["--build-tests",
            "--verbose-build"]

    if CI_TARGET_ARCH == "X86_64-ARM64":
        cmd += ["--macos-arch='x86_64;arm64'"]

    if CI_USE_SCCACHE:
        cmd += [f"--compiler-launcher={CI_USE_SCCACHE}"]

    cmd += ["--limited-api=yes"]

    if is_snapshot_build():
        cmd += ["--snapshot-build"]

    qtpaths_path = get_ci_qtpaths_path(CI_ENV_INSTALL_DIR, CI_HOST_OS)
    cmd.append(qtpaths_path)

    # Due to certain older CMake versions generating very long paths
    # (at least with CMake 3.6.2) when using the export() function,
    # pass the shorter paths option on Windows so we don't hit
    # the path character length limit (260).
    if CI_HOST_OS == "Windows":
        cmd += ["--shorter-paths"]

    cmd += ["--package-timestamp=" + CI_INTEGRATION_ID]

    env = os.environ
    run_instruction(cmd, "Failed to run setup.py for build", initial_env=env)

if __name__ == "__main__":

    # Remove some environment variables that impact cmake
    arch = '32' if CI_TARGET_ARCH == 'X86' else '64'
    expand_clang_variables(arch)
    for env_var in ['CC', 'CXX']:
        if os.environ.get(env_var):
            del os.environ[env_var]
    python_ver = "3"
    if CI_TARGET_OS in ["Linux"] and CI_HOST_ARCH !="aarch64":
        python_ver = "3.8"
    wheel_package_dir = "qfpa-p3.6"
    if CI_TARGET_OS in ["Windows"]:
        if (os.environ.get('HOST_OSVERSION_COIN')).startswith('windows_10'):
            python_ver = "3.10.0"
        else:
            python_ver = "3.7.9"
    if CI_TEST_PHASE in ["ALL", "BUILD"]:
        call_setup(python_ver, "BUILD")
    # Until CI has a feature to set more dynamic signing dir, make sure it actually exist
    if os.environ.get("QTEST_ENVIRONMENT") == "ci" and sys.platform == "win32":
        signing_dir = str(os.environ.get("PYSIDE_SIGNING_DIR"))
        print("Check for signing dir " + signing_dir)
        assert(os.path.isdir(signing_dir))
    if CI_TEST_PHASE in ["ALL", "WHEEL"] and sys.platform != "win32":
        # "Old" Windows wheels won't be signed anyway so there is no need to
        # create those, so that we don't accidentally release those.
        call_setup(python_ver, "WHEEL")
