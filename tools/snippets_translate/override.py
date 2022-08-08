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
    (EXAMPLES_PATH / "widgets" / "tutorials" / "modelview" / "7_selections.py", "2")
}


_python_example_snippet_mapping = {}


def python_example_snippet_mapping():
    global _python_example_snippet_mapping
    if not _python_example_snippet_mapping:
        result = _PYTHON_EXAMPLE_SNIPPET_MAPPING
        _python_example_snippet_mapping = result

    return _python_example_snippet_mapping
