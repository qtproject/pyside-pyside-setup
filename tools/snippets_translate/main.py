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

import argparse
import logging
import os
import re
import shutil
import sys
from enum import Enum
from pathlib import Path
from textwrap import dedent

from converter import snippet_translate

# Logger configuration
try:
    from rich.logging import RichHandler

    logging.basicConfig(
        level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
    )
    have_rich = True
    extra = {"markup": True}

    from rich.console import Console
    from rich.table import Table

except ModuleNotFoundError:
    # 'rich' not found, falling back to default logger"
    logging.basicConfig(level=logging.INFO)
    have_rich = False
    extra = {}

log = logging.getLogger("snippets_translate")

# Filter and paths configuration
SKIP_END = (".pro", ".pri", ".cmake", ".qdoc", ".yaml", ".frag", ".qsb", ".vert", "CMakeLists.txt")
SKIP_BEGIN = ("changes-", ".")
OUT_MAIN = Path("sources/pyside6/doc/codesnippets/")
OUT_SNIPPETS = OUT_MAIN / "doc/src/snippets/"
OUT_EXAMPLES = OUT_MAIN / "examples/"
SNIPPET_PATTERN = re.compile(r"//! \[([^]]+)\]")


class FileStatus(Enum):
    Exists = 0
    New = 1


def get_parser():
    parser = argparse.ArgumentParser(prog="snippets_translate")
    # List pyproject files
    parser.add_argument(
        "--qt",
        action="store",
        dest="qt_dir",
        required=True,
        help="Path to the Qt directory (QT_SRC_DIR)",
    )

    parser.add_argument(
        "--pyside",
        action="store",
        dest="pyside_dir",
        required=True,
        help="Path to the pyside-setup directory",
    )

    parser.add_argument(
        "-w",
        "--write",
        action="store_true",
        dest="write_files",
        help="Actually copy over the files to the pyside-setup directory",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbose",
        help="Generate more output",
    )

    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        dest="debug",
        help="Generate even more output",
    )

    parser.add_argument(
        "-s",
        "--single",
        action="store",
        dest="single_snippet",
        help="Path to a single file to be translated",
    )

    parser.add_argument(
        "--filter",
        action="store",
        dest="filter_snippet",
        help="String to filter the snippets to be translated",
    )
    return parser


def is_directory(directory):
    if not os.path.isdir(directory):
        log.error(f"Path '{directory}' is not a directory")
        return False
    return True


def check_arguments(options):

    # Notify 'write' option
    if options.write_files:
        if not opt_quiet:
            log.warning(
                f"Files will be copied from '{options.qt_dir}':\n" f"\tto '{options.pyside_dir}'"
            )
    else:
        msg = "This is a listing only, files are not being copied"
        if have_rich:
            msg = f"[green]{msg}[/green]"
        if not opt_quiet:
            log.info(msg, extra=extra)

    # Check 'qt_dir' and 'pyside_dir'
    if is_directory(options.qt_dir) and is_directory(options.pyside_dir):
        return True

    return False


def is_valid_file(x):
    file_name = x.name
    # Check END
    for ext in SKIP_END:
        if file_name.endswith(ext):
            return False

    # Check BEGIN
    for ext in SKIP_BEGIN:
        if file_name.startswith(ext):
            return False

    # Contains 'snippets' or 'examples' as subdirectory
    if not ("snippets" in x.parts or "examples" in x.parts):
        return False

    return True


def get_snippet_ids(line):
    """Extract the snippet ids for a line '//! [1] //! [2]'"""
    result = []
    for m in SNIPPET_PATTERN.finditer(line):
        result.append(m.group(1))
    return result


def get_snippets(data):
    """Extract (potentially overlapping) snippets from a C++ file indicated by //! [1]"""
    current_snippets = []  # Active ids
    snippets = []
    for line in data:
        new_ids = get_snippet_ids(line)
        for id in new_ids:
            if id in current_snippets:  # id encountered 2nd time: Snippet ends
                current_snippets.remove(id)
            else:
                current_snippets.append(id)

        if new_ids or current_snippets:
            snippets.append(line)

    return snippets


def get_license_from_file(filename):
    lines = []
    with open(filename, "r") as f:
        line = True
        while line:
            line = f.readline().rstrip()

            if line.startswith("/*") or line.startswith("**"):
                lines.append(line)
            # End of the comment
            if line.endswith("*/"):
                break
    if lines:
        # We know we have the whole block, so we can
        # perform replacements to translate the comment
        lines[0] = lines[0].replace("/*", "**").replace("*", "#")
        lines[-1] = lines[-1].replace("*/", "**").replace("*", "#")

        for i in range(1, len(lines) - 1):
            lines[i] = re.sub(r"^\*\*", "##", lines[i])

        return "\n".join(lines)
    else:
        return ""

def translate_file(file_path, final_path, debug, write):
    with open(str(file_path)) as f:
        snippets = get_snippets(f.read().splitlines())
    if snippets:
        # TODO: Get license header first
        license_header = get_license_from_file(str(file_path))
        if debug:
            if have_rich:
                console = Console()
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("C++")
                table.add_column("Python")

        translated_lines = []
        for line in snippets:
            if not line:
                continue
            translated_line = snippet_translate(line)
            translated_lines.append(translated_line)

            # logging
            if debug:
                if have_rich:
                    table.add_row(line, translated_line)
                else:
                    if not opt_quiet:
                        print(line, translated_line)

        if debug and have_rich:
            if not opt_quiet:
                console.print(table)

        if write:
            # Open the final file
            with open(str(final_path), "w") as out_f:
                out_f.write(license_header)
                out_f.write("\n\n")

                for s in translated_lines:
                    out_f.write(s)
                    out_f.write("\n")

            # Rename to .py
            written_file = shutil.move(str(final_path), str(final_path.with_suffix(".py")))
            if not opt_quiet:
                log.info(f"Written: {written_file}")
    else:
        if not opt_quiet:
            log.warning("No snippets were found")



def copy_file(file_path, py_path, category, category_path, write=False, debug=False):

    if not category:
        translate_file(file_path, Path("_translated.py"), debug, write)
        return
    # Get path after the directory "snippets" or "examples"
    # and we add +1 to avoid the same directory
    idx = file_path.parts.index(category) + 1
    rel_path = Path().joinpath(*file_path.parts[idx:])

    final_path = py_path / category_path / rel_path

    # Check if file exists.
    if final_path.exists():
        status_msg = "  [yellow][Exists][/yellow]" if have_rich else "[Exists]"
        status = FileStatus.Exists
    elif final_path.with_suffix(".py").exists():
        status_msg = "[cyan][ExistsPy][/cyan]" if have_rich else "[Exists]"
        status = FileStatus.Exists
    else:
        status_msg = "     [green][New][/green]" if have_rich else "[New]"
        status = FileStatus.New

    if debug:
        if not opt_quiet:
            log.info(f"From {file_path} to")
            log.info(f"==> {final_path}")

    if not opt_quiet:
        if have_rich:
            log.info(f"{status_msg} {final_path}", extra={"markup": True})
        else:
            log.info(f"{status_msg:10s} {final_path}")

    # Directory where the file will be placed, if it does not exists
    # we create it. The option 'parents=True' will create the parents
    # directories if they don't exist, and if some of them exists,
    # the option 'exist_ok=True' will ignore them.
    if write and not final_path.parent.is_dir():
        if not opt_quiet:
            log.info(f"Creating directories for {final_path.parent}")
        final_path.parent.mkdir(parents=True, exist_ok=True)

    # Change .cpp to .py
    # TODO:
    # - What do we do with .h in case both .cpp and .h exists with
    #   the same name?

    # Translate C++ code into Python code
    if final_path.name.endswith(".cpp"):
        translate_file(file_path, final_path, debug, write)

    return status


def process(options):
    qt_path = Path(options.qt_dir)
    py_path = Path(options.pyside_dir)

    # (new, exists)
    valid_new, valid_exists = 0, 0

    # Creating directories in case they don't exist
    if not OUT_SNIPPETS.is_dir():
        OUT_SNIPPETS.mkdir(parents=True)

    if not OUT_EXAMPLES.is_dir():
        OUT_EXAMPLES.mkdir(parents=True)

    if options.single_snippet:
        f = Path(options.single_snippet)
        if is_valid_file(f):
            if "snippets" in f.parts:
                status = copy_file(
                    f,
                    py_path,
                    "snippets",
                    OUT_SNIPPETS,
                    write=options.write_files,
                    debug=options.debug,
                )
            elif "examples" in f.parts:
                status = copy_file(
                    f,
                    py_path,
                    "examples",
                    OUT_EXAMPLES,
                    write=options.write_files,
                    debug=options.debug,
                )
        else:
            log.warning("Path did not contain 'snippets' nor 'examples'."
                        "File will not be copied over, just generated locally.")
            status = copy_file(
                f,
                py_path,
                None,
                None,
                write=options.write_files,
                debug=options.debug,
            )

    else:
        for i in qt_path.iterdir():
            module_name = i.name
            # FIXME: remove this, since it's just for testing.
            if i.name != "qtbase":
                continue

            # Filter only Qt modules
            if not module_name.startswith("qt"):
                continue
            if not opt_quiet:
                log.info(f"Module {module_name}")

            # Iterating everything
            for f in i.glob("**/*.*"):
                if is_valid_file(f):
                    if options.filter_snippet:
                        # Proceed only if the full path contain the filter string
                        if options.filter_snippet not in str(f.absolute()):
                            continue
                    if "snippets" in f.parts:
                        status = copy_file(
                            f,
                            py_path,
                            "snippets",
                            OUT_SNIPPETS,
                            write=options.write_files,
                            debug=options.debug,
                        )
                    elif "examples" in f.parts:
                        status = copy_file(
                            f,
                            py_path,
                            "examples",
                            OUT_EXAMPLES,
                            write=options.write_files,
                            debug=options.debug,
                        )

                    # Stats
                    if status == FileStatus.New:
                        valid_new += 1
                    elif status == FileStatus.Exists:
                        valid_exists += 1

            if not opt_quiet:
                log.info(
                    dedent(
                        f"""\
                    Summary:
                      Total valid files: {valid_new + valid_exists}
                         New files:      {valid_new}
                         Existing files: {valid_exists}
                    """
                    )
                )


if __name__ == "__main__":
    parser = get_parser()
    options = parser.parse_args()
    opt_quiet = False if options.verbose else True
    opt_quiet = False if options.debug else opt_quiet

    if not check_arguments(options):
        parser.print_help()
        sys.exit(0)

    process(options)
