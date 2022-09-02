#############################################################################
##
## Copyright (C) 2022 The Qt Company Ltd.
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
#############################################################################

from pathlib import Path

ROOT_PATH = Path(__file__).parents[2]
EXAMPLES_PATH = ROOT_PATH / "examples"
TUTORIAL_EXAMPLES_PATH = ROOT_PATH / "sources" / "pyside6" / "doc" / "tutorials"


_PYTHON_EXAMPLE_SNIPPET_MAPPING = {
    ("qtbase/examples/widgets/tutorials/modelview/1_readonly/mymodel.cpp",
     "Quoting ModelView Tutorial"):
    (EXAMPLES_PATH / "widgets" / "tutorials" / "modelview" / "1_readonly.py", "1"),
    ("qtbase/examples/widgets/tutorials/modelview/2_formatting/mymodel.cpp",
     "Quoting ModelView Tutorial"):
    (EXAMPLES_PATH / "widgets" / "tutorials" / "modelview" / "2_formatting.py", "1"),
    ("qtbase/examples/widgets/tutorials/modelview/3_changingmodel/mymodel.cpp",
     "quoting mymodel_QVariant"):
    (EXAMPLES_PATH / "widgets" / "tutorials" / "modelview" / "3_changingmodel.py", "2"),
    ("qtbase/examples/widgets/tutorials/modelview/3_changingmodel/mymodel.cpp",
     "quoting mymodel_a"):
    (EXAMPLES_PATH / "widgets" / "tutorials" / "modelview" / "3_changingmodel.py", "1"),
    ("qtbase/examples/widgets/tutorials/modelview/3_changingmodel/mymodel.cpp",
     "quoting mymodel_b"):
    (EXAMPLES_PATH / "widgets" / "tutorials" / "modelview" / "3_changingmodel.py", "3"),
    ("qtbase/examples/widgets/tutorials/modelview/4_headers/mymodel.cpp",
     "quoting mymodel_c"):
    (EXAMPLES_PATH / "widgets" / "tutorials" / "modelview" / "4_headers.py", "1"),
    ("qtbase/examples/widgets/tutorials/modelview/5_edit/mymodel.cpp",
     "quoting mymodel_e"):
    (EXAMPLES_PATH / "widgets" / "tutorials" / "modelview" / "5_edit.py", "1"),
    ("qtbase/examples/widgets/tutorials/modelview/5_edit/mymodel.cpp",
     "quoting mymodel_f"):
    (EXAMPLES_PATH / "widgets" / "tutorials" / "modelview" / "5_edit.py", "2"),
    ("qtbase/examples/widgets/tutorials/modelview/6_treeview/mainwindow.cpp",
     "Quoting ModelView Tutorial"):
    (EXAMPLES_PATH / "widgets" / "tutorials" / "modelview" / "6_treeview.py", "1"),
    ("qtbase/examples/widgets/tutorials/modelview/7_selections/mainwindow.cpp",
     "quoting modelview_a"):
    (EXAMPLES_PATH / "widgets" / "tutorials" / "modelview" / "7_selections.py", "1"),
    ("qtbase/examples/widgets/tutorials/modelview/7_selections/mainwindow.cpp",
     "quoting modelview_b"):
    (EXAMPLES_PATH / "widgets" / "tutorials" / "modelview" / "7_selections.py", "2"),
    ("qtbase/src/widgets/doc/snippets/qlistview-dnd/mainwindow.cpp.cpp", "0"):
    (TUTORIAL_EXAMPLES_PATH / "modelviewprogramming" / "qlistview-dnd.py", "mainwindow0")
}


_python_example_snippet_mapping = {}


def python_example_snippet_mapping():
    global _python_example_snippet_mapping
    if not _python_example_snippet_mapping:
        result = _PYTHON_EXAMPLE_SNIPPET_MAPPING

        qt_path = "qtbase/src/widgets/doc/snippets/simplemodel-use/main.cpp"
        pyside_path = TUTORIAL_EXAMPLES_PATH / "modelviewprogramming" / "stringlistmodel.py"
        for i in range(3):
            snippet_id = str(i)
            result[(qt_path, snippet_id)] = pyside_path, snippet_id

        qt_path = "qtbase/src/widgets/doc/snippets/stringlistmodel/main.cpp"
        pyside_path = TUTORIAL_EXAMPLES_PATH / "modelviewprogramming" / "stringlistmodel.py"
        for i in range(6):
            snippet_id = str(i)
            result[(qt_path, snippet_id)] = pyside_path, f"main{snippet_id}"

        qt_path = "qtbase/examples/widgets/itemviews/spinboxdelegate/delegate.cpp"
        pyside_path = (EXAMPLES_PATH / "widgets" / "itemviews" / "spinboxdelegate"
                       / "spinboxdelegate.py")
        for i in range(5):
            snippet_id = str(i)
            result[(qt_path, snippet_id)] = pyside_path, snippet_id

        qt_path = "qtbase/src/widgets/doc/snippets/stringlistmodel/model.cpp"
        pyside_path = (TUTORIAL_EXAMPLES_PATH / "modelviewprogramming"
                       / "stringlistmodel.py")
        for i in range(10):
            snippet_id = str(i)
            result[(qt_path, snippet_id)] = pyside_path,  snippet_id

        qt_path = "qtbase/src/widgets/doc/snippets/qlistview-dnd/model.cpp"
        pyside_path = (TUTORIAL_EXAMPLES_PATH / "modelviewprogramming"
                       / "qlistview-dnd.py")
        for i in range(11):
            snippet_id = str(i)
            result[(qt_path, snippet_id)] = pyside_path,  snippet_id

        qt_path = "qtconnectivity/examples/bluetooth/heartrate_game/devicefinder.cpp"
        pyside_path = EXAMPLES_PATH / "bluetooth" / "heartrate_game" / "devicefinder.py"
        for i in range(5):
            snippet_id = f"devicediscovery-{i}"
            result[(qt_path, snippet_id)] = pyside_path,  snippet_id

        qt_path = "qtconnectivity/examples/bluetooth/heartrate_game/devicehandler.cpp"
        pyside_path = EXAMPLES_PATH / "bluetooth" / "heartrate_game" / "devicehandler.py"
        for snippet_id in ["Connect-Signals-1", "Connect-Signals-2",
                           "Filter HeartRate service 2", "Find HRM characteristic",
                           "Reading value"]:
            result[(qt_path, snippet_id)] = pyside_path,  snippet_id

        qt_path = "qtconnectivity/examples/bluetooth/heartrate_server/main.cpp"
        pyside_path = EXAMPLES_PATH / "bluetooth" / "heartrate_server" / "heartrate_server.py"
        for snippet_id in ["Advertising Data", "Start Advertising", "Service Data",
                           "Provide Heartbeat"]:
            result[(qt_path, snippet_id)] = pyside_path,  snippet_id

        _python_example_snippet_mapping = result

    return _python_example_snippet_mapping
