#############################################################################
##
## Copyright (C) 2022 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of the Qt for Python examples of the Qt Toolkit.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of The Qt Company Ltd nor the names of its
##     contributors may be used to endorse or promote products derived
##     from this software without specific prior written permission.
##
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
## $QT_END_LICENSE$
##
#############################################################################

import sys
from argparse import ArgumentParser, RawTextHelpFormatter

from PySide6.QtWidgets import (QApplication, QFileSystemModel,
                               QFileIconProvider, QScroller, QTreeView)
from PySide6.QtCore import QDir

"""PySide6 port of the widgets/itemviews/dirview example from Qt v6.x"""


if __name__ == "__main__":
    app = QApplication(sys.argv)

    name = "Dir View"
    argument_parser = ArgumentParser(description=name,
                                     formatter_class=RawTextHelpFormatter)
    argument_parser.add_argument("--no-custom", "-c", action="store_true",
                                 help="Set QFileSystemModel.DontUseCustomDirectoryIcons")
    argument_parser.add_argument("--no-watch", "-w", action="store_true",
                                 help="Set QFileSystemModel.DontWatch")
    argument_parser.add_argument("directory",
                                 help="The directory to start in.",
                                 nargs='?', type=str)
    options = argument_parser.parse_args()
    root_path = options.directory

    model = QFileSystemModel()
    icon_provider = QFileIconProvider()
    model.setIconProvider(icon_provider)
    model.setRootPath("")
    if options.no_custom:
        model.setOption(QFileSystemModel.DontUseCustomDirectoryIcons)
    if options.no_watch:
        model.setOption(QFileSystemModel.DontWatchForChanges)
    tree = QTreeView()
    tree.setModel(model)
    if root_path:
        root_index = model.index(QDir.cleanPath(root_path))
        if root_index.isValid():
            tree.setRootIndex(root_index)

    # Demonstrating look and feel features
    tree.setAnimated(False)
    tree.setIndentation(20)
    tree.setSortingEnabled(True)
    availableSize = tree.screen().availableGeometry().size()
    tree.resize(availableSize / 2)
    tree.setColumnWidth(0, tree.width() / 3)

    # Make it flickable on touchscreens
    QScroller.grabGesture(tree, QScroller.ScrollerGestureType.TouchGesture)

    tree.setWindowTitle(name)
    tree.show()

    sys.exit(app.exec())

