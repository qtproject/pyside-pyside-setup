# This Python file uses the following encoding: utf-8
#############################################################################
##
## Copyright (C) 2021 The Qt Company Ltd.
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

"""
generate_pyi.py

This script generates the .pyi files for all PySide modules.
"""

import argparse
import inspect
import logging
import os
import sys
import typing

from pathlib import Path

# Can we use forward references?
USE_PEP563 = sys.version_info[:2] >= (3, 7)


def generate_all_pyi(outpath, options):
    ps = os.pathsep
    if options.sys_path:
        # make sure to propagate the paths from sys_path to subprocesses
        normpath = lambda x: os.fspath(Path(x).resolve())
        sys_path = [normpath(_) for _ in options.sys_path]
        sys.path[0:0] = sys_path
        pypath = ps.join(sys_path)
        os.environ["PYTHONPATH"] = pypath

    # now we can import
    global PySide6, inspect, typing, HintingEnumerator, build_brace_pattern
    import PySide6
    from PySide6.support.signature.lib.enum_sig import HintingEnumerator
    from PySide6.support.signature.lib.tool import build_brace_pattern
    from PySide6.support.signature.lib.pyi_generator import generate_pyi

    # propagate USE_PEP563 to the mapping module.
    # Perhaps this can be automated?
    PySide6.support.signature.mapping.USE_PEP563 = USE_PEP563

    import __feature__ as feature

    outpath = Path(outpath) if outpath and os.fspath(outpath) else Path(PySide6.__file__).parent
    name_list = PySide6.__all__ if options.modules == ["all"] else options.modules
    errors = ", ".join(set(name_list) - set(PySide6.__all__))
    if errors:
        raise ImportError(f"The module(s) '{errors}' do not exist")
    quirk1, quirk2 = "QtMultimedia", "QtMultimediaWidgets"
    if name_list == [quirk1]:
        logger.debug(f"Note: We must defer building of {quirk1}.pyi until {quirk2} is available")
        name_list = []
    elif name_list == [quirk2]:
        name_list = [quirk1, quirk2]
    for mod_name in name_list:
        import_name = "PySide6." + mod_name
        feature_id = feature.get_select_id(options.feature)
        with feature.force_selection(feature_id, import_name):
            generate_pyi(import_name, outpath, options)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This script generates the .pyi file for all PySide modules.")
    parser.add_argument("modules", nargs="+",
        help="'all' or the names of modules to build (QtCore QtGui etc.)")
    parser.add_argument("--quiet", action="store_true", help="Run quietly")
    parser.add_argument("--check", action="store_true", help="Test the output if on Python 3")
    parser.add_argument("--outpath",
        help="the output directory (default = binary location)")
    parser.add_argument("--sys-path", nargs="+",
        help="a list of strings prepended to sys.path")
    parser.add_argument("--feature", nargs="+", choices=["snake_case", "true_property"], default=[],
        help="""a list of feature names. Example: `--feature snake_case true_property`""")
    options = parser.parse_args()

    qtest_env = os.environ.get("QTEST_ENVIRONMENT", "")
    log_level = logging.DEBUG if qtest_env else logging.INFO
    if options.quiet:
        log_level = logging.WARNING
    logging.basicConfig(level=log_level)
    logger = logging.getLogger("generate_pyi")

    outpath = options.outpath
    if outpath and not Path(outpath).exists():
        os.makedirs(outpath)
        logger.info(f"+++ Created path {outpath}")
    options._pyside_call = True
    options.logger = logger
    options.is_ci = qtest_env == "ci"
    generate_all_pyi(outpath, options=options)
# eof
