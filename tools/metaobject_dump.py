#############################################################################
##
## Copyright (C) 2021 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of the Qt for Python project.
##
## $QT_BEGIN_LICENSE:COMM$
##
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## $QT_END_LICENSE$
##
#############################################################################

import sys
from dump_metaobject import dump_metaobject

# Import all widget classes to enable instantiating them by type name
from PySide2.QtWidgets import *


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
        print('Invalid type {}'.format(type_name))
        sys.exit(1)
    dump_metaobject(type_instance.staticMetaObject)
