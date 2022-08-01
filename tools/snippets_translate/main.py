# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import logging
import os
import re
import sys
from argparse import ArgumentParser, Namespace
from enum import Enum
from pathlib import Path
from textwrap import dedent
from typing import List

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
SNIPPET_PATTERN = re.compile(r"//! ?\[([^]]+)\]")


class FileStatus(Enum):
    Exists = 0
    New = 1


def get_parser() -> ArgumentParser:
    """
    Returns a parser for the command line arguments of the script.
    See README.md for more information.
    """
    parser = ArgumentParser(prog="snippets_translate")
    parser.add_argument(
        "--qt",
        action="store",
        dest="qt_dir",
        required=True,
        help="Path to the Qt directory (QT_SRC_DIR)",
    )

    parser.add_argument(
        "--target",
        action="store",
        dest="target_dir",
        required=True,
        help="Directory into which to generate the snippets",
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
        "-f",
        "--directory",
        action="store",
        dest="single_directory",
        help="Path to a single directory to be translated",
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
                f"Files will be copied from '{options.qt_dir}':\n" f"\tto '{options.target_dir}'"
            )
    else:
        msg = "This is a listing only, files are not being copied"
        if have_rich:
            msg = f"[green]{msg}[/green]"
        if not opt_quiet:
            log.info(msg, extra=extra)

    # Check 'qt_dir'
    return is_directory(options.qt_dir)


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


def get_snippet_ids(line: str) -> List[str]:
    # Extract the snippet ids for a line '//! [1] //! [2]'
    result = []
    for m in SNIPPET_PATTERN.finditer(line):
        result.append(m.group(1))
    return result


def get_snippets(lines: List[str]) -> List[List[str]]:
    # Extract (potentially overlapping) snippets from a C++ file indicated by //! [1]
    snippets: List[List[str]] = []
    snippet: List[str]

    i = 0
    while i < len(lines):
        line = lines[i]
        i += 1

        start_ids = get_snippet_ids(line)
        while start_ids:
            # Start of a snippet
            start_id = start_ids.pop(0)
            snippet = [line]  # The snippet starts with his id

            # Find the end of the snippet
            j = i
            while j < len(lines):
                l = lines[j]
                j += 1

                # Add the line to the snippet
                snippet.append(l)

                # Check if the snippet is complete
                if start_id in get_snippet_ids(l):
                    # End of snippet
                    snippets.append(snippet)
                    break

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
        for snippet in snippets:
            for line in snippet:
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
            new_suffix = ".h.py" if final_path.name.endswith(".h") else ".py"
            target_file = final_path.with_suffix(new_suffix)

            # Directory where the file will be placed, if it does not exists
            # we create it. The option 'parents=True' will create the parents
            # directories if they don't exist, and if some of them exists,
            # the option 'exist_ok=True' will ignore them.
            if not target_file.parent.is_dir():
                if not opt_quiet:
                    log.info(f"Creating directories for {target_file.parent}")
                target_file.parent.mkdir(parents=True, exist_ok=True)

            with target_file.open("w") as out_f:
                out_f.write(license_header)
                out_f.write("\n\n")

                for s in translated_lines:
                    out_f.write(s)
                    out_f.write("\n")

            if not opt_quiet:
                log.info(f"Written: {target_file}")
    else:
        if not opt_quiet:
            log.warning("No snippets were found")


def copy_file(file_path, qt_path, out_path, write=False, debug=False):

    # Replicate the Qt path including module under the PySide snippets directory
    qt_path_count = len(qt_path.parts)
    final_path = out_path.joinpath(*file_path.parts[qt_path_count:])

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

    # Change .cpp to .py, .h to .h.py
    # Translate C++ code into Python code
    if final_path.name.endswith(".cpp") or final_path.name.endswith(".h"):
        translate_file(file_path, final_path, debug, write)

    return status


def single_directory(options, qt_path, out_path):
    # Process all files in the directory
    directory_path = Path(options.single_directory)
    for file_path in directory_path.glob("**/*"):
        if file_path.is_dir() or not is_valid_file(file_path):
            continue
        copy_file(file_path, qt_path, out_path, write=options.write_files, debug=options.debug)


def single_snippet(options, qt_path, out_path):
    # Process a single file
    file = Path(options.single_snippet)
    if is_valid_file(file):
        copy_file(file, qt_path, out_path, write=options.write_files, debug=options.debug)


def all_modules_in_directory(options, qt_path, out_path):
    """
    Process all Qt modules in the directory. Logs how many files were processed.
    """
    # New files, already existing files
    valid_new, valid_exists = 0, 0

    for module in qt_path.iterdir():
        module_name = module.name

        # Filter only Qt modules
        if not module_name.startswith("qt"):
            continue

        if not opt_quiet:
            log.info(f"Module {module_name}")

        # Iterating everything
        for f in module.glob("**/*.*"):
            # Proceed only if the full path contain the filter string
            if not is_valid_file(f):
                continue

            if options.filter_snippet and options.filter_snippet not in str(f.absolute()):
                continue

            status = copy_file(f, qt_path, out_path, write=options.write_files, debug=options.debug)

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


def process_files(options: Namespace) -> None:
    qt_path = Path(options.qt_dir)
    out_path = Path(options.target_dir)

    # Creating directories in case they don't exist
    if not out_path.is_dir():
        out_path.mkdir(parents=True)

    if options.single_directory:
        single_directory(options, qt_path, out_path)
    elif options.single_snippet:
        single_snippet(options, qt_path, out_path)
    else:
        # General case: process all Qt modules in the directory
        all_modules_in_directory(options, qt_path, out_path)


if __name__ == "__main__":
    parser = get_parser()
    opt: Namespace = parser.parse_args()
    opt_quiet = not (opt.verbose or opt.debug)

    if not check_arguments(opt):
        # Error, invalid arguments
        parser.print_help()
        sys.exit(-1)

    process_files(opt)
