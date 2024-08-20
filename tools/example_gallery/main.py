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
from dataclasses import dataclass
from enum import IntEnum, Enum
from pathlib import Path
from textwrap import dedent


class Format(Enum):
    RST = 0
    MD = 1


class ModuleType(IntEnum):
    ESSENTIALS = 0
    ADDONS = 1
    M2M = 2


SUFFIXES = {Format.RST: "rst", Format.MD: "md"}


opt_quiet = False


LITERAL_INCLUDE = ".. literalinclude::"


IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".svgz", ".webp")


IGNORED_SUFFIXES = IMAGE_SUFFIXES + (".pdf", ".pyc", ".obj", ".mesh")


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


def check_img_ext(i):
    """Check whether path is an image."""
    return i.suffix in IMAGE_SUFFIXES


@dataclass
class ModuleDescription:
    """Specifies a sort key and type for a Qt module."""
    sort_key: int = 0
    module_type: ModuleType = ModuleType.ESSENTIALS
    description: str = ''


MODULE_DESCRIPTIONS = {
    "async": ModuleDescription(16, ModuleType.ESSENTIALS, ''),
    "corelib": ModuleDescription(15, ModuleType.ESSENTIALS, ''),
    "dbus": ModuleDescription(22, ModuleType.ESSENTIALS, ''),
    "designer": ModuleDescription(11, ModuleType.ESSENTIALS, ''),
    "gui": ModuleDescription(25, ModuleType.ESSENTIALS, ''),
    "network": ModuleDescription(20, ModuleType.ESSENTIALS, ''),
    "opengl": ModuleDescription(26, ModuleType.ESSENTIALS, ''),
    "qml": ModuleDescription(0, ModuleType.ESSENTIALS, ''),
    "quick": ModuleDescription(1, ModuleType.ESSENTIALS, ''),
    "quickcontrols": ModuleDescription(2, ModuleType.ESSENTIALS, ''),
    "samplebinding": ModuleDescription(30, ModuleType.ESSENTIALS, ''),
    "scriptableapplication": ModuleDescription(30, ModuleType.ESSENTIALS, ''),
    "sql": ModuleDescription(21, ModuleType.ESSENTIALS, ''),
    "uitools": ModuleDescription(12, ModuleType.ESSENTIALS, ''),
    "widgetbinding": ModuleDescription(30, ModuleType.ESSENTIALS, ''),
    "widgets": ModuleDescription(10, ModuleType.ESSENTIALS, ''),
    "xml": ModuleDescription(24, ModuleType.ESSENTIALS, ''),
    "Qt Demos": ModuleDescription(0, ModuleType.ADDONS, ''),  # from Qt repos
    "3d": ModuleDescription(30, ModuleType.ADDONS, ''),
    "axcontainer": ModuleDescription(20, ModuleType.ADDONS, ''),
    "bluetooth": ModuleDescription(20, ModuleType.ADDONS, ''),
    "charts": ModuleDescription(12, ModuleType.ADDONS, ''),
    "datavisualization": ModuleDescription(11, ModuleType.ADDONS, ''),
    "demos": ModuleDescription(0, ModuleType.ADDONS, ''),
    "external": ModuleDescription(20, ModuleType.ADDONS, ''),
    "graphs": ModuleDescription(10, ModuleType.ADDONS, ''),
    "httpserver": ModuleDescription(0, ModuleType.ADDONS, ''),
    "location": ModuleDescription(20, ModuleType.ADDONS, ''),
    "multimedia": ModuleDescription(12, ModuleType.ADDONS, ''),
    "networkauth": ModuleDescription(20, ModuleType.ADDONS, ''),
    "pdf": ModuleDescription(20, ModuleType.ADDONS, ''),
    "pdfwidgets": ModuleDescription(20, ModuleType.ADDONS, ''),
    "quick3d": ModuleDescription(20, ModuleType.ADDONS, ''),
    "remoteobjects": ModuleDescription(20, ModuleType.ADDONS, ''),
    "serialbus": ModuleDescription(30, ModuleType.ADDONS, ''),
    "serialport": ModuleDescription(30, ModuleType.ADDONS, ''),
    "spatialaudio": ModuleDescription(20, ModuleType.ADDONS, ''),
    "speech": ModuleDescription(20, ModuleType.ADDONS, ''),
    "statemachine": ModuleDescription(30, ModuleType.ADDONS, ''),
    "webchannel": ModuleDescription(30, ModuleType.ADDONS, ''),
    "webenginequick": ModuleDescription(15, ModuleType.ADDONS, ''),
    "webenginewidgets": ModuleDescription(16, ModuleType.ADDONS, ''),
    "coap": ModuleDescription(0, ModuleType.M2M, ''),
    "mqtt": ModuleDescription(0, ModuleType.M2M, ''),
    "opcua": ModuleDescription(0, ModuleType.M2M, '')
}


def module_sort_key(name):
    """Return key for sorting modules."""
    description = MODULE_DESCRIPTIONS.get(name)
    module_type = int(description.module_type) if description else 5
    sort_key = description.sort_key if description else 100
    return f"{module_type}:{sort_key:04}:{name}"


def module_title(name):
    """Return title for a module."""
    result = name.title()
    description = MODULE_DESCRIPTIONS.get(name)
    if description:
        if description.description:
            result += " - " + description.description
        if description.module_type == ModuleType.M2M:
            result += " (M2M)"
        elif description.module_type == ModuleType.ADDONS:
            result += " (Add-ons)"
        else:
            result += " (Essentials)"
    return result


@dataclass
class ExampleData:
    """Example data for formatting the gallery."""

    def __init__(self):
        self.headline = ""

    example: str
    module: str
    extra: str
    doc_file: str
    file_format: Format
    abs_path: str
    has_doc: bool
    img_doc: Path
    headline: str


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
        suffix = SUFFIXES[e.file_format]
        url = e.doc_file.replace(f".{suffix}", ".html")
        name = e.example
        underline = e.module

        if e.extra:
            underline += f"/{e.extra}"

        if i > 0:
            gallery += "\n"
        img_name = e.img_doc.name if e.img_doc else "../example_no_image.png"

        # Fix long names
        if name.startswith("chapter"):
            name = name.replace("chapter", "c")
        elif name.startswith("advanced"):
            name = name.replace("advanced", "a")

        desc = e.headline
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


def make_zip_archive(zip_file, src, skip_dirs=None):
    src_path = Path(src).expanduser().resolve(strict=True)
    if skip_dirs is None:
        skip_dirs = []
    if not isinstance(skip_dirs, list):
        print("Error: A list needs to be passed for 'skip_dirs'")
        return
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zf:
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


def get_code_tabs(files, project_dir, file_format):
    content = "\n"

    # Prepare ZIP file, and copy to final destination
    # Handle examples which only have a dummy pyproject file in the "doc" dir
    zip_root = project_dir.parent if project_dir.name == "doc" else project_dir
    zip_name = f"{zip_root.name}.zip"
    make_zip_archive(EXAMPLES_DOC / zip_name, zip_root, skip_dirs=["doc"])

    if file_format == Format.RST:
        content += f":download:`Download this example <{zip_name}>`\n\n"
    else:
        content += f"{{download}}`Download this example <{zip_name}>`\n\n"
        content += "```{eval-rst}\n"

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

    if file_format == Format.MD:
        content += "```"

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


def get_headline(text, file_format):
    """Find the headline in the .rst file."""
    if file_format == Format.RST:
        underline = text.find("\n====")
        if underline != -1:
            start = text.rfind("\n", 0, underline - 1)
            return text[start + 1:underline]
    elif file_format == Format.MD:
        headline = text.find("# ")
        if headline != -1:
            new_line = text.find("\n", headline + 1)
            if new_line != -1:
                return text[headline + 2:new_line].strip()
    return ""


def get_doc_source_file(original_doc_dir, example_name):
    """Find the doc source file, return (Path, Format)."""
    if original_doc_dir.is_dir():
        for file_format in (Format.RST, Format.MD):
            suffix = SUFFIXES[file_format]
            result = original_doc_dir / f"{example_name}.{suffix}"
            if result.is_file():
                return result, file_format
    return None, Format.RST


def get_screenshot(image_dir, example_name):
    """Find screen shot: We look for an image with the same
       example_name first, if not, we select the first."""
    if not image_dir.is_dir():
        return None
    images = [i for i in image_dir.glob("*") if i.is_file() and check_img_ext(i)]
    example_images = [i for i in images if i.name.startswith(example_name)]
    if example_images:
        return example_images[0]
    if images:
        return images[0]
    return None


def write_resources(src_list, dst):
    """Write a list of example resource paths to the dst path."""
    for src in src_list:
        resource_written = shutil.copy(src, dst / src.name)
        if not opt_quiet:
            print("Written resource:", resource_written)


@dataclass
class ExampleParameters:
    """Parameters obtained from scanning the examples directory."""

    def __init__(self):
        self.file_format = Format.RST
        self.src_doc_dir = self.src_doc_file_path = self.src_screenshot = None
        self.extra_names = ""

    example_dir: Path
    module_name: str
    example_name: str
    extra_names: str
    file_format: Format
    target_doc_file: str
    src_doc_dir: Path
    src_doc_file_path: Path
    src_screenshot: Path


def detect_pyside_example(example_root, pyproject_file):
    """Detemine parameters of a PySide example."""
    p = ExampleParameters()

    p.example_dir = pyproject_file.parent
    if p.example_dir.name == "doc":  # Dummy pyproject in doc dir (scriptableapplication)
        p.example_dir = p.example_dir.parent

    parts = p.example_dir.parts[len(example_root.parts):]
    p.module_name = parts[0]
    p.example_name = parts[-1]
    # handling subdirectories besides the module level and the example
    p.extra_names = "" if len(parts) == 2 else "_".join(parts[1:-1])

    # Check for a 'doc' directory inside the example
    src_doc_dir = p.example_dir / "doc"

    if src_doc_dir.is_dir():
        src_doc_file_path, fmt = get_doc_source_file(src_doc_dir, p.example_name)
        if src_doc_file_path:
            p.src_doc_file_path = src_doc_file_path
            p.file_format = fmt
            p.src_doc_dir = src_doc_dir
            p.src_screenshot = get_screenshot(src_doc_dir, p.example_name)

    target_suffix = SUFFIXES[p.file_format]
    doc_file = f"example_{p.module_name}_{p.extra_names}_{p.example_name}.{target_suffix}"
    p.target_doc_file = doc_file.replace("__", "_")
    return p


def detect_qt_example(example_root, pyproject_file):
    """Detemine parameters of an example from a Qt repository."""
    p = ExampleParameters()

    p.example_dir = pyproject_file.parent
    p.module_name = "Qt Demos"
    p.example_name = p.example_dir.name
    # Check for a 'doc' directory inside the example (qdoc)
    doc_root = p.example_dir / "doc"
    if doc_root.is_dir():
        src_doc_file_path, fmt = get_doc_source_file(doc_root / "src", p.example_name)
        if src_doc_file_path:
            p.src_doc_file_path = src_doc_file_path
            p.file_format = fmt
            p.src_doc_dir = doc_root
            p.src_screenshot = get_screenshot(doc_root / "images", p.example_name)

    target_suffix = SUFFIXES[p.file_format]
    p.target_doc_file = f"example_qtdemos_{p.example_name}.{target_suffix}"
    return p


def write_example(example_root, pyproject_file, pyside_example=True):
    """Read the project file and documentation, create the .rst file and
       copy the data. Return a tuple of module name and a dict of example data."""
    p = (detect_pyside_example(example_root, pyproject_file) if pyside_example
         else detect_qt_example(example_root, pyproject_file))

    result = ExampleData()
    result.example = p.example_name
    result.module = p.module_name
    result.extra = p.extra_names
    result.doc_file = p.target_doc_file
    result.file_format = p.file_format
    result.abs_path = str(p.example_dir)
    result.has_doc = bool(p.src_doc_file_path)
    result.img_doc = p.src_screenshot

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
        doc_file = EXAMPLES_DOC / p.target_doc_file
        with open(doc_file, "w", encoding="utf-8") as out_f:
            if p.src_doc_file_path:
                content_f = read_rst_file(p.example_dir, files, p.src_doc_file_path)
                headline = get_headline(content_f, p.file_format)
                if not headline:
                    print(f"example_gallery: No headline found in {doc_file}",
                          file=sys.stderr)

                # Copy other files in the 'doc' directory, but
                # excluding the main '.rst' file and all the
                # directories.
                resources = []
                if pyside_example:
                    for _f in p.src_doc_dir.glob("*"):
                        if _f != p.src_doc_file_path and not _f.is_dir():
                            resources.append(_f)
                else:  # Qt example: only use image.
                    if p.src_screenshot:
                        resources.append(p.src_screenshot)
                write_resources(resources, EXAMPLES_DOC)
            else:
                content_f = get_header_title(p.example_dir)
            content_f += get_code_tabs(files, pyproject_file.parent, p.file_format)
            out_f.write(content_f)

        if not opt_quiet:
            print(f"Written: {doc_file}")
    else:
        if not opt_quiet:
            print("Empty '.pyproject' file, skipping")

    result.headline = headline

    return (p.module_name, result)


def example_sort_key(example: ExampleData):
    name = example.example
    return "AAA" + name if "gallery" in name else name


def sort_examples(example):
    result = {}
    for module in example.keys():
        result[module] = sorted(example.get(module), key=example_sort_key)
    return result


def scan_examples_dir(examples_dir, pyside_example=True):
    """Scan a directory of examples."""
    for pyproject_file in examples_dir.glob("**/*.pyproject"):
        if pyproject_file.name != "examples.pyproject":
            module_name, data = write_example(examples_dir, pyproject_file,
                                              pyside_example)
            if module_name not in examples:
                examples[module_name] = []
            examples[module_name].append(data)


if __name__ == "__main__":
    # Only examples with a '.pyproject' file will be listed.
    DIR = Path(__file__).parent
    EXAMPLES_DOC = Path(f"{DIR}/../../sources/pyside6/doc/examples").resolve()
    EXAMPLES_DIR = Path(f"{DIR}/../../examples/").resolve()
    BASE_URL = "https://code.qt.io/cgit/pyside/pyside-setup.git/tree"
    columns = 5
    gallery = ""

    parser = ArgumentParser(description=__doc__, formatter_class=RawTextHelpFormatter)
    TARGET_HELP = f"Directory into which to generate Doc files (default: {str(EXAMPLES_DOC)})"
    parser.add_argument("--target", "-t", action="store", dest="target_dir", help=TARGET_HELP)
    parser.add_argument("--qt-src-dir", "-s", action="store", help="Qt source directory")
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
    EXAMPLES_DOC.mkdir(exist_ok=True)

    scan_examples_dir(EXAMPLES_DIR)
    if options.qt_src_dir:
        qt_src = Path(options.qt_src_dir)
        if not qt_src.is_dir():
            print("Invalid Qt source directory: {}", file=sys.stderr)
            sys.exit(-1)
        scan_examples_dir(qt_src.parent / "qtdoc", pyside_example=False)

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
        for module_name in sorted(examples.keys(), key=module_sort_key):
            e = examples.get(module_name)
            for i in e:
                index_files.append(i.doc_file)
            title = module_title(module_name)
            f.write(f"{title}\n")
            f.write(f"{'*' * len(title)}\n")
            f.write(get_module_gallery(e))
        f.write("\n\n")
        f.write(footer_index)
        for i in index_files:
            f.write(f"   {i}\n")

    if not opt_quiet:
        print(f"Written index: {EXAMPLES_DOC}/index.rst")
