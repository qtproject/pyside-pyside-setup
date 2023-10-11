#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import importlib
import os
import subprocess
import sys
import sysconfig
from pathlib import Path
from subprocess import PIPE, Popen

import PySide6 as ref_mod

VIRTUAL_ENV = "VIRTUAL_ENV"


def is_virtual_env():
    return sys.prefix != sys.base_prefix


def init_virtual_env():
    """PYSIDE-2251: Enable running from a non-activated virtual environment
       as is the case for Visual Studio Code by setting the VIRTUAL_ENV
       variable which is used by the Qt Designer plugin."""
    if is_virtual_env() and not os.environ.get(VIRTUAL_ENV):
        os.environ[VIRTUAL_ENV] = sys.prefix


def main():
    # This will take care of "pyside6-lupdate" listed as an entrypoint
    # in setup.py are copied to 'scripts/..'
    cmd = os.path.join("..", os.path.basename(sys.argv[0]))
    command = [os.path.join(os.path.dirname(os.path.realpath(__file__)), cmd)]
    command.extend(sys.argv[1:])
    sys.exit(subprocess.call(command))


def qt_tool_wrapper(qt_tool, args, libexec=False):
    # Taking care of pyside6-uic, pyside6-rcc, and pyside6-designer
    # listed as an entrypoint in setup.py
    pyside_dir = Path(ref_mod.__file__).resolve().parent
    if libexec and sys.platform != "win32":
        exe = pyside_dir / 'Qt' / 'libexec' / qt_tool
    else:
        exe = pyside_dir / qt_tool

    cmd = [os.fspath(exe)] + args
    proc = Popen(cmd, stderr=PIPE)
    out, err = proc.communicate()
    if err:
        msg = err.decode("utf-8")
        command = ' '.join(cmd)
        print(f"Error: {msg}\nwhile executing '{command}'")
    sys.exit(proc.returncode)


def pyside_script_wrapper(script_name):
    """Launch a script shipped with PySide."""
    script = Path(__file__).resolve().parent / script_name
    command = [sys.executable, os.fspath(script)] + sys.argv[1:]
    sys.exit(subprocess.call(command))


def ui_tool_binary(binary):
    """Return the binary of a UI tool (App bundle on macOS)."""
    if sys.platform != "darwin":
        return binary
    name = binary[0:1].upper() + binary[1:]
    return f"{name}.app/Contents/MacOS/{name}"


def lrelease():
    qt_tool_wrapper("lrelease", sys.argv[1:])


def lupdate():
    qt_tool_wrapper("lupdate", sys.argv[1:])


def uic():
    qt_tool_wrapper("uic", ['-g', 'python'] + sys.argv[1:], True)


def rcc():
    args = []
    user_args = sys.argv[1:]
    if "--binary" not in user_args:
        args.extend(['-g', 'python'])
    args.extend(user_args)
    qt_tool_wrapper("rcc", args, True)


def qmltyperegistrar():
    qt_tool_wrapper("qmltyperegistrar", sys.argv[1:], True)


def qmlimportscanner():
    qt_tool_wrapper("qmlimportscanner", sys.argv[1:], True)


def qmlcachegen():
    qt_tool_wrapper("qmlcachegen", sys.argv[1:], True)


def qmllint():
    qt_tool_wrapper("qmllint", sys.argv[1:])


def qmlformat():
    qt_tool_wrapper("qmlformat", sys.argv[1:])


def qmlls():
    qt_tool_wrapper("qmlls", sys.argv[1:])


def assistant():
    qt_tool_wrapper(ui_tool_binary("assistant"), sys.argv[1:])


def _extend_path_var(var, value, prepend=False):
    env_value = os.environ.get(var)
    if env_value:
        env_value = (f'{value}{os.pathsep}{env_value}'
                     if prepend else f'{env_value}{os.pathsep}{value}')
    else:
        env_value = value
    os.environ[var] = env_value


def designer():
    init_virtual_env()

    # https://www.python.org/dev/peps/pep-0384/#linkage :
    # "On Unix systems, the ABI is typically provided by the python executable
    # itself", that is, libshiboken does not link against any Python library
    # and expects to get these symbols from a python executable. Since no
    # python executable is involved when loading this plugin, pre-load python.so
    # This should also help to work around a numpy issue, see
    # https://stackoverflow.com/questions/49784583/numpy-import-fails-on-multiarray-extension-library-when-called-from-embedded-pyt
    major_version = sys.version_info[0]
    minor_version = sys.version_info[1]
    os.environ['PY_MAJOR_VERSION'] = str(major_version)
    os.environ['PY_MINOR_VERSION'] = str(minor_version)
    if sys.platform == 'linux':
        # Determine library name (examples/utils/pyside_config.py)
        version = f'{major_version}.{minor_version}'
        library_name = f'libpython{version}{sys.abiflags}.so'
        os.environ['LD_PRELOAD'] = library_name
    elif sys.platform == 'darwin':
        library_name = sysconfig.get_config_var("LDLIBRARY")
        framework_prefix = sysconfig.get_config_var("PYTHONFRAMEWORKPREFIX")
        lib_path = os.fspath(Path(framework_prefix) / library_name)
        os.environ['DYLD_INSERT_LIBRARIES'] = lib_path
    elif sys.platform == 'win32':
        # Find Python DLLs from the base installation
        if is_virtual_env():
            _extend_path_var("PATH", os.fspath(Path(sys._base_executable).parent), True)

    qt_tool_wrapper(ui_tool_binary("designer"), sys.argv[1:])


def linguist():
    qt_tool_wrapper(ui_tool_binary("linguist"), sys.argv[1:])


def genpyi():
    pyside_dir = Path(__file__).resolve().parents[1]
    support = pyside_dir / "support"
    cmd = support / "generate_pyi.py"
    command = [sys.executable, os.fspath(cmd)] + sys.argv[1:]
    sys.exit(subprocess.call(command))


def metaobjectdump():
    pyside_script_wrapper("metaobjectdump.py")


def project():
    pyside_script_wrapper("project.py")


def qml():
    pyside_script_wrapper("qml.py")


def qtpy2cpp():
    pyside_script_wrapper("qtpy2cpp.py")


def deploy():
    pyside_script_wrapper("deploy.py")


def android_deploy():
    if not sys.platform == "linux":
        print("pyside6-android-deploy only works from a Linux host")
    else:
        dependent_packages = ["jinja2", "pkginfo"]
        for dependent_package in dependent_packages:
            if not bool(importlib.util.find_spec(dependent_package)):
                command = [sys.executable, "-m", "pip", "install", dependent_package]
                subprocess.run(command)
        pyside_script_wrapper("android_deploy.py")


if __name__ == "__main__":
    main()
