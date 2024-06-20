# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

from pathlib import Path
import os
import re
import subprocess
import sys

"""Scan the Qt C++ headers per module for classes that should be present
   in the matching type system and print the missing classes."""


VALUE_TYPE = re.compile(r'^\s*<value-type name="([^"]+)"')


OBJECT_TYPE = re.compile(r'^\s*<object-type name="([^"]+)"')


def query_qtpaths(keyword):
    """Query qtpaths for a keyword."""
    query_cmd = ["qtpaths", "-query", keyword]
    output = subprocess.check_output(query_cmd, stderr=subprocess.STDOUT,
                                     universal_newlines=True)
    return output.strip()


def is_class_exluded(name):
    """Check for excluded classes that do not make sense in a typesystem."""
    if len(name) < 2:
        return True
    if "Iterator" in name or "iterator" in name:
        return True
    if name.startswith("If") or name.startswith("Is") or name.startswith("When"):
        return True
    if name[:1].islower():
        return True
    if name.startswith("QOpenGLFunctions") and name.endswith("Backend"):
        return True
    return False


def class_from_header_line(line):
    """Extract a class name from a C++ header line."""
    def _is_macro(token):
        return "EXPORT" in token or "API" in token

    def _fix_class_name(name):
        pos = name.find('<')  # Some template specialization "class Name<TemplateParam>"
        if pos > 0:
            name = name[:pos]
        if name.endswith(':'):
            name = name[:-1]
        return name

    if line.startswith('//') or line.endswith(';'):  # comment/forward decl
        return None
    line = line.strip()
    if not line.startswith("class ") and not line.startswith("struct "):
        return None
    tokens = line.split()
    pos = 1
    while pos < len(tokens) and _is_macro(tokens[pos]):
        pos += 1
    return _fix_class_name(tokens[pos]) if pos < len(tokens) else None


def classes_from_header(header):
    """Extract classes from C++ header file."""
    result = []
    for line in header.read_text("utf-8").splitlines():
        name = class_from_header_line(line)
        if name and not is_class_exluded(name):
            result.append(name)
    return sorted(result)


def classes_from_typesystem(typesystem):
    """Extract classes from typesystem XML file."""
    result = []
    for line in typesystem.read_text("utf-8").splitlines():
        match = VALUE_TYPE.search(line) or OBJECT_TYPE.search(line)
        if match:
            result.append(match.group(1))
    return sorted(result)


def check_classes(qt_module_inc_dir, pyside_dir):
    """Check classes of a module."""
    module_name = qt_module_inc_dir.name
    sys.stderr.write(f"Checking {module_name} ")
    cpp_classes = []
    typesystem_classes = []
    for header in qt_module_inc_dir.glob("q*.h"):
        if not header.name.endswith("_p.h"):
            cpp_classes.extend(classes_from_header(header))
    for typesystem in pyside_dir.glob("*.xml"):
        typesystem_classes.extend(classes_from_typesystem(typesystem))

    cpp_count = len(cpp_classes)
    typesystem_count = len(typesystem_classes)
    sys.stderr.write(f"found {cpp_count} C++ / {typesystem_count} typesystem classes")
    if cpp_count <= typesystem_count:
        sys.stderr.write(" ok\n")
    else:
        sys.stderr.write(f", {cpp_count-typesystem_count} missing\n")
        for cpp_class in cpp_classes:
            if cpp_class not in typesystem_classes:
                wrapper_name = cpp_class.lower() + "_wrapper.cpp"
                print(f"{module_name}:{cpp_class}:{wrapper_name}")


if __name__ == '__main__':
    qt_version = query_qtpaths("QT_VERSION")
    qt_inc_dir = Path(query_qtpaths("QT_INSTALL_HEADERS"))
    print(f"Qt {qt_version} at {os.fspath(qt_inc_dir.parent)}", file=sys.stderr)

    dir = Path(__file__).parents[1].resolve()
    for module_dir in (dir / "sources" / "pyside6" / "PySide6").glob("Qt*"):
        qt_module_inc_dir = qt_inc_dir / module_dir.name
        if qt_module_inc_dir.is_dir():
            check_classes(qt_module_inc_dir, module_dir)
