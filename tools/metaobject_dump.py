# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import sys

from dump_metaobject import dump_metaobject
# Import all widget classes to enable instantiating them by type name
from PySide6.QtWidgets import *

DESC = """
metaobject_dump.py <class_name>

Dumps the QMetaObject of a class

Example: metaobject_dump QLabel
"""


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(DESC)
        sys.exit(0)
    app = QApplication(sys.argv)

    type_name = sys.argv[1]
    type_instance = eval(type_name)
    if not type_instance:
        print(f'Invalid type {type_name}')
        sys.exit(1)
    dump_metaobject(type_instance.staticMetaObject)
