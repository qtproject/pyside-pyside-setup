# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import logging
import os
import sys
from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path

sys.path.append(os.fspath(Path(__file__).parent / "snippets_translate"))

from converter import snippet_translate

DESCRIPTION = "Tool to convert C++ to Python based on snippets_translate"


def create_arg_parser(desc):
    parser = ArgumentParser(description=desc,
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument("--stdout", "-s", action="store_true",
                        help="Write to stdout")
    parser.add_argument("--force", "-f", action="store_true",
                        help="Force overwrite of existing files")
    parser.add_argument("files", type=str, nargs="+",
                        help="C++ source file(s)")
    return parser


if __name__ == "__main__":
    arg_parser = create_arg_parser(DESCRIPTION)
    args = arg_parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    for input_file_str in args.files:
        input_file = Path(input_file_str)
        if not input_file.is_file():
            logger.error(f"{input_file_str} does not exist or is not a file.")
            sys.exit(-1)

        if input_file.suffix != ".cpp" and input_file.suffix != ".h":
            logger.error(f"{input_file} does not appear to be a C++ file.")
            sys.exit(-1)

        translated_lines = [f"# Converted from {input_file.name}\n"]
        for line in input_file.read_text().split("\n"):
            translated_lines.append(snippet_translate(line))
        translated = "\n".join(translated_lines)

        if args.stdout:
            sys.stdout.write(translated)
        else:
            target_file = input_file.parent / (input_file.stem + ".py")
            if target_file.exists():
                if not target_file.is_file():
                    logger.error(f"{target_file} exists and is not a file.")
                    sys.exit(-1)
                if not args.force:
                    logger.error(f"{target_file} exists. Use -f to overwrite.")
                    sys.exit(-1)

            target_file.write_text(translated)
            logger.info(f"Wrote {target_file}.")
