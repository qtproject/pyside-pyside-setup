# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

"""
This tool reads all the changelogs in doc/changelogs and generates .rst files for each of the
changelogs. This .rst files are then used to generate the contents of the 'Release Notes' section
in the navigation pane of the Qt for Python documentation.
"""

import re
import logging
import shutil
from pathlib import Path
from argparse import ArgumentParser, RawTextHelpFormatter

SECTION_NAMES = ["PySide6", "Shiboken6", "PySide2", "Shiboken2"]
DIR = Path(__file__).parent
DEFAULT_OUTPUT_DIR = Path(f"{DIR}/../../sources/pyside6/doc/release_notes").resolve()
CHANGELOG_DIR = Path(f"{DIR}/../../doc/changelogs").resolve()

BASE_CONTENT = """\
.. _release_notes:

Release Notes
=============

This section contains the release notes for different versions of Qt for Python.

.. toctree::
    :maxdepth: 1

    pyside6_release_notes.md
    shiboken6_release_notes.md
    pyside2_release_notes.md
    shiboken2_release_notes.md
"""


class Changelog:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.version = file_path.name.split("-")[-1]
        self.sections = {section: [] for section in SECTION_NAMES}
        # for matching lines like *    PySide6    * to identify the section
        self.section_pattern = re.compile(r"\* +(\w+) +\*")
        # for line that start with ' -' which lists the changes
        self.line_pattern = re.compile(r"^ -")
        # for line that contains a bug report like PYSIDE-<bug_number>
        self.bug_number_pattern = re.compile(r"\[PYSIDE-\d+\]")

    def add_line(self, section, line):
        self.sections[section].append(line)

    def parsed_sections(self):
        return self.sections

    def parse(self):
        current_section = None
        buffer = []

        with open(self.file_path, 'r', encoding='utf-8') as file:
            # convert the lines to an iterator for skip the '***' lines
            lines = iter(file.readlines())

        for line in lines:
            # skip lines with all characters as '*'
            if line.strip() == '*' * len(line.strip()):
                continue

            match = self.section_pattern.match(line)
            if match:
                # if buffer has content, add it to the current section
                if buffer:
                    self.add_line(current_section, ' '.join(buffer).strip())
                    buffer = []
                current_section = match.group(1)
                # skip the next line which contains '***'
                try:
                    next(lines)
                except StopIteration:
                    break
                continue

            if current_section:
                if self.line_pattern.match(line) and buffer:
                    self.add_line(current_section, ' '.join(buffer).strip())
                    buffer = []

                # If the line contains a reference to a bug report like [PYSIDE-<bug_number>]
                # then insert a link to the reference that conforms with Sphinx syntax
                bug_number = self.bug_number_pattern.search(line)
                if bug_number:
                    bug_number = bug_number.group()
                    # remove the square brackets
                    actual_bug_number = bug_number[1:-1]
                    bug_number_replacement = (
                        f"[{actual_bug_number}]"
                        f"(https://bugreports.qt.io/browse/{actual_bug_number})"
                    )
                    line = re.sub(re.escape(bug_number), bug_number_replacement, line)

                # Add the line to the buffer
                buffer.append(line.strip())

        # Add any remaining content in the buffer to the current section
        if buffer:
            self.add_line(current_section, ' '.join(buffer).strip())


def parse_changelogs() -> str:
    '''
    Parse the changelogs in the CHANGELOG_DIR and return a list of parsed changelogs.
    '''
    changelogs = []
    logging.info(f"[RELEASE_DOC] Processing changelogs in {CHANGELOG_DIR}")
    for file_path in CHANGELOG_DIR.iterdir():
        # exclude changes-1.2.3
        if "changes-1.2.3" in file_path.name:
            continue
        logging.info(f"[RELEASE_DOC] Processing file {file_path.name}")
        changelog = Changelog(file_path)
        changelog.parse()
        changelogs.append(changelog)
    return changelogs


def write_md_file(section: str, changelogs: list[Changelog], output_dir: Path):
    '''
    For each section create a .md file with the following content:

    Section Name
    ============

    Version
    -------

    - Change 1
    - Change 2
    ....
    '''
    file_path = output_dir / f"{section.lower()}_release_notes.md"
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(f"# {section}\n")
        for changelog in changelogs:
            section_contents = changelog.parsed_sections()[section]
            if section_contents:
                file.write(f"## {changelog.version}\n\n")
                for lines in section_contents:
                    # separate each line with a newline
                    file.write(f"{lines}\n")
                file.write("\n")


def generate_index_file(output_dir: Path):
    """Generate the index RST file."""
    index_path = output_dir / "index.rst"
    index_path.write_text(BASE_CONTENT, encoding='utf-8')


def main():
    parser = ArgumentParser(description="Generate release notes from changelog",
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument("-v", "--verbose", help="run in verbose mode", action="store_const",
                        dest="loglevel", const=logging.INFO)
    parser.add_argument("--target", "-t", help="Directory to output the generated files",
                        type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)

    output_dir = args.target.resolve()

    # create the output directory if it does not exist
    # otherwise remove its contents
    if output_dir.is_dir():
        shutil.rmtree(output_dir, ignore_errors=True)
        logging.info(f"[RELEASE_DOC] Removed existing {output_dir}")

    logging.info(f"[RELEASE_DOC] Creating {output_dir}")
    output_dir.mkdir(exist_ok=True)

    logging.info("[RELEASE_DOC] Generating index.md file")
    generate_index_file(output_dir)

    logging.info("[RELEASE_DOC] Parsing changelogs")
    changelogs = parse_changelogs()

    # sort changelogs by version number in descending order
    changelogs.sort(key=lambda x: x.version, reverse=True)

    for section in SECTION_NAMES:
        logging.info(f"[RELEASE_DOC] Generating {section.lower()}_release_notes.md file")
        write_md_file(section, changelogs, output_dir)


if __name__ == "__main__":
    main()
