# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
import os
import logging
import site
import sys

from build_scripts.log import log
from build_scripts.options import has_option, log, option_value
from build_scripts.utils import (expand_clang_variables, get_ci_qmake_path,
                                 get_qtci_virtualEnv, remove_tree, run_instruction)

log.setLevel(logging.INFO)

# Values must match COIN thrift
CI_HOST_OS = option_value("os")
CI_TARGET_OS = option_value("targetOs")
CI_HOST_ARCH = option_value("hostArch")
CI_TARGET_ARCH = option_value("targetArch")
CI_HOST_OS_VER = option_value("osVer")
CI_ENV_INSTALL_DIR = option_value("instdir")
CI_ENV_AGENT_DIR = option_value("agentdir") or "."
CI_COMPILER = option_value("compiler")
CI_FEATURES = []
_ci_features = option_value("features")
if _ci_features is not None:
    for f in _ci_features.split(', '):
        CI_FEATURES.append(f)
CI_RELEASE_CONF = has_option("packaging")


def call_testrunner(python_ver, buildnro):
    _pExe, _env, env_pip, env_python = get_qtci_virtualEnv(python_ver, CI_HOST_OS, CI_HOST_ARCH, CI_TARGET_ARCH)
    remove_tree(_env, True)
    # Pinning the virtualenv before creating one
    # Use pip3 if possible while pip seems to install the virtualenv to wrong dir in some OS
    python3 = "python3"
    if sys.platform == "win32":
        python3 = os.path.join(os.getenv("PYTHON3_PATH"), "python.exe")

    # we shouldn't install anything outside of virtualenv, while m1 is not virtualized yet
    if CI_HOST_OS == "MacOS" and CI_HOST_ARCH == "ARM64":
        v_env = "virtualenv"
        run_instruction([str(v_env), "-p", str(_pExe), str(_env)], "Failed to create virtualenv")
        run_instruction([env_pip, "install", "-r", "requirements.txt"], "Failed to install dependencies")
    else:
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
        run_instruction([env_pip, "install", "-r", "requirements.txt"], "Failed to install dependencies")
        # Install distro to replace missing platform.linux_distribution() in python3.8
        run_instruction([env_pip, "install", "distro"], "Failed to install distro")

    cmd = [env_python, "testrunner.py", "test", "--blacklist", "build_history/blacklist.txt",
           f"--buildno={buildnro}"]
    run_instruction(cmd, "Failed to run testrunner.py")

    qmake_path = get_ci_qmake_path(CI_ENV_INSTALL_DIR, CI_HOST_OS)

    # Try to install built wheels, and build some buildable examples.
    if CI_RELEASE_CONF:
        wheel_tester_path = os.path.join("testing", "wheel_tester.py")
        # We create wheels differently in Qt CI with Windows and there are no "old" wheels
        if CI_HOST_OS != "Windows":
            # Run the test for the old set of wheels
            cmd = [env_python, wheel_tester_path, qmake_path]
            run_instruction(cmd, "Error while running wheel_tester.py on old wheels")

            # Uninstalling the other wheels
            run_instruction([env_pip, "uninstall", "shiboken6", "shiboken6_generator", "pyside6", "-y"],
                            "Failed to uninstall old wheels")

        # Run the test for the new set of wheels
        cmd = [env_python, wheel_tester_path, qmake_path, "--wheels-dir=dist_new", "--new"]
        run_instruction(cmd, "Error while running wheel_tester.py on new wheels")


def run_test_instructions():
    # Remove some environment variables that impact cmake
    arch = '32' if CI_TARGET_ARCH == 'X86' else '64'
    expand_clang_variables(arch)
    for env_var in ['CC', 'CXX']:
        if os.environ.get(env_var):
            del os.environ[env_var]

    os.chdir(CI_ENV_AGENT_DIR)
    testRun = 0

    # In win machines, there are additional python versions to test with
    if CI_HOST_OS == "Windows":
        if (os.environ.get('HOST_OSVERSION_COIN')).startswith('windows_10'):
            call_testrunner("3.10.0", str(testRun))
        else:
            call_testrunner("3.7.9", str(testRun))
    elif CI_HOST_OS == "Linux":
        call_testrunner("3.8", str(testRun))
    else:
        call_testrunner("3", str(testRun))


if __name__ == "__main__":
    run_test_instructions()
