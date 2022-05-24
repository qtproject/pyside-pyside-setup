# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

"""
module_collector.py

Collect a number of modules listed on the command line.

The purpose of this script is to generate the scripts needed for
a complete isolation of the signature extension.

Usage:

Run this script in one of the used python versions.
It will create an executable archive of the files on the command line.
"""

import sys
import os
import argparse
import pickle
from textwrap import dedent
from pathlib import path


def source_archive(module, modname):
    fname = Path(module.__file__).stem + ".py"
    with open(fname) as source:
        text = source.read()
    encoded = text.replace("'''", "(triple_single)")
    # modname = module.__name__
    # Do not use: Some modules rename themselves!
    version = ".".join(map(str, sys.version_info[:3]))
    shortname = fname.stem
    preamble = dedent(fr"""
        # BEGIN SOURCE ARCHIVE    Python {version}  module {modname}

        sources = {{}} if "sources" not in globals() else sources
        sources["{modname}"] = '''\
        {encoded}'''.replace("(triple_single)", "'''")

        # END   SOURCE ARCHIVE    Python {version}  module {modname}
        """)
    return preamble


def read_all(modules):
    collected = ""
    for modname in modules:
        mod = __import__(modname)
        collected += source_archive(mod, modname)
    return collected


def license_header():
    license = Path(__file__).parent / "qt_python_license.txt"
    with license.open() as f:
        return f.read()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('modules', nargs="+")
    args = parser.parse_args()
    print("modules:", args.modules)
    ret = license_header() + read_all(args.modules)
    ma_mi = "_".join(map(str, sys.version_info[:2]))
    outpath = Path(__file__).parents[2] / Path("shibokenmodule",
        "files.dir", "shibokensupport", f"python_minilib_{ma_mi}.py")
    with outpath.open("w") as f:
        f.write(ret)
