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


"""
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
import shutil
from pathlib import Path
from textwrap import dedent


opt_quiet = False
suffixes = {
    ".h": "cpp",
    ".cpp": "cpp",
    ".md": "markdown",
    ".py": "py",
    ".qml": "js",
    ".conf": "ini",
    ".qrc": "xml",
    ".ui": "xml",
    ".xbel": "xml",
}


def ind(x):
    return " " * 4 * x


def get_lexer(path):
    if path.name == "CMakeLists.txt":
        return "cmake"
    suffix = path.suffix
    if suffix in suffixes:
        return suffixes[suffix]
    return "text"


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

    gallery = (
        ".. panels::\n"
        f"{ind(1)}:container: container-lg pb-3\n"
        f"{ind(1)}:column: col-lg-3 col-md-6 col-sm-6 col-xs-12 p-2\n\n"
    )

    # Iteration per rows
    for i in range(math.ceil(len(examples))):
        e = examples[i]
        url = e["rst"].replace(".rst", ".html")
        name = e["example"]
        underline = f'{e["module"]}'


        if e["extra"]:
            underline += f'/{e["extra"]}'

        if i > 0:
            gallery += f"{ind(1)}---\n"
        elif e["img_doc"]:
            gallery += f"{ind(1)}---\n"

        if e["img_doc"]:
            img_name = e['img_doc'].name
        else:
            img_name = "../example_no_image.png"

        gallery += f"{ind(1)}:img-top: {img_name}\n"
        gallery += f"{ind(1)}:img-top-cls: + d-flex align-self-center\n\n"

        # Fix long names
        if name.startswith("chapter"):
            name = name.replace("chapter", "c")

        gallery += f"{ind(1)}`{name} <{url}>`_\n"
        gallery += f"{ind(1)}+++\n"
        gallery += f"{ind(1)}{underline}\n"
        gallery += f"\n{ind(1)}.. link-button:: {url}\n"
        gallery += f"{ind(2)}:type: url\n"
        gallery += f"{ind(2)}:text: Go to Example\n"
        gallery += f"{ind(2)}:classes: btn-qt btn-block stretched-link\n"

    return f"{gallery}\n"


def remove_licenses(s):
    new_s = []
    for line in s.splitlines():
        if line.strip().startswith(("/*", "**", "##")):
            continue
        new_s.append(line)
    return "\n".join(new_s)


def get_code_tabs(files, project_file):
    content = "\n"

    for i, project_file in enumerate(files):
        pfile = Path(project_file)
        if pfile.suffix in (".jpg", ".png", ".pyc"):
            continue

        content += f".. tabbed:: {project_file}\n\n"

        lexer = get_lexer(pfile)
        content += add_indent(f".. code-block:: {lexer}", 1)
        content += "\n"

        _path = f_path.resolve().parents[0] / project_file
        _file_content = ""
        try:
            with open(_path, "r") as _f:
                _file_content = remove_licenses(_f.read())
        except UnicodeDecodeError as e:
            print(f"example_gallery: error decoding {_path}:{e}")
            raise

        content += add_indent(_file_content, 2)
        content += "\n\n"
    return content


def get_header_title(f_path):
    _title = f_path.stem
    url_name = "/".join(f_path.parts[f_path.parts.index("examples")+1:-1])
    url = f"{BASE_URL}/{url_name}"
    return (
        "..\n    This file was auto-generated by the 'examples_gallery' "
        "script.\n    Any change will be lost!\n\n"
        f"{_title}\n"
        f"{'=' * len(_title)}\n\n"
        f"(You can also check this code `in the repository <{url}>`_)\n\n"
    )


if __name__ == "__main__":
    # Only examples with a '.pyproject' file will be listed.
    DIR = Path(__file__).parent
    EXAMPLES_DOC = Path(f"{DIR}/../../sources/pyside6/doc/examples")
    EXAMPLES_DIR = Path(f"{DIR}/../../examples/")
    BASE_URL = "https://code.qt.io/cgit/pyside/pyside-setup.git/tree/examples"
    columns = 5
    gallery = ""

    parser = ArgumentParser(description=__doc__, formatter_class=RawTextHelpFormatter)
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet")
    options = parser.parse_args()
    opt_quiet = options.quiet

    # This main loop will be in charge of:
    #   * Getting all the .pyproject files,
    #   * Gather the information of the examples and store them in 'examples'
    #   * Read the .pyproject file to output the content of each file
    #     on the final .rst file for that specific example.
    examples = {}

    # Create the 'examples' directory if it doesn't exist
    if not EXAMPLES_DOC.is_dir():
        EXAMPLES_DOC.mkdir()

    for f_path in EXAMPLES_DIR.glob("**/*.pyproject"):
        if str(f_path).endswith("examples.pyproject"):
            continue

        parts = f_path.parts[len(EXAMPLES_DIR.parts):-1]

        module_name = parts[0]
        example_name = parts[-1]
        # handling subdirectories besides the module level and the example
        extra_names = "" if len(parts) == 2 else "_".join(parts[1:-1])

        rst_file = f"example_{module_name}_{extra_names}_{example_name}.rst"

        def check_img_ext(i):
            EXT = (".png", ".jpg", ".jpeg", ".gif")
            if i.suffix in EXT:
                return True
            return False

        # Check for a 'doc' directory inside the example
        has_doc = False
        img_doc = None
        original_doc_dir = Path(f_path.parent / "doc")
        if original_doc_dir.is_dir():
            has_doc = True
            images = [i for i in original_doc_dir.glob("*") if i.is_file() and check_img_ext(i)]
            if len(images) > 0:
                # We look for an image with the same example_name first, if not, we select the first
                image_path = [i for i in images if example_name in str(i)]
                if not image_path:
                    image_path = images[0]
                else:
                    img_doc = image_path[0]

        if module_name not in examples:
            examples[module_name] = []

        examples[module_name].append(
            {
                "example": example_name,
                "module": module_name,
                "extra": extra_names,
                "rst": rst_file,
                "abs_path": str(f_path),
                "has_doc": has_doc,
                "img_doc": img_doc,
            }
        )

        files = []
        try:
            with open(str(f_path), "r") as pyf:
                pyproject = json.load(pyf)
                files = pyproject["files"]
        except (json.JSONDecodeError, KeyError) as e:
            print(f"example_gallery: error reading {f_path}: {e}")
            raise

        if files:
            rst_file_full = EXAMPLES_DOC / rst_file

            with open(rst_file_full, "w") as out_f:
                if has_doc:
                    doc_path = Path(f_path.parent) / "doc"
                    doc_rst = doc_path / f"{example_name}.rst"

                    with open(doc_rst) as doc_f:
                        content_f = doc_f.read()

                    # Copy other files in the 'doc' directory, but
                    # excluding the main '.rst' file and all the
                    # directories.
                    for _f in doc_path.glob("*"):
                        if _f == doc_rst or _f.is_dir():
                            continue
                        src = _f
                        dst = EXAMPLES_DOC / _f.name

                        resource_written = shutil.copy(src, dst)
                        if not opt_quiet:
                            print("Written resource:", resource_written)
                else:
                    content_f = get_header_title(f_path)
                content_f += get_code_tabs(files, out_f)
                out_f.write(content_f)

            if not opt_quiet:
                print(f"Written: {EXAMPLES_DOC}/{rst_file}")
        else:
            if not opt_quiet:
                print("Empty '.pyproject' file, skipping")

    base_content = dedent(
        """\
    ..
        This file was auto-generated from the 'pyside-setup/tools/example_gallery'
        All editions in this file will be lost.

    |project| Examples
    ===================

    A collection of examples are provided with |project| to help new users
    to understand different use cases of the module.

    You can find all these examples inside the ``pyside-setup`` on the ``examples``
    directory, or you can access them after installing |pymodname| from ``pip``
    inside the ``site-packages/PySide6/examples`` directory.

       """
    )

    # We generate a 'toctree' at the end of the file, to include the new
    # 'example' rst files, so we get no warnings, and also that users looking
    # for them will be able to, since they are indexed.
    # Notice that :hidden: will not add the list of files by the end of the
    # main examples HTML page.
    footer_index = dedent(
        """\
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
            f.write(f"{module_name.title()}\n")
            f.write(f"{'*' * len(module_name.title())}\n")
            f.write(get_module_gallery(e))
        f.write("\n\n")
        f.write(footer_index)
        for i in index_files:
            f.write(f"   {i}\n")

    if not opt_quiet:
        print(f"Written index: {EXAMPLES_DOC}/index.rst")
