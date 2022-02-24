#!/usr/bin/env python
# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2020 The Qt Company Ltd.
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


if __name__ == "__main__":
    main()
