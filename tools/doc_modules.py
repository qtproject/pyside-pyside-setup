# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import os
import subprocess
import sys
from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path
import xml.sax
from xml.sax.handler import ContentHandler

DESC = """Print a list of module short names ordered by typesystem dependencies
for which documentation can be built by intersecting the PySide6 modules with
the modules built in Qt."""


ROOT_DIR = Path(__file__).parents[1].resolve()
SOURCE_DIR = ROOT_DIR / "sources" / "pyside6" / "PySide6"


qt_version = None
qt_include_dir = None


class TypeSystemContentHandler(ContentHandler):
    """XML SAX content handler that extracts required modules from the
       "load-typesystem" elements of the typesystem_file. Nodes that start
       with Qt and are marked as generate == "no" are considered required."""

    def __init__(self):
        self.required_modules = []

    def startElement(self, name, attrs):
        if name == "load-typesystem":
            generate = attrs.get("generate", "").lower()
            if generate == "no" or generate == "false":
                load_file_name = attrs.get("name")  # "QtGui/typesystem_gui.xml"
                if load_file_name.startswith("Qt"):
                    slash = load_file_name.find("/")
                    if slash > 0:
                        self.required_modules.append(load_file_name[:slash])


def required_typesystems(module):
    """Determine the required Qt modules by looking at the "load-typesystem"
       elements of the typesystem_file."""
    name = module[2:].lower()
    typesystem_file = SOURCE_DIR / module / f"typesystem_{name}.xml"
    # Use a SAX parser since that works despite undefined entity
    # errors for typesystem entities.
    handler = TypeSystemContentHandler()
    try:
        parser = xml.sax.make_parser()
        parser.setContentHandler(handler)
        parser.parse(typesystem_file)
    except Exception as e:
        print(f"Error parsing {typesystem_file}: {e}", file=sys.stderr)
    return handler.required_modules


def query_qtpaths(keyword):
    query_cmd = ["qtpaths", "-query", keyword]
    output = subprocess.check_output(query_cmd, stderr=subprocess.STDOUT,
                                     universal_newlines=True)
    return output.strip()


def sort_modules(dependency_dict):
    """Sort the modules by dependencies using brute force: Keep adding
       modules all of whose requirements are present to the result list
       until done."""
    result = []
    while True:
        found = False
        for module, dependencies in dependency_dict.items():
            if module not in result:
                if all(dependency in result for dependency in dependencies):
                    result.append(module)
                    found = True
        if not found:
            break

    if len(result) < len(dependency_dict) and verbose:
        for desired_module in dependency_dict.keys():
            if desired_module not in result:
                print(f"Not documenting {desired_module} (missing dependency)",
                      file=sys.stderr)
    return result


def _write_type_system(modules, file):
    """Helper to write the type system for shiboken. It needs to be in
       dependency order to prevent shiboken from loading the included
       typesystems with generate="no", which causes those modules to be
       missing."""
    for module in modules:
        name = module[2:].lower()
        filename = f"{module}/typesystem_{name}.xml"
        print(f'    <load-typesystem name="{filename}" generate="yes"/>',
              file=file)
    print("</typesystem>", file=file)


def write_type_system(modules, filename):
    """Write the type system for shiboken in dependency order."""
    if filename == "-":
        _write_type_system(modules, sys.stdout)
    else:
        path = Path(filename)
        exists = path.exists()
        with path.open(mode="a") as f:
            if not exists:
                print('<typesystem  package="PySide">', file=f)
            _write_type_system(modules, f)


def _write_global_header(modules, file):
    """Helper to write the global header for shiboken."""
    for module in modules:
        print(f"#include <{module}/{module}>", file=file)


def write_global_header(modules, filename):
    """Write the global header for shiboken."""
    if filename == "-":
        _write_global_header(modules, sys.stdout)
    else:
        with Path(filename).open(mode="a") as f:
            _write_global_header(modules, f)


def _write_docconf(modules, file):
    """Helper to write the include paths for the .qdocconf file."""
    # @TODO fix this for macOS frameworks.
    for module in modules:
        root = f"    -I/{qt_include_dir}/{module}"
        print(f"{root} \\", file=file)
        print(f"{root}/{qt_version} \\", file=file)
        print(f"{root}/{qt_version}/{module} \\", file=file)


def write_docconf(modules, filename):
    """Write the include paths for the .qdocconf file."""
    if filename == "-":
        _write_docconf(modules, sys.stdout)
    else:
        with Path(filename).open(mode="a") as f:
            _write_docconf(modules, f)


if __name__ == "__main__":
    argument_parser = ArgumentParser(description=DESC,
                                     formatter_class=RawTextHelpFormatter)
    argument_parser.add_argument("--verbose", "-v", action="store_true",
                                 help="Verbose")
    argument_parser.add_argument("qt_include_dir", help="Qt Include dir",
                                 nargs='?', type=str)
    argument_parser.add_argument("qt_version", help="Qt version string",
                                 nargs='?', type=str)
    argument_parser.add_argument("--typesystem", "-t", help="Typesystem file to write",
                                 action="store", type=str)
    argument_parser.add_argument("--global-header", "-g", help="Global header to write",
                                 action="store", type=str)
    argument_parser.add_argument("--docconf", "-d", help="docconf file to write",
                                 action="store", type=str)

    options = argument_parser.parse_args()
    verbose = options.verbose
    if options.qt_include_dir:
        qt_include_dir = Path(options.qt_include_dir)
        if not qt_include_dir.is_dir():
            print(f"Invalid include directory passed: {options.qt_include_dir}",
                  file=sys.stderr)
            sys.exit(-1)
    else:
        verbose = True  # Called by hand to find out about available modules
        query_cmd = ["qtpaths", "-query", "QT_INSTALL_HEADERS"]
        qt_include_dir = Path(query_qtpaths("QT_INSTALL_HEADERS"))
        if not qt_include_dir.is_dir():
            print("Cannot determine include directory", file=sys.stderr)
            sys.exit(-1)

    qt_version = options.qt_version if options.qt_version else query_qtpaths("QT_VERSION")

    # Build a typesystem dependency dict of the available modules in order
    # to be able to sort_modules by dependencies. This is required as
    # otherwise shiboken will read the required typesystems with
    # generate == "no" and thus omit modules.
    module_dependency_dict = {}
    for m in SOURCE_DIR.glob("Qt*"):
        module = m.name
        qt_include_path = qt_include_dir / module
        if qt_include_path.is_dir():
            module_dependency_dict[module] = required_typesystems(module)
        elif verbose:
            print(f"Not documenting {module} (not built)", file=sys.stderr)

    modules = sort_modules(module_dependency_dict)
    print(" ".join([m[2:] for m in modules]))

    if options.typesystem:
        write_type_system(modules, options.typesystem)
    if options.global_header:
        write_global_header(modules, options.global_header)
    if options.docconf:
        write_docconf(modules, options.docconf)
