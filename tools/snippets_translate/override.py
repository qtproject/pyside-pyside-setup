# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

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
