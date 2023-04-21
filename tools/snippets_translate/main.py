# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import logging
import os
import re
import sys
from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter
from enum import Enum
from pathlib import Path
from textwrap import dedent
from typing import Dict, List

from override import python_example_snippet_mapping
from converter import snippet_translate

HELP = """Converts Qt C++ code snippets to Python snippets.

Ways to override Snippets:

1) Complete snippets from local files:
   To replace snippet "[1]" of "foo/bar.cpp", create a file
   "sources/pyside6/doc/snippets/foo/bar_1.cpp.py" .
2) Snippets extracted from Python examples:
   To use snippets from Python examples, add markers ("#! [id]") to it
   and an entry to _PYTHON_EXAMPLE_SNIPPET_MAPPING.
"""


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
CPP_SNIPPET_PATTERN = re.compile(r"//! ?\[([^]]+)\]")
PYTHON_SNIPPET_PATTERN = re.compile(r"#! ?\[([^]]+)\]")

ROOT_PATH = Path(__file__).parents[2]
SOURCE_PATH = ROOT_PATH / "sources" / "pyside6" / "doc" / "snippets"


OVERRIDDEN_SNIPPET = "# OVERRIDDEN_SNIPPET"


class FileStatus(Enum):
    Exists = 0
    New = 1


def get_parser() -> ArgumentParser:
    """
    Returns a parser for the command line arguments of the script.
    See README.md for more information.
    """
    parser = ArgumentParser(prog="snippets_translate",
                            description=HELP,
                            formatter_class=RawDescriptionHelpFormatter)
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
    if not directory.is_dir():
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
    return is_directory(Path(options.qt_dir))


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


def get_snippet_ids(line: str, pattern: re.Pattern) -> List[str]:
    # Extract the snippet ids for a line '//! [1] //! [2]'
    result = []
    for m in pattern.finditer(line):
        result.append(m.group(1))
    return result


def overriden_snippet_lines(lines: List[str], start_id: str) -> List[str]:
    """Wrap an overridden snippet with marker and id lines."""
    id_string = f"//! [{start_id}]"
    result = [OVERRIDDEN_SNIPPET, id_string]
    result.extend(lines)
    result.append(id_string)
    return result


def get_snippet_override(start_id: str, rel_path: str) -> List[str]:
    """Check if the snippet is overridden by a local file under
       sources/pyside6/doc/snippets."""
    file_start_id = start_id.replace(' ', '_')
    override_name = f"{rel_path.stem}_{file_start_id}{rel_path.suffix}.py"
    override_path = SOURCE_PATH / rel_path.parent / override_name
    if not override_path.is_file():
        return []
    lines = override_path.read_text().splitlines()
    return overriden_snippet_lines(lines, start_id)


def _get_snippets(lines: List[str],
                  comment: str,
                  pattern: re.Pattern) -> Dict[str, List[str]]:
    """Helper to extract (potentially overlapping) snippets from a C++ file
       indicated by pattern ("//! [1]") and return them as a dict by <id>."""
    snippets: Dict[str, List[str]] = {}
    snippet: List[str]
    done_snippets : List[str] = []

    i = 0
    while i < len(lines):
        line = lines[i]
        i += 1

        start_ids = get_snippet_ids(line, pattern)
        while start_ids:
            # Start of a snippet
            start_id = start_ids.pop(0)
            if start_id in done_snippets:
                continue

            # Reconstruct a single ID line to avoid repetitive ID lines
            # by consecutive snippets with multi-ID lines like "//! [1] [2]"
            id_line = f"{comment}! [{start_id}]"
            done_snippets.append(start_id)
            snippet = [id_line]  # The snippet starts with this id

            # Find the end of the snippet
            j = i
            while j < len(lines):
                l = lines[j]
                j += 1

                # Add the line to the snippet
                snippet.append(l)

                # Check if the snippet is complete
                if start_id in get_snippet_ids(l, pattern):
                    # End of snippet
                    snippet[len(snippet) - 1] = id_line
                    snippets[start_id] = snippet
                    break

    return snippets


def get_python_example_snippet_override(start_id: str, rel_path: str) -> List[str]:
    """Check if the snippet is overridden by a python example snippet."""
    key = (os.fspath(rel_path), start_id)
    value = python_example_snippet_mapping().get(key)
    if not value:
        return []
    path, id = value
    file_lines = path.read_text().splitlines()
    snippet_dict = _get_snippets(file_lines, '#', PYTHON_SNIPPET_PATTERN)
    lines = snippet_dict.get(id)
    if not lines:
        raise RuntimeError(f'Snippet "{id}" not found in "{os.fspath(path)}"')
    lines = lines[1:-1]  # Strip Python snippet markers
    return overriden_snippet_lines(lines, start_id)


def get_snippets(lines: List[str], rel_path: str) -> List[List[str]]:
    """Extract (potentially overlapping) snippets from a C++ file indicated
       by '//! [1]'."""
    result = _get_snippets(lines, '//', CPP_SNIPPET_PATTERN)
    id_list = result.keys()
    for snippet_id in id_list:
        # Check file overrides and example overrides
        snippet = get_snippet_override(snippet_id, rel_path)
        if not snippet:
            snippet = get_python_example_snippet_override(snippet_id, rel_path)
        if snippet:
            result[snippet_id] = snippet

    return result.values()


def get_license_from_file(lines):
    result = []
    spdx = len(lines) >= 2 and lines[0].startswith("//") and "SPDX" in lines[1]
    if spdx:  # SPDX, 6.4
        for line in lines:
            if line.startswith("//"):
                result.append("# " + line[3:])
            else:
                break
    else:  # Old style, C-Header, 6.2
        for line in lines:
            if line.startswith("/*") or line.startswith("**"):
                result.append(line)
            # End of the comment
            if line.endswith("*/"):
                break
        if result:
            # We know we have the whole block, so we can
            # perform replacements to translate the comment
            result[0] = result[0].replace("/*", "**").replace("*", "#")
            result[-1] = result[-1].replace("*/", "**").replace("*", "#")

            for i in range(1, len(result) - 1):
                result[i] = re.sub(r"^\*\*", "##", result[i])
    return "\n".join(result)


def translate_file(file_path, final_path, qt_path, debug, write):
    lines = []
    snippets = []
    try:
        with file_path.open("r", encoding="utf-8") as f:
            lines = f.read().splitlines()
            rel_path = file_path.relative_to(qt_path)
            snippets = get_snippets(lines, rel_path)
    except Exception as e:
        log.error(f"Error reading {file_path}: {e}")
        raise
    if snippets:
        # TODO: Get license header first
        license_header = get_license_from_file(lines)
        if debug:
            if have_rich:
                console = Console()
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("C++")
                table.add_column("Python")

        translated_lines = []
        for snippet in snippets:
            if snippet and snippet[0] == OVERRIDDEN_SNIPPET:
                translated_lines.extend(snippet[1:])
                continue

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

            with target_file.open("w", encoding="utf-8") as out_f:
                out_f.write("//! [AUTO]\n\n")
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
        translate_file(file_path, final_path, qt_path, debug, write)

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
