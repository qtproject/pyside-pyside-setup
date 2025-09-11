# Copyright (C) 2025 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import os
import shutil
import sys
from pathlib import Path
from argparse import ArgumentParser, RawDescriptionHelpFormatter

USAGE = """
Updates example images, shaders, *.qml, *.ui, *.qrc and qmldir files from
a Qt source tree.

Check the diffs produced with care ("prefer" in qmldir, QML module
definitions).
"""

BINARY_SUFFIXES = ["jpg", "png", "svgz", "webp"]
TEXT_SUFFIXES = ["frag", "qrc", "qml", "svg", "ui", "vert"]
SUFFIXES = BINARY_SUFFIXES + TEXT_SUFFIXES


QML_SIMPLE_TUTORIAL_NAMES = ["chapter1-basics", "chapter2-methods",
                             "chapter3-bindings", "chapter4-customPropertyTypes",
                             "chapter5-listproperties", "chapter6-plugins"]
QML_SIMPLE_TUTORIALS = ["qml/tutorials/extending-qml/" + n for n in QML_SIMPLE_TUTORIAL_NAMES]

QML_ADVANCED_TUTORIAL_NAMES = ["advanced1-Base-project", "advanced2-Inheritance-and-coercion",
                               "advanced3-Default-properties", "advanced4-Grouped-properties",
                               "advanced5-Attached-properties", "advanced6-Property-value-source"]
QML_ADVANCED_TUTORIALS = ["qml/tutorials/extending-qml-advanced/" + n
                          for n in QML_ADVANCED_TUTORIAL_NAMES]

EXAMPLE_MAPPING = {
    "qtbase": ["corelib/ipc/sharedmemory", "gui/rhiwindow", "sql/books",
               "widgets/animation/easing", "widgets/rhi/simplerhiwidget"],
    "qtconnectivity": ["bluetooth/heartrate_game", "bluetooth/lowenergyscanner"],
    "qtdeclarative": (QML_SIMPLE_TUTORIALS + QML_ADVANCED_TUTORIALS
                      + ["quick/models/stringlistmodel", "quick/models/objectlistmodel",
                         "quick/window",
                         "quick/rendercontrol/rendercontrol_opengl",
                         "quick/scenegraph/openglunderqml",
                         "quick/scenegraph/scenegraph_customgeometry",
                         "quick/customitems/painteditem",
                         "quickcontrols/filesystemexplorer", "quickcontrols/gallery"]),
    "qtgraphs": ["graphs/2d/hellographs", "graphs/3d/bars", "graphs/3d/widgetgraphgallery"],
    "qtlocation": ["location/mapviewer"],
    "qtmultimedia": ["multimedia/camera"],
    "qtquick3d": ["quick3d/customgeometry", "quick3d/intro", "quick3d/proceduraltexture"],
    "qtserialbus": ["serialbus/can", "serialbus/modbus/modbusclient"],
    "qtserialport": ["serialport/terminal"],
    "qtspeech": ["speech/hello_speak"],
    "qtwebchannel": ["webchannel/standalone"],
    "qtwebengine": ["pdfwidgets/pdfviewer", "webenginequick/nanobrowser",
                    "webenginewidgets/notifications", "webenginewidgets/simplebrowser"],
    "qtwebview": ["webview/minibrowser"],
}


file_count = 0
updated_file_count = 0
new_file_count = 0
warnings_count = 0


def pyside_2_qt_example(e):
    """Fix some example names differing in PySide."""
    if "heartrate" in e:
        return e.replace("heartrate_", "heartrate-")
    if e == "webenginequick/nanobrowser":
        return "webenginequick/quicknanobrowser"
    if e.endswith("scenegraph_customgeometry"):
        return e.replace("scenegraph_customgeometry", "customgeometry")
    if e.endswith("modbusclient"):
        return e.replace("modbusclient", "client")
    return e


def files_differ(p1, p2):
    return (p1.stat().st_size != p2.stat().st_size
            or p1.read_bytes() != p2.read_bytes())


def use_file(path):
    """Exclude C++ docs and Qt Creator builds."""
    path_str = os.fspath(path)
    return "/doc/" not in path_str and "_install_" not in path_str


def example_sources(qt_example):
    """Retrieve all update-able files of a Qt C++ example."""
    result = []
    for suffix in SUFFIXES:
        for file in qt_example.glob(f"**/*.{suffix}"):
            if use_file(file):
                result.append(file)
    for file in qt_example.glob("**/qmldir"):
        if use_file(file):
            result.append(file)
    return result


def detect_qml_module(pyside_example, sources):
    """Detect the directory of a QML module of a PySide example.
       While in Qt C++, the QML module's .qml files are typically
       located in the example root, PySide has an additional directory
       since it loads the QML files from the file system.
       Read the qmldir file and check whether a module directory exists."""
    qml_dir_file = None
    for source in sources:
        if source.name == "qmldir":
            qml_dir_file = source
            break
    if not qml_dir_file:
        return None
    for line in qml_dir_file.read_text(encoding="utf-8").split("\n"):
        if line.startswith("module "):
            module = line[7:].strip()
            if (pyside_example / module).is_dir():
                return module
            break
    return None


def sync_example(pyside_example, qt_example, dry_run):
    """Update files of a PySide example."""
    global file_count, updated_file_count, new_file_count, warnings_count
    sources = example_sources(qt_example)
    source_count = len(sources)
    if source_count == 0:
        print(f"No sources found in {qt_example}", file=sys.stderr)
        return
    count = 0
    qml_module = detect_qml_module(pyside_example, sources)
    for source in sources:
        rel_source = source.relative_to(qt_example)
        target = pyside_example / rel_source
        if qml_module and not target.is_file():
            target = pyside_example / qml_module / rel_source
        if target.is_file():
            if files_differ(source, target):
                if not dry_run:
                    shutil.copy(source, target)
                count += 1
        else:
            print(f"{qt_example.name}: {rel_source} does not have an equivalent "
                  "PySide file, skipping", file=sys.stderr)
            warnings_count += 1
            new_file_count += 1
    if count > 0:
        print(f"  {qt_example.name:<30}: Updated {count}/{source_count} files(s)")
    else:
        print(f"  {qt_example.name:<30}: Unchanged, {source_count} files(s)")
    file_count += source_count
    updated_file_count += count


def main():
    global warnings_count
    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
                            description=USAGE)
    parser.add_argument("--dry-run", action="store_true", help="show the files to be updated")
    parser.add_argument('qtsource', nargs=1)
    args = parser.parse_args()
    dry_run = args.dry_run
    qt_source = Path(args.qtsource[0])
    if not qt_source.is_dir():
        raise Exception(f"{qt_source} is not a directory")

    pyside_examples = Path(__file__).parents[1].resolve() / "examples"
    print(qt_source, '->', pyside_examples)

    for qt_module, example_list in EXAMPLE_MAPPING.items():
        for example in example_list:
            pyside_example = pyside_examples / example
            qt_example = (qt_source / qt_module / "examples"
                          / pyside_2_qt_example(example))
            if pyside_example.is_dir() and qt_example.is_dir():
                sync_example(pyside_example, qt_example, dry_run)
            else:
                print(f"Invalid mapping {qt_example} -> {pyside_example}",
                      file=sys.stderr)
                warnings_count += 1
    msg = f"Updated {updated_file_count}/{file_count} file(s)"
    if new_file_count:
        msg += f", {new_file_count} new files(s)"
    if warnings_count:
        msg += f", {warnings_count} warning(s)"
    print(f"\n{msg}.\n")
    return 0


if __name__ == "__main__":
    r = -1
    try:
        r = main()
    except Exception as e:
        print(str(e), file=sys.stderr)
    sys.exit(r)
