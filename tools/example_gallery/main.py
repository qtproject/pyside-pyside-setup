# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only


"""
This tool reads all the examples from the main repository that have a
'.pyproject' file, and generates a special table/gallery in the documentation
page.

For the usage, simply run:
    python tools/example_gallery/main.py
since there is no special requirements.
"""

import json
import math
import os
import shutil
import zipfile
import sys
from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path
from textwrap import dedent

opt_quiet = False


LITERAL_INCLUDE = ".. literalinclude::"


IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".svgz", ".webp")


IGNORED_SUFFIXES = IMAGE_SUFFIXES + (".pdf", ".pyc")


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
    ".xml": "xml",
}


BASE_CONTENT = """\
Examples
========

 A collection of examples are provided with |project| to help new users
 to understand different use cases of the module.

 You can find all these examples inside the
 `pyside-setup <https://code.qt.io/cgit/pyside/pyside-setup.git/>`_ repository
 on the `examples <https://code.qt.io/cgit/pyside/pyside-setup.git/tree/examples>`_
 directory.

"""

def ind(x):
    return " " * 4 * x


def get_lexer(path):
    if path.name == "CMakeLists.txt":
        return "cmake"
    lexer = suffixes.get(path.suffix)
    return lexer if lexer else "text"


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
        ".. grid:: 1 4 4 4\n"
        f"{ind(1)}:gutter: 2\n\n"
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
            gallery += "\n"
        if e["img_doc"]:
            img_name = e['img_doc'].name
        else:
            img_name = "../example_no_image.png"

        # Fix long names
        if name.startswith("chapter"):
            name = name.replace("chapter", "c")
        elif name.startswith("advanced"):
            name = name.replace("advanced", "a")

        desc = e.get("headline")
        if not desc:
            desc = f"found in the ``{underline}`` directory."

        gallery += f"{ind(1)}.. grid-item-card:: {name}\n"
        gallery += f"{ind(2)}:class-item: cover-img\n"
        gallery += f"{ind(2)}:link: {url}\n"
        gallery += f"{ind(2)}:img-top: {img_name}\n\n"
        gallery += f"{ind(2)}{desc}\n"

    return f"{gallery}\n"


def remove_licenses(s):
    new_s = []
    for line in s.splitlines():
        if line.strip().startswith(("/*", "**", "##")):
            continue
        new_s.append(line)
    return "\n".join(new_s)


def make_zip_archive(zip_name, src, skip_dirs=None):
    src_path = Path(src).expanduser().resolve(strict=True)
    if skip_dirs is None:
        skip_dirs = []
    if not isinstance(skip_dirs, list):
        print("Error: A list needs to be passed for 'skip_dirs'")
        return
    with zipfile.ZipFile(src_path.parents[0] / Path(zip_name), 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in src_path.rglob('*'):
            skip = False
            _parts = file.relative_to(src_path).parts
            for sd in skip_dirs:
                if sd in _parts:
                    skip = True
                    break
            if not skip:
                zf.write(file, file.relative_to(src_path.parent))


def doc_file(project_dir, project_file_entry):
    """Return the (optional) .rstinc file describing a source file."""
    rst_file = project_dir
    if rst_file.name != "doc":  # Special case: Dummy .pyproject file in doc dir
        rst_file /= "doc"
    rst_file /= Path(project_file_entry).name + ".rstinc"
    return rst_file if rst_file.is_file() else None


def get_code_tabs(files, project_dir):
    content = "\n"

    # Prepare ZIP file, and copy to final destination
    zip_name = f"{project_dir.name}.zip"
    make_zip_archive(zip_name, project_dir, skip_dirs=["doc"])
    zip_src = f"{project_dir}.zip"
    zip_dst = EXAMPLES_DOC / zip_name
    shutil.move(zip_src, zip_dst)

    content += f":download:`Download this example <{zip_name}>`\n\n"

    for i, project_file in enumerate(files):
        if i == 0:
            content += ".. tab-set::\n\n"

        pfile = Path(project_file)
        if pfile.suffix in IGNORED_SUFFIXES:
            continue

        content += f"{ind(1)}.. tab-item:: {project_file}\n\n"

        doc_rstinc_file = doc_file(project_dir, project_file)
        if doc_rstinc_file:
            indent = ind(2)
            for line in doc_rstinc_file.read_text("utf-8").split("\n"):
                content += indent + line + "\n"
            content += "\n"

        lexer = get_lexer(pfile)
        content += add_indent(f"{ind(1)}.. code-block:: {lexer}", 1)
        content += "\n"

        _path = project_dir / project_file
        _file_content = ""
        try:
            with open(_path, "r", encoding="utf-8") as _f:
                _file_content = remove_licenses(_f.read())
        except UnicodeDecodeError as e:
            print(f"example_gallery: error decoding {project_dir}/{_path}:{e}",
                  file=sys.stderr)
            raise
        except FileNotFoundError as e:
            print(f"example_gallery: error opening {project_dir}/{_path}:{e}",
                  file=sys.stderr)
            raise

        content += add_indent(_file_content, 3)
        content += "\n\n"
    return content


def get_header_title(example_dir):
    _index = example_dir.parts.index("examples")
    rel_path = "/".join(example_dir.parts[_index:])
    _title = rel_path
    url = f"{BASE_URL}/{rel_path}"
    return (
        "..\n    This file was auto-generated by the 'examples_gallery' "
        "script.\n    Any change will be lost!\n\n"
        f"{_title}\n"
        f"{'=' * len(_title)}\n\n"
        f"(You can also check this code `in the repository <{url}>`_)\n\n"
    )


def rel_path(from_path, to_path):
    """Determine relative paths for paths that are not subpaths (where
       relative_to() fails) via a common root."""
    common = Path(*os.path.commonprefix([from_path.parts, to_path.parts]))
    up_dirs = len(from_path.parts) - len(common.parts)
    prefix = up_dirs * "../"
    rel_to_common = os.fspath(to_path.relative_to(common))
    return f"{prefix}{rel_to_common}"


def read_rst_file(project_dir, project_files, doc_rst):
    """Read the example .rst file and expand literal includes to project files
       by relative paths to the example directory. Note: sphinx does not
       handle absolute paths as expected, they need to be relative."""
    content = ""
    with open(doc_rst, encoding="utf-8") as doc_f:
        content = doc_f.read()
    if LITERAL_INCLUDE not in content:
        return content

    result = []
    path_to_example = rel_path(EXAMPLES_DOC, project_dir)
    for line in content.split("\n"):
        if line.startswith(LITERAL_INCLUDE):
            file = line[len(LITERAL_INCLUDE) + 1:].strip()
            if file in project_files:
                line = f"{LITERAL_INCLUDE} {path_to_example}/{file}"
        result.append(line)
    return "\n".join(result)


def get_headline(text):
    """Find the headline in the .rst file."""
    underline = text.find("\n====")
    if underline != -1:
        start = text.rfind("\n", 0, underline - 1)
        return text[start + 1:underline]
    return ""


def write_example(pyproject_file):
    """Read the project file and documentation, create the .rst file and
       copy the data. Return a tuple of module name and a dict of example data."""
    example_dir = pyproject_file.parent
    if example_dir.name == "doc":  # Dummy pyproject in doc dir (scriptableapplication)
        example_dir = example_dir.parent

    parts = example_dir.parts[len(EXAMPLES_DIR.parts):]

    module_name = parts[0]
    example_name = parts[-1]
    # handling subdirectories besides the module level and the example
    extra_names = "" if len(parts) == 2 else "_".join(parts[1:-1])

    rst_file = f"example_{module_name}_{extra_names}_{example_name}.rst".replace("__", "_")

    def check_img_ext(i):
        return i.suffix in IMAGE_SUFFIXES

    # Check for a 'doc' directory inside the example
    has_doc = False
    img_doc = None
    original_doc_dir = Path(example_dir / "doc")
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

    result = {"example": example_name,
              "module": module_name,
              "extra": extra_names,
              "rst": rst_file,
              "abs_path": str(example_dir),
              "has_doc": has_doc,
              "img_doc": img_doc}

    files = []
    try:
        with pyproject_file.open("r", encoding="utf-8") as pyf:
            pyproject = json.load(pyf)
            # iterate through the list of files in .pyproject and
            # check if they exist, before appending to the list.
            for f in pyproject["files"]:
                if not Path(f).exists:
                    print(f"example_gallery: {f} listed in {pyproject_file} does not exist")
                    raise FileNotFoundError
                else:
                    files.append(f)
    except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
        print(f"example_gallery: error reading {pyproject_file}: {e}")
        raise

    headline = ""
    if files:
        rst_file_full = EXAMPLES_DOC / rst_file

        with open(rst_file_full, "w", encoding="utf-8") as out_f:
            if has_doc:
                doc_rst = original_doc_dir / f"{example_name}.rst"
                content_f = read_rst_file(example_dir, files, doc_rst)
                headline = get_headline(content_f)
                if not headline:
                    print(f"example_gallery: No headline found in {doc_rst}",
                          file=sys.stderr)

                # Copy other files in the 'doc' directory, but
                # excluding the main '.rst' file and all the
                # directories.
                for _f in original_doc_dir.glob("*"):
                    if _f == doc_rst or _f.is_dir():
                        continue
                    src = _f
                    dst = EXAMPLES_DOC / _f.name

                    resource_written = shutil.copy(src, dst)
                    if not opt_quiet:
                        print("Written resource:", resource_written)
            else:
                content_f = get_header_title(example_dir)
            content_f += get_code_tabs(files, pyproject_file.parent)
            out_f.write(content_f)

        if not opt_quiet:
            print(f"Written: {EXAMPLES_DOC}/{rst_file}")
    else:
        if not opt_quiet:
            print("Empty '.pyproject' file, skipping")

    result["headline"] = headline

    return (module_name, result)


def sort_examples(example):
    result = {}
    for module in example.keys():
        result[module] = sorted(example.get(module), key=lambda e: e.get("rst"))
    return result


if __name__ == "__main__":
    # Only examples with a '.pyproject' file will be listed.
    DIR = Path(__file__).parent
    EXAMPLES_DOC = Path(f"{DIR}/../../sources/pyside6/doc/examples").resolve()
    EXAMPLES_DIR = Path(f"{DIR}/../../examples/").resolve()
    BASE_URL = "https://code.qt.io/cgit/pyside/pyside-setup.git/tree"
    columns = 5
    gallery = ""

    parser = ArgumentParser(description=__doc__, formatter_class=RawTextHelpFormatter)
    TARGET_HELP = f"Directory into which to generate RST files (default: {str(EXAMPLES_DOC)})"
    parser.add_argument("--target", "-t", action="store", dest="target_dir", help=TARGET_HELP)
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet")
    options = parser.parse_args()
    opt_quiet = options.quiet
    if options.target_dir:
        EXAMPLES_DOC = Path(options.target_dir).resolve()

    # This main loop will be in charge of:
    #   * Getting all the .pyproject files,
    #   * Gather the information of the examples and store them in 'examples'
    #   * Read the .pyproject file to output the content of each file
    #     on the final .rst file for that specific example.
    examples = {}

    # Create the 'examples' directory if it doesn't exist
    # If it does exist, remove it and create a new one to start fresh
    if EXAMPLES_DOC.is_dir():
        shutil.rmtree(EXAMPLES_DOC, ignore_errors=True)
        if not opt_quiet:
            print("WARNING: Deleted old html directory")
    EXAMPLES_DOC.mkdir()

    for pyproject_file in EXAMPLES_DIR.glob("**/*.pyproject"):
        if pyproject_file.name != "examples.pyproject":
            module_name, data = write_example(pyproject_file)
            if module_name not in examples:
                examples[module_name] = []
            examples[module_name].append(data)

    examples = sort_examples(examples)

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
        f.write(BASE_CONTENT)
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
