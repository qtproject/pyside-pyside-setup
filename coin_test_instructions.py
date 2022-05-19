#############################################################################
##
## Copyright (C) 2019 The Qt Company Ltd.
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
import site
import sys
from os.path import expanduser
import pathlib
import urllib.request as urllib

from build_scripts.options import has_option, log, option_value
from build_scripts.utils import (expand_clang_variables, get_ci_qmake_path,
                                 get_qtci_virtualEnv, rmtree, run_instruction)

log.set_verbosity(log.INFO)

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
CI_TEST_WITH_PYPY = has_option("pypy")


def call_testrunner(python_ver, buildnro, pypy=None):

    env_python=""
    if python_ver == "pypy":
        print("running with " + pypy)
        env_python = pypy
    else:
        _pExe, _env, env_pip, env_python = get_qtci_virtualEnv(python_ver, CI_HOST_OS, CI_HOST_ARCH, CI_TARGET_ARCH)
        rmtree(_env, True)
        # Pinning the virtualenv before creating one
        # Use pip3 if possible while pip seems to install the virtualenv to wrong dir in some OS
        python3 = "python3"
        if sys.platform == "win32":
            python3 = os.path.join(os.getenv("PYTHON3_PATH"), "python.exe")

        if  CI_HOST_OS == "MacOS" and CI_HOST_ARCH == "ARM64": # we shouldn't install anything to m1, while it is not virtualized
            v_env = "virtualenv"
            run_instruction([v_env, "-p", _pExe,  _env], "Failed to create virtualenv")
        else:
            run_instruction([python3, "-m", "pip", "install", "--user", "virtualenv==20.7.2"], "Failed to pin virtualenv")
            # installing to user base might not be in PATH by default.
            env_path = os.path.join(site.USER_BASE, "bin")
            v_env = os.path.join(env_path, "virtualenv")
            if sys.platform == "win32":
                env_path = os.path.join(site.USER_BASE, "Scripts")
                v_env = os.path.join(env_path, "virtualenv.exe")
            try:
                run_instruction([v_env, "--version"], "Using default virtualenv")
            except Exception as e:
                v_env = "virtualenv"
            run_instruction([v_env, "-p", _pExe,  _env], "Failed to create virtualenv")
            # When the 'python_ver' variable is empty, we are using Python 2
            # Pip is always upgraded when CI template is provisioned, upgrading it in later phase may cause perm issue
            run_instruction([env_pip, "install", "-r", "requirements.txt"], "Failed to install dependencies")


    cmd = [env_python, "testrunner.py", "test", "--blacklist", "build_history/blacklist.txt",
           f"--buildno={buildnro}"]
    run_instruction(cmd, "Failed to run testrunner.py")

    qmake_path = get_ci_qmake_path(CI_ENV_INSTALL_DIR, CI_HOST_OS)

    # Try to install built wheels, and build some buildable examples.
    if CI_RELEASE_CONF:
        wheel_tester_path = os.path.join("testing", "wheel_tester.py")
        # Run the test for the old set of wheels
        cmd = [env_python, wheel_tester_path, qmake_path]
        run_instruction(cmd, "Error while running wheel_tester.py on old wheels")
        if python_ver == "pypy":
            return
        # Uninstalling the other wheels
        run_instruction([env_pip, "uninstall", "shiboken6", "shiboken6_generator", "pyside6", "-y"],
                        "Failed to uninstall old wheels")

        # Run the test for the new set of wheels
        cmd = [env_python, wheel_tester_path, qmake_path, "--wheels-dir=dist_new", "--new"]
        run_instruction(cmd, "Error while running wheel_tester.py on new wheels")


# move to utils
def install_pypy():
    localfile = None
    home = expanduser("~")
    file = "https://downloads.python.org/pypy/pypy3.8-v7.3.8-osx64.tar.bz2"
    target =os.path.join(home, "work", "pypy-3.8")
    pypy = os.path.join(target, "pypy3.8-v7.3.8-osx64", "bin", "pypy")
    if sys.platform == "win32":
        file = "http://ci-files01-hki.ci.local/input/pypy/pypy3.8-v7.3.8-win64.zip"
        pypy = os.path.join(target, "pypy3.8-v7.3.8-win64", "pypy.exe")
    if CI_HOST_OS == "Linux":
        file = "https://downloads.python.org/pypy/pypy3.8-v7.3.8-linux64.tar.bz2"
        pypy = os.path.join(target, "pypy3.8-v7.3.8-linux64", "bin", "pypy")

    for i in range(1, 10):
        try:
            log.info(f"Downloading fileUrl {file}, attempt #{i}")
            localfile, info = urllib.urlretrieve(file)
            break
        except urllib.URLError:
            pass
    if not localfile:
        log.error(f"Error downloading {file} : {info}")
        raise RuntimeError(f" Error downloading {file}")

    pathlib.Path(target).mkdir(parents=True, exist_ok=True)
    if sys.platform == "win32":
        cmd = ["7z", "x", "-y", localfile, "-o"+target]
    else:
        cmd = ["tar", "xjf", localfile, "-C", target]
    run_instruction(cmd, "Failed to extract pypy")
    return  pypy

# move to utils and rename
def build_with_pypy(pypy):
    run_instruction([pypy, "-m", "ensurepip"], "Failed to install pip")
    cmd = [pypy, "-m", "pip", "install", "-r", "requirements.txt"]
    run_instruction(cmd, "Failed to install requirements.txt")

    cmd = [pypy, "-m", "pip", "install", "numpy"]
    run_instruction(cmd, "Failed to install numpy")


def run_test_instructions():
    # Remove some environment variables that impact cmake
    arch = '32' if CI_TARGET_ARCH == 'X86' else '64'
    pypy = ""
    p_ver = "3"
    expand_clang_variables(arch)
    for env_var in ['CC', 'CXX']:
        if os.environ.get(env_var):
            del os.environ[env_var]
    os.chdir(CI_ENV_AGENT_DIR)
    testRun = 0

    if CI_TEST_WITH_PYPY:
        pypy = install_pypy()
        build_with_pypy(pypy)
        p_ver = "pypy"
        call_testrunner(p_ver, str(testRun), pypy)
    else:
        call_testrunner("3", str(testRun))


if __name__ == "__main__":
    run_test_instructions()
