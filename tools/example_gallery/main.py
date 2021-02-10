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
###############


DESCRIPTION = """
This tool reads all the examples from the main repository that have a
'.pyproject' file, and generates a special table/gallery in the documentation
page.

For the usage, simply run:
    python tools/example_gallery/main.py
since there is no special requirements.
"""

from argparse import ArgumentParser, RawTextHelpFormatter
import json
import math
from pathlib import Path
from textwrap import dedent


opt_quiet = False


def ind(x):
    return " " * 4 * x


def get_colgroup(columns, indent=2):
    width = 80  # percentage
    width_column = width // columns
    return f'{ind(indent)}<col style="width: {width_column}%" />\n' * columns


def add_indent(s, level):
    new_s = ""
    for line in s.splitlines():
        if line.strip():
            new_s += f"{ind(level)}{line}\n"
        else:
            new_s += "\n"
    return new_s


def get_module_gallery(examples):
    """
    This function takes a list of dictionaries, that contain examples
    information, from one specific module.
    """

    gallery = dedent(f"""\
    <table class="special">
        <colgroup>
{get_colgroup(columns, indent=3)}
        </colgroup>
    """
    )

    # Iteration per rows
    for i in range(math.ceil(len(examples) / columns)):
        gallery += f"{ind(1)}<tr>\n"
        # Iteration per columns
        for j in range(columns):
            # We use a 'try-except' to handle when the examples are
            # not an exact 'rows x columns', meaning that some cells
            # will be empty.
            try:
                e = examples[i * columns + j]
                url = e["rst"].replace(".rst", ".html")
                name = e["example"]
                underline = f'{e["module"]}'
                if e["extra"]:
                    underline += f'/{e["extra"]}'
                gallery += (
                    f'{ind(2)}<td><a href="{url}"><p><strong>{name}</strong><br/>'
                    f"({underline})</p></a></td>\n"
                )
            except IndexError:
                # We use display:none to hide the cell
                gallery += f'{ind(2)}<td style="display: none;"></td>\n'
        gallery += f"{ind(1)}</tr>\n"

    gallery += dedent("""\
    </table>
    """
    )
    return gallery


def remove_licenses(s):
    new_s = []
    for line in s.splitlines():
        if line.strip().startswith(("/*", "**", "##")):
            continue
        new_s.append(line)
    return "\n".join(new_s)


if __name__ == "__main__":
    # Only examples with a '.pyproject' file will be listed.
    DIR = Path(__file__).parent
    EXAMPLES_DOC = f"{DIR}/../../sources/pyside6/doc/examples"
    EXAMPLES_DIR = Path(f"{DIR}/../../examples/")
    columns = 5
    gallery = ""

    parser = ArgumentParser(description=DESCRIPTION,
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Quiet')
    options = parser.parse_args()
    opt_quiet = options.quiet

    # This main loop will be in charge of:
    #   * Getting all the .pyproject files,
    #   * Gather the information of the examples and store them in 'examples'
    #   * Read the .pyproject file to output the content of each file
    #     on the final .rst file for that specific example.
    examples = {}
    for f_path in EXAMPLES_DIR.glob("**/*.pyproject"):
        if str(f_path).endswith("examples.pyproject"):
            continue

        parts = f_path.parts[len(EXAMPLES_DIR.parts) : -1]

        module_name = parts[0]
        example_name = parts[-1]
        # handling subdirectories besides the module level and the example
        extra_names = "" if len(parts) == 2 else "_".join(parts[1:-1])

        rst_file = f"example_{module_name}_{extra_names}_{example_name}.rst"

        if module_name not in examples:
            examples[module_name] = []

        examples[module_name].append(
            {
                "example": example_name,
                "module": module_name,
                "extra": extra_names,
                "rst": rst_file,
                "abs_path": str(f_path),
            }
        )

        pyproject = ""
        with open(str(f_path), "r") as pyf:
            pyproject = json.load(pyf)

        if pyproject:
            with open(f"{EXAMPLES_DOC}/{rst_file}", "w") as out_f:
                content_f = (
                    "..\n    This file was auto-generated by the 'examples_gallery' "
                    "script.\n    Any change will be lost!\n\n"
                )
                for project_file in pyproject["files"]:
                    if project_file.split(".")[-1] in ("png", "pyc"):
                        continue
                    length = len(project_file)
                    content_f += f"{project_file}\n{'=' * length}\n\n::\n\n"

                    _path = f_path.resolve().parents[0] / project_file
                    _content = ""
                    with open(_path, "r") as _f:
                        _content = remove_licenses(_f.read())

                    content_f += add_indent(_content, 1)
                    content_f += "\n\n"
                out_f.write(content_f)
            if not opt_quiet:
                print(f"Written: {EXAMPLES_DOC}/{rst_file}")
        else:
            if not opt_quiet:
                print("Empty '.pyproject' file, skipping")

    base_content = dedent("""\
    ..
        This file was auto-generated from the 'pyside-setup/tools/example_gallery'
        All editions in this file will be lost.

    |project| Examples
    ===================

    A collection of examples are provided with |project| to help new users
    to understand different use cases of the module.

    .. toctree::
       :maxdepth: 1

       tabbedbrowser.rst
       ../pyside-examples/all-pyside-examples.rst

    Gallery
    -------

    You can find all these examples inside the ``pyside-setup`` on the ``examples``
    directory, or you can access them after installing |pymodname| from ``pip``
    inside the ``site-packages/PySide6/examples`` directory.

    .. raw:: html

       """
    )

    # We generate a 'toctree' at the end of the file, to include the new
    # 'example' rst files, so we get no warnings, and also that users looking
    # for them will be able to, since they are indexed.
    # Notice that :hidden: will not add the list of files by the end of the
    # main examples HTML page.
    footer_index = dedent("""\
      .. toctree::
         :hidden:
         :maxdepth: 1

        """
    )

    # Writing the main example rst file.
    index_files = []
    with open(f"{EXAMPLES_DOC}/index.rst", "w") as f:
        f.write(base_content)
        for module_name, e in sorted(examples.items()):
            for i in e:
                index_files.append(i["rst"])
            f.write(f"{ind(1)}<h3>{module_name.title()}</h3>\n")
            f.write(add_indent(get_module_gallery(e), 1))
        f.write("\n\n")
        f.write(footer_index)
        for i in index_files:
            f.write(f"   {i}\n")

    if not opt_quiet:
        print(f"Written index: {EXAMPLES_DOC}/index.rst")
