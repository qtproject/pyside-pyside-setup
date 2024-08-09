# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

# broken_links.py
# This script is used to find the broken links in the generated sphinx documentation.

# Pre-requisites before running this script:
#
# 1. Generate the HTML documentation as given in
#    https://doc.qt.io/qtforpython-6/gettingstarted/index.html#building-the-documentation
#    . This will generate a folder inside 'pyside-setup' called 'html'.
# 2. Run sphinx-build with linkcheck builder to generate an output.json file inside 'html' folder.
#    The command to run is:
#    sphinx-build -b linkcheck -j auto -n -c ./html/pyside6/base <folder_of_rst> ./html
#
# The final output will be <output_folder>/broken_links.json

import json
import argparse
from pathlib import Path


def find_broken_links(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    broken_links = []
    for line in lines:
        entry = json.loads(line)
        if entry.get("status") == "broken":
            broken_links.append(entry)

    return broken_links


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find broken links in a JSON file.")
    parser.add_argument('--input-file', type=str, required=True, help='Path to the input JSON file')
    parser.add_argument('--output-folder', type=str, default=Path(__file__).resolve().parents[2],
                        help='Path to the output folder')
    args = parser.parse_args()

    broken_links = find_broken_links(args.input_file)

    output_file_path = Path(args.output_folder) / 'broken_links.json'

    if broken_links:
        with open(output_file_path, 'w') as outfile:
            json.dump(broken_links, outfile, indent=4)
        print(f"Broken links written to {output_file_path}")
    else:
        print("No broken links found.")
