# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

import fnmatch
import os
import shutil
import zipfile
import sys
from argparse import ArgumentParser, RawTextHelpFormatter
from dataclasses import dataclass
from enum import IntEnum, Enum
from pathlib import Path
from collections import defaultdict
from typing import DefaultDict

sys.path.append(os.fspath(Path(__file__).parent.parent.parent / "sources" / "pyside-tools"))
from project_lib import parse_pyproject_json, parse_pyproject_toml, \
    PYPROJECT_FILE_PATTERNS, PYPROJECT_TOML_PATTERN, PYPROJECT_JSON_PATTERN  # noqa: E402


class Format(Enum):
    RST = 0
    MD = 1


__doc__ = """\
This tool scans the main repository for examples with project files and generates a documentation
page formatted as a gallery, displaying the examples in a table

For the usage, simply run:
    python tools/example_gallery/main.py
"""
DIR = Path(__file__).parent
EXAMPLES_DOC = Path(f"{DIR}/../../sources/pyside6/doc/examples").resolve()
EXAMPLES_DIR = Path(f"{DIR}/../../examples/").resolve()
TARGET_HELP = f"Directory into which to generate Doc files (default: {str(EXAMPLES_DOC)})"
BASE_URL = "https://code.qt.io/cgit/pyside/pyside-setup.git/tree"
DOC_SUFFIXES = {Format.RST: "rst", Format.MD: "md"}
LITERAL_INCLUDE = ".. literalinclude::"
IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".svgz", ".webp")
# Suffixes to ignore when displaying source files that are referenced in the project file
IGNORED_SUFFIXES = IMAGE_SUFFIXES + (".pdf", ".pyc", ".obj", ".mesh")
LANGUAGE_PATTERNS = {
    "*.h": "cpp",
    "*.cpp": "cpp",
    "*.md": "markdown",
    "*.py": "py",
    "*.qml": "js",
    "*.qmlproject": "js",
    "*.conf": "ini",
    "*.qrc": "xml",
    "*.ui": "xml",
    "*.xbel": "xml",
    "*.xml": "xml",
    "*.html": "html",
    "CMakeLists.txt": "cmake",
}

BASE_CONTENT = """\
.. _pyside6_examples:

Examples
========

 A collection of examples are provided with |project| to help new users
 to understand different use cases of the module.

 You can find all these examples inside the
 `pyside-setup <https://code.qt.io/cgit/pyside/pyside-setup.git/>`_ repository
 on the `examples <https://code.qt.io/cgit/pyside/pyside-setup.git/tree/examples>`_
 directory.

"""

INJECTED_JS = """\
.. raw:: html

    <div id="examples-filter-bar" style="margin: 1.5em 0 1em 0;">
      <input
        id="examples-filter-input"
        type="search"
        placeholder="Filter examples by title..."
        autocomplete="off"
        style="
          width: 100%;
          max-width: 480px;
          padding: 0.5em 0.75em;
          font-size: 1rem;
          border: 1px solid var(--color-foreground-border, #ccc);
          border-radius: 4px;
          background: var(--color-background-primary, #fff);
          color: var(--color-foreground-primary, #000);
          box-sizing: border-box;
        "
      />
      <span
        id="examples-filter-count"
        style="
          display: inline-block;
          margin-left: 0.75em;
          font-size: 0.875rem;
          color: var(--color-foreground-secondary, #666);
          vertical-align: middle;
        "
      ></span>
    </div>

    <script>
    (function () {
      function initFilter() {
        var input = document.getElementById('examples-filter-input');
        var counter = document.getElementById('examples-filter-count');
        if (!input) return;

        input.addEventListener('input', function () {
          var query = input.value.trim().toLowerCase();
          var totalVisible = 0;

          var dropdowns = document.querySelectorAll('details.sd-dropdown');

          dropdowns.forEach(function (dropdown) {
            var cols = dropdown.querySelectorAll('.sd-col');
            var visibleInSection = 0;

            cols.forEach(function (col) {
              var titleEl = col.querySelector('.sd-card-title');
              var raw = titleEl ? titleEl.textContent.trim() : '';
              var title = raw.replace(/([a-z])([A-Z])/g, '$1 $2').replace(/[-()]/g, ' ').toLowerCase();
              var words = query.toLowerCase().split(/\s+/).filter(Boolean);
              var matches = !query || words.every(function(w) {
                return title.split(/\s+/).some(function(t) { return t.indexOf(w) === 0; });
              });
              //var matches = !query || title.indexOf(query) !== -1;

              // Use setProperty with !important to win over any flexbox/grid
              // class-based CSS that sphinx-design may apply on the .sd-col
              col.style.setProperty('display', matches ? '' : 'none', matches ? '' : 'important');
              if (matches) {
                visibleInSection++;
                totalVisible++;
              }
            });

            if (query) {
              dropdown.style.display = visibleInSection > 0 ? '' : 'none';
              // Only open if there are matches; don't close manually opened ones
              if (visibleInSection > 0) dropdown.open = true;
            } else {
              dropdown.style.display = '';
              dropdown.open = false;
              cols.forEach(function (col) {
                col.style.removeProperty('display');
              });
            }
          });

          counter.textContent = query
            ? totalVisible + ' example' + (totalVisible !== 1 ? 's' : '') + ' found'
            : '';
        });
      }

      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initFilter);
      } else {
        initFilter();
      }
    })();
    </script>
"""
# We generate a 'toctree' at the end of the file to include the new 'example' rst files, so we get
# no warnings and also that users looking for them will be able to, since they are indexed
# Notice that :hidden: will not add the list of files by the end of the main examples HTML page.
FOOTER_INDEX = """\
.. toctree::
    :hidden:
    :maxdepth: 1

"""
TUTORIAL_HEADLINES = {
    "tutorials/extending-qml/chapter": "Tutorial: Writing QML Extensions with Python",
    "tutorials/extending-qml-advanced/advanced": "Tutorial: Writing advanced QML Extensions with"
                                                 "Python",
    "tutorials/finance_manager": "Tutorial: Finance Manager - Integrating PySide6 with SQLAlchemy "
                                 "and FastAPI",
}


class ModuleType(IntEnum):
    ESSENTIALS = 0
    ADDONS = 1
    M2M = 2


def get_lexer(path: Path) -> str:
    """Given a file path, return the language lexer to use for syntax highlighting"""
    for pattern, lexer in LANGUAGE_PATTERNS.items():
        if fnmatch.fnmatch(path.name, pattern):
            return lexer
    # Default to text
    return "text"


def ind(level: int) -> str:
    """Return a string of spaces for string indentation given certain level"""
    return " " * 4 * level


def add_indent(s: str, level: int) -> str:
    """Add indentation to a string"""
    new_s = ""
    for line in s.splitlines():
        if line.strip():
            new_s += f"{ind(level)}{line}\n"
        else:
            # Empty line
            new_s += "\n"
    return new_s


def check_img_ext(image_path: Path) -> bool:
    """Check whether a file path is an image depending on its suffix."""
    return image_path.suffix in IMAGE_SUFFIXES


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


def module_sort_key(name: str) -> str:
    """Return a key for sorting the Qt modules."""
    description = MODULE_DESCRIPTIONS.get(name)
    module_type = int(description.module_type) if description else 5
    sort_key = description.sort_key if description else 100
    return f"{module_type}:{sort_key:04}:{name}"


def module_title(name: str) -> str:
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

    example_name: str = None
    module: str = None
    extra: str = None
    doc_file: str = None
    file_format: Format = None
    abs_path: str = None
    src_doc_file: Path = None
    img_doc: Path = None
    tutorial: str = None
    headline: str = ""


def get_module_gallery(examples: list[ExampleData]) -> str:
    """
    This function takes a list of examples from one specific module and returns the resulting string
    in RST format that can be used to generate the table for the examples
    """

    gallery = (
        f"{ind(1)}.. grid:: 1 3 3 3\n"
        f"{ind(2)}:gutter: 3\n\n"
    )

    for i, example in enumerate(examples):
        suffix = DOC_SUFFIXES[example.file_format]
        # doc_file with suffix removed, to be used as a sphinx reference
        # lower case sphinx reference
        # this seems to be a bug or a requirement from sphinx
        doc_file_name = example.doc_file.replace(f".{suffix}", "").lower()

        name = example.example_name
        underline = example.module

        if example.extra:
            underline += f"/{example.extra}"

        if i > 0:
            gallery += "\n"
        img_name = example.img_doc.name if example.img_doc else "../example_no_image.png"

        # Fix long names
        if name.startswith("chapter"):
            name = name.replace("chapter", "c")
        elif name.startswith("advanced"):
            name = name.replace("advanced", "a")

        # Handling description from original file
        desc = ""
        if example.src_doc_file:
            with example.src_doc_file.open("r", encoding="utf-8") as f:
                # Read the first line
                first_line = f.readline().strip()

                # Check if the first line is a reference (starts with '(' and ends with ')=' for MD,
                # or starts with '.. ' and ends with '::' for RST)
                if ((example.file_format == Format.MD and first_line.startswith('(')
                     and first_line.endswith(')='))
                        or (example.file_format == Format.RST and first_line.startswith('.. ')
                            and first_line.endswith('::'))):
                    # The first line is a reference, so read the next lines until a non-empty line
                    # is found
                    while True:
                        title_line = f.readline().strip()
                        if title_line:
                            break
                else:
                    # The first line is the title
                    title_line = first_line

                # The next line handling depends on the file format
                line = f.readline().strip()

                if example.file_format == Format.MD:
                    # For markdown, the second line is the empty line
                    pass
                else:
                    # For RST and other formats, the second line is the underline under the title
                    # The next line should be empty
                    line = f.readline().strip()

                if line != "":
                    raise RuntimeError(
                        f"{line} was expected to be empty. Doc file: {example.src_doc_file}")

                # Now read until another empty line
                lines = []
                while True:
                    line = f.readline().strip()
                    if line.startswith(".. tags") or line.startswith("#"):
                        # Skip the empty line
                        _ = f.readline()
                        # Read the next line
                        line = f.readline().strip()

                    if not line:
                        break
                    lines.append(line)

                desc = " ".join(lines)
                if len(desc) > 120:
                    desc = desc[:120] + "..."
        else:
            if not opt_quiet:
                print(
                    f"example_gallery: No source doc file found in {example.abs_path}."
                    f"Skipping example",
                    file=sys.stderr,
                )

        if not (title := example.headline):
            title = f"{name} from ``{underline}``."

        # Clean refs from desc
        if ":ref:" in desc:
            desc = desc.replace(":ref:`", "")
        desc = desc.replace("`", "")

        gallery += f"{ind(2)}.. grid-item-card:: {title}\n"
        gallery += f"{ind(3)}:class-item: cover-img\n"
        gallery += f"{ind(3)}:link: {doc_file_name}\n"
        gallery += f"{ind(3)}:link-type: ref\n"
        gallery += f"{ind(3)}:img-top: {img_name}\n\n"
        gallery += f"{ind(3)}+++\n"
        gallery += f"{ind(3)}{desc}\n"

    return f"{gallery}\n"


def remove_licenses(file_content: str) -> str:
    # Return the content of the file with the Qt license removed
    new_s = []
    for line in file_content.splitlines():
        if line.strip().startswith(("/*", "**", "##")):
            continue
        new_s.append(line)
    return "\n".join(new_s)


def make_zip_archive(output_path: Path, src: Path, skip_dirs: list[str] = None):
    # Create a .zip file from a source directory ignoring the specified directories
    src_path = src.expanduser().resolve(strict=True)
    if skip_dirs is None:
        skip_dirs = []
    if not isinstance(skip_dirs, list):
        raise ValueError("Type error: 'skip_dirs' must be a list instance")
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in src_path.rglob('*'):
            skip = False
            _parts = file.relative_to(src_path).parts
            for sd in skip_dirs:
                if sd in _parts:
                    skip = True
                    break
            if not skip:
                zf.write(file, file.relative_to(src_path.parent))


def get_rstinc_for_file(project_dir: Path, project_file: Path) -> Path | None:
    """Return the .rstinc file in the doc folder describing a source file, if found"""
    rst_file = project_dir
    if project_dir.name != "doc":  # Special case: Dummy .pyproject file in doc dir
        rst_file /= "doc"
    rst_file /= project_file.name + ".rstinc"
    return rst_file if rst_file.is_file() else None


def get_code_tabs(files: list[Path], project_dir: Path, file_format: Format) -> str:
    """
    Return the string which contains the code tabs source for the example
    Also creates a .zip file for downloading the source files
    """
    content = "\n"

    # Prepare ZIP file, and copy to final destination
    zip_name = f"{project_dir.name}.zip"
    make_zip_archive(EXAMPLES_DOC / zip_name, project_dir, skip_dirs=["doc"])

    if file_format == Format.RST:
        content += f":download:`Download this example <{zip_name}>`\n\n"
    elif file_format == Format.MD:
        content += f"{{download}}`Download this example <{zip_name}>`\n\n"
        # MD files wrap the content in a eval-rst block
        content += "```{eval-rst}\n"
    else:
        raise ValueError(f"Unknown documentation file format {file_format}")

    if files:
        content += ".. tab-set::\n\n"

    for i, file in enumerate(files):
        if file.suffix in IGNORED_SUFFIXES:
            continue

        try:
            tab_title = file.relative_to(project_dir).as_posix()
        except ValueError:
            # The file is outside project_dir, so the best we can do is to use the file name
            tab_title = file.name

        content += f"{ind(1)}.. tab-item:: {tab_title}\n\n"

        if doc_rstinc_file := get_rstinc_for_file(project_dir, file):
            content += add_indent(doc_rstinc_file.read_text("utf-8"), 2)
            content += "\n"

        content += add_indent(f"{ind(1)}.. code-block:: {get_lexer(file)}", 1)
        content += "\n"

        try:
            file_content = remove_licenses(file.read_text(encoding="utf-8"))
        except UnicodeDecodeError as e:
            raise RuntimeError(f"example_gallery: error decoding {file}: {e}")
        except FileNotFoundError as e:
            raise RuntimeError(f"example_gallery: error opening {file}: {e}")

        content += add_indent(file_content, 3)
        content += "\n\n"

    if file_format == Format.MD:
        # Close the eval-rst block
        content += "```"

    return content


def get_default_header_title(example_dir: Path) -> str:
    """Get a default header title for an example directory without a doc file"""
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


def rel_path(from_path: Path, to_path: Path) -> str:
    """
    Get a relative path for a given path that is not a subpath (where Path.relative_to() fails)
    of from_path via a common ancestor path

    For example: from_path = Path("/a/b/c/d"), to_path = Path("/a/b/e/f"). Returns: "../../e/f"
    """
    common_path = Path(*os.path.commonprefix([from_path.parts, to_path.parts]))
    up_dirs = len(from_path.parts) - len(common_path.parts)
    prefix = up_dirs * "../"
    relative_to_common = to_path.relative_to(common_path).as_posix()
    return f"{prefix}{relative_to_common}"


def read_rst_file(project_dir: Path, project_files: list[Path], doc_rst: Path) -> str:
    """
    Read the example .rst file and replace Sphinx literal includes of project files by paths
    relative to the example directory
    Note: Sphinx does not handle absolute paths as expected, they need to be relative
    """
    content = Path(doc_rst).read_text(encoding="utf-8")
    if LITERAL_INCLUDE not in content:
        # The file does not contain any literal includes, so we can return it as is
        return content

    result = []
    path_to_example = rel_path(EXAMPLES_DOC, project_dir)
    for line in content.split("\n"):
        if line.startswith(LITERAL_INCLUDE):
            file = line[len(LITERAL_INCLUDE) + 1:].strip()
            file_path = project_dir / file
            if file_path not in project_files:
                raise RuntimeError(f"File {file} not found in project files: {project_files}")
            line = f"{LITERAL_INCLUDE} {path_to_example}/{file}"
        result.append(line)
    return "\n".join(result)


def get_headline(text: str, file_format: Format) -> str:
    """Find the headline in the documentation file."""
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
    else:
        raise ValueError(f"Unknown file format {file_format}")
    return ""


def get_doc_source_file(original_doc_dir: Path, example_name: str) -> tuple[Path, Format] | None:
    """
    Find the doc source file given a doc directory and an example name
    Returns the doc file path and the file format, if found
    """
    if not original_doc_dir.is_dir():
        return None

    for file_format, suffix in DOC_SUFFIXES.items():
        result = original_doc_dir / f"{example_name}.{suffix}"
        if result.is_file():
            return result, file_format
    return None


def get_screenshot(image_dir: Path, example_name: str) -> Path | None:
    """
    Find an screenshot given an image directory and the example name
    Returns the image with the same example_name, if found
    If not found, the first image in the directory is returned
    """
    if not image_dir.is_dir():
        return None
    images = [i for i in image_dir.glob("*") if i.is_file() and check_img_ext(i)]
    example_images = [i for i in images if i.name.startswith(example_name)]
    if example_images:
        return example_images[0]
    if images:
        return images[0]
    return None


def write_resources(src_list: list[Path], dst: Path):
    """Write a list of example resource paths to the dst path."""
    for src in src_list:
        resource_written = shutil.copy(src, dst / src.name)
        if not opt_quiet:
            print(f"Written resource: {resource_written}")


@dataclass
class ExampleParameters:
    """Parameters obtained from scanning the examples directory."""
    example_dir: Path = None
    module_name: str = ""
    example_name: str = ""
    target_doc_file: str = None
    extra_names: str = ""
    src_doc_dir: Path = None
    src_doc_file_path: Path = None
    src_screenshot: Path = None
    file_format: Format = Format.RST


def get_pyside_example_parameters(example_root: Path, pyproject_file: Path) -> ExampleParameters:
    """Analyze a PySide example folder to get the example parameters"""
    p = ExampleParameters()

    p.example_dir = pyproject_file.parent
    if list(p.example_dir.parent.glob("*.qmlproject")) and p.example_dir.name == "Python":
        # Design Studio project example
        p.example_dir = pyproject_file.parent.parent

    if p.example_dir.name == "doc":  # Dummy pyproject file in doc dir (e.g. scriptableapplication)
        p.example_dir = p.example_dir.parent

    parts = p.example_dir.parts[len(example_root.parts):]
    p.module_name = parts[0]
    p.example_name = parts[-1]
    # handling subdirectories besides the module level and the example
    p.extra_names = "" if len(parts) == 2 else "_".join(parts[1:-1])

    # Check for a 'doc' directory inside the example
    src_doc_dir = p.example_dir / "doc"

    if src_doc_dir.is_dir():
        src_doc_file = get_doc_source_file(src_doc_dir, p.example_name)
        if src_doc_file:
            p.src_doc_file_path, p.file_format = src_doc_file
            p.src_doc_dir = src_doc_dir
            p.src_screenshot = get_screenshot(src_doc_dir, p.example_name)

    target_suffix = DOC_SUFFIXES[p.file_format]
    doc_file = f"example_{p.module_name}_{p.extra_names}_{p.example_name}.{target_suffix}"
    p.target_doc_file = doc_file.replace("__", "_")
    return p


def get_qt_example_parameters(pyproject_file: Path) -> ExampleParameters:
    """
    Analyze a Qt repository example to get its parameters.
    For instance, the qtdoc/examples/demos/mediaplayer example
    """
    p = ExampleParameters()

    p.example_dir = pyproject_file.parent
    p.module_name = "Qt Demos"
    p.example_name = p.example_dir.name
    # Check for a 'doc' directory inside the example (qdoc)
    doc_root = p.example_dir / "doc"
    if doc_root.is_dir():
        src_doc_file = get_doc_source_file(doc_root / "src", p.example_name)
        if src_doc_file:
            p.src_doc_file_path, p.file_format = src_doc_file
            p.src_doc_dir = doc_root
            p.src_screenshot = get_screenshot(doc_root / "images", p.example_name)
        else:
            raise ValueError(f"No source file found in {doc_root} / src given {p.example_name}")
    else:
        raise ValueError(f"No doc directory found in {p.example_dir}")
    target_suffix = DOC_SUFFIXES[p.file_format]
    p.target_doc_file = f"example_qtdemos_{p.example_name}.{target_suffix}"
    return p


def write_example(
    example_root: Path, pyproject_file: Path, pyside_example: bool = True
) -> tuple[str, ExampleData]:
    """
    Read the project file and documentation, create the .rst file and copy the example data
    Return a tuple with the module name and an ExampleData instance
    """
    # Get the example parameters depending on whether it is a PySide example or a Qt one
    p: ExampleParameters = (
        get_pyside_example_parameters(example_root, pyproject_file)
        if pyside_example else get_qt_example_parameters(pyproject_file))

    result = ExampleData()
    result.example_name = p.example_name
    result.module = p.module_name
    result.extra = p.extra_names
    result.doc_file = p.target_doc_file
    result.file_format = p.file_format
    result.abs_path = str(p.example_dir)
    result.src_doc_file = p.src_doc_file_path
    result.img_doc = p.src_screenshot
    result.tutorial = TUTORIAL_HEADLINES.get(result.abs_path, "")

    if pyproject_file.match(PYPROJECT_JSON_PATTERN):
        pyproject_parse_result = parse_pyproject_json(pyproject_file)
    elif pyproject_file.match(PYPROJECT_TOML_PATTERN):
        pyproject_parse_result = parse_pyproject_toml(pyproject_file)
    else:
        raise RuntimeError(f"Invalid project file: {pyproject_file}")

    if pyproject_parse_result.errors:
        raise RuntimeError(f"Error reading {pyproject_file}: {pyproject_parse_result.errors}")

    for file in pyproject_parse_result.files:
        if not Path(file).exists:
            raise FileNotFoundError(f"{file} listed in {pyproject_file} does not exist")

    files = pyproject_parse_result.files
    headline = ""
    if files:
        doc_file = EXAMPLES_DOC / p.target_doc_file
        sphnx_ref_example = p.target_doc_file.replace(f'.{DOC_SUFFIXES[p.file_format]}', '')
        # lower case sphinx reference
        # this seems to be a bug or a requirement from sphinx
        sphnx_ref_example = sphnx_ref_example.lower()

        if p.file_format == Format.RST:
            content_f = f".. _{sphnx_ref_example}:\n\n"
        elif p.file_format == Format.MD:
            content_f = f"({sphnx_ref_example})=\n\n"
        else:
            raise ValueError(f"Invalid file format {p.file_format}")

        with open(doc_file, "w", encoding="utf-8") as out_f:
            if p.src_doc_file_path:
                content_f += read_rst_file(p.example_dir, files, p.src_doc_file_path)
                headline = get_headline(content_f, p.file_format)
                if not headline and not opt_quiet:
                    print(f"example_gallery: No headline found in {doc_file}", file=sys.stderr)

                # Copy other files in the 'doc' directory, but excluding the main '.rst' file and
                # all the directories
                resources = []
                if pyside_example:
                    for _f in p.src_doc_dir.glob("*"):
                        if _f != p.src_doc_file_path and not _f.is_dir():
                            resources.append(_f)
                elif p.src_screenshot:
                    # Qt example: only use image, if found
                    resources.append(p.src_screenshot)
                write_resources(resources, EXAMPLES_DOC)
            else:
                content_f += get_default_header_title(p.example_dir)
            content_f += get_code_tabs(files, p.example_dir, p.file_format)
            out_f.write(content_f)

        if not opt_quiet:
            print(f"Written: {doc_file}")
    else:
        if not opt_quiet:
            print(f"{pyproject_file} does not contain any file, skipping")

    result.headline = headline

    return p.module_name, result


def example_sort_key(example: ExampleData) -> str:
    """
    Return a key for sorting the examples. Tutorials are sorted first, then the examples which
    contain "gallery" in their name, then alphabetically
    """
    result = ""
    if example.tutorial:
        result += "AA:" + example.tutorial + ":"
    elif "gallery" in example.example_name:
        result += "AB:"
    result += example.example_name
    return result


def sort_examples(examples: dict[str, list[ExampleData]]) -> dict[str, list[ExampleData]]:
    """Sort the examples using a custom function."""
    result = {}
    for module in examples.keys():
        result[module] = sorted(examples.get(module), key=example_sort_key)
    return result


def scan_examples_dir(
    examples_dir: Path, pyside_example: bool = True
) -> dict[str, list[ExampleData]]:
    """
    Scan a directory of examples and return a dictionary with the found examples grouped by module
    Also creates the .rst file for each example
    """
    examples: dict[str, list[ExampleData]] = defaultdict(list)
    # Find all the project files contained in the examples directory
    project_files: list[Path] = []
    for project_file_pattern in PYPROJECT_FILE_PATTERNS:
        project_files.extend(examples_dir.glob(f"**/{project_file_pattern}"))

    for project_file in project_files:
        if project_file.name == "examples.pyproject":
            # Ignore this project file. It contains files from many examples
            continue

        module_name, data = write_example(examples_dir, project_file, pyside_example)
        examples[module_name].append(data)

    return dict(examples)


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__, formatter_class=RawTextHelpFormatter)
    parser.add_argument("--target", "-t", action="store", dest="target_dir", help=TARGET_HELP)
    parser.add_argument("--qt-src-dir", "-s", action="store", help="Qt source directory")
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet")
    options = parser.parse_args()
    opt_quiet = options.quiet
    if options.target_dir:
        EXAMPLES_DOC = Path(options.target_dir).resolve()

    # This script will be in charge of:
    #   * Getting all the project files
    #   * Gather the information of the examples
    #   * Read the project file to output the content of each source file
    #     on the final .rst file for that specific example

    # Create the 'examples' directory if it doesn't exist
    # If it does exist, try to remove it and create a new one to start fresh
    if EXAMPLES_DOC.is_dir():
        shutil.rmtree(EXAMPLES_DOC, ignore_errors=True)
        if not opt_quiet:
            print("WARNING: Deleted existing examples HTML directory")
    EXAMPLES_DOC.mkdir(exist_ok=True)

    examples = scan_examples_dir(EXAMPLES_DIR)

    if options.qt_src_dir:
        # Scan the Qt source directory for Qt examples and include them in the dictionary of
        # discovered examples
        qt_src = Path(options.qt_src_dir)
        if not qt_src.is_dir():
            raise RuntimeError(f"Invalid Qt source directory: {qt_src}")
        examples.update(scan_examples_dir(qt_src.parent / "qtdoc", pyside_example=False))

    examples = sort_examples(examples)

    # List of all the example files found to be included in the index table of contents
    index_files: list[str] = []
    # Write the main example .rst file and the example files
    with open(f"{EXAMPLES_DOC}/index.rst", "w") as f:
        f.write(BASE_CONTENT)
        f.write(INJECTED_JS)
        for module_name in sorted(examples.keys(), key=module_sort_key):
            module_examples = examples.get(module_name)
            tutorial_examples: DefaultDict[str, list[ExampleData]] = defaultdict(list)
            non_tutorial_examples: list[ExampleData] = []

            for example in module_examples:
                index_files.append(example.doc_file)
                if example.tutorial:
                    tutorial_examples[example.tutorial].append(example)
                else:
                    non_tutorial_examples.append(example)

            title = module_title(module_name)
            f.write(f".. dropdown:: {title}\n\n")

            # Write tutorial examples under their tutorial names
            for tutorial_name, tutorial_exs in tutorial_examples.items():
                f.write(f"{ind(1)}**{tutorial_name}**\n\n")
                f.write(get_module_gallery(tutorial_exs))

            # If there are non-tutorial examples and tutorials exist
            if tutorial_examples and non_tutorial_examples:
                f.write(f"{ind(1)}**Other Examples**\n\n")
                f.write(get_module_gallery(non_tutorial_examples))
            # If no tutorials exist, list all examples
            elif not tutorial_examples:
                f.write(get_module_gallery(module_examples))

        f.write("\n\n")

        # Add the list of the example files found to the index table of contents
        f.write(FOOTER_INDEX)
        for index_file in index_files:
            f.write(f"{ind(1)}{index_file}\n")

    if not opt_quiet:
        print(f"Written index: {EXAMPLES_DOC}/index.rst")
