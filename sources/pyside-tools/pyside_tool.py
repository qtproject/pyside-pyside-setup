#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import sys
import os
from pathlib import Path
import subprocess
import sysconfig

from subprocess import Popen, PIPE
import PySide6 as ref_mod


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
    qt_tool_wrapper("rcc", ['-g', 'python'] + sys.argv[1:], True)


def qmltyperegistrar():
    qt_tool_wrapper("qmltyperegistrar", sys.argv[1:], True)


def qmllint():
    qt_tool_wrapper("qmllint", sys.argv[1:])


def qmlformat():
    qt_tool_wrapper("qmlformat", sys.argv[1:])


def qmlls():
    qt_tool_wrapper("qmlls", sys.argv[1:])


def assistant():
    qt_tool_wrapper(ui_tool_binary("assistant"), sys.argv[1:])


def _append_to_path_var(var, value):
    env_value = os.environ.get(var)
    if env_value:
        env_value = f'{env_value}{os.pathsep}{value}'
    else:
        env_value = value
    os.environ[var] = env_value


def designer():
    # Add the examples to PYSIDE_DESIGNER_PLUGINS, as determined by starting from
    # PySide6/scripts.
    pyside_dir = Path(__file__).resolve().parents[1]

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
    # Add the Wiggly Widget example
    wiggly_dir = os.fspath(pyside_dir / 'examples' / 'widgetbinding')
    _append_to_path_var('PYSIDE_DESIGNER_PLUGINS', wiggly_dir)
    taskmenu_dir = os.fspath(pyside_dir / 'examples' / 'designer' / 'taskmenuextension')
    _append_to_path_var('PYSIDE_DESIGNER_PLUGINS', taskmenu_dir)

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


if __name__ == "__main__":
    main()
