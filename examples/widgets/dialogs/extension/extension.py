
#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited.
## Copyright (C) 2016 The Qt Company Ltd.
## Contact: http://www.qt.io/licensing/
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

"""PySide6 port of the widgets/dialogs/extension example from Qt v5.x"""

from PySide6 import QtCore, QtWidgets


class FindDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(FindDialog, self).__init__(parent)

        label = QtWidgets.QLabel("Find &what:")
        line_edit = QtWidgets.QLineEdit()
        label.setBuddy(line_edit)

        case_check_box = QtWidgets.QCheckBox("Match &case")
        from_start_check_box = QtWidgets.QCheckBox("Search from &start")
        from_start_check_box.setChecked(True)

        find_button = QtWidgets.QPushButton("&Find")
        find_button.setDefault(True)

        more_button = QtWidgets.QPushButton("&More")
        more_button.setCheckable(True)
        more_button.setAutoDefault(False)

        button_box = QtWidgets.QDialogButtonBox(QtCore.Qt.Vertical)
        button_box.addButton(find_button, QtWidgets.QDialogButtonBox.ActionRole)
        button_box.addButton(more_button, QtWidgets.QDialogButtonBox.ActionRole)

        extension = QtWidgets.QWidget()

        whole_words_check_box = QtWidgets.QCheckBox("&Whole words")
        backward_check_box = QtWidgets.QCheckBox("Search &backward")
        search_selection_check_box = QtWidgets.QCheckBox("Search se&lection")

        more_button.toggled.connect(extension.setVisible)

        extension_layout = QtWidgets.QVBoxLayout()
        extension_layout.setContentsMargins(0, 0, 0, 0)
        extension_layout.addWidget(whole_words_check_box)
        extension_layout.addWidget(backward_check_box)
        extension_layout.addWidget(search_selection_check_box)
        extension.setLayout(extension_layout)

        top_left_layout = QtWidgets.QHBoxLayout()
        top_left_layout.addWidget(label)
        top_left_layout.addWidget(line_edit)

        left_layout = QtWidgets.QVBoxLayout()
        left_layout.addLayout(top_left_layout)
        left_layout.addWidget(case_check_box)
        left_layout.addWidget(from_start_check_box)
        left_layout.addStretch(1)

        main_layout = QtWidgets.QGridLayout()
        main_layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        main_layout.addLayout(left_layout, 0, 0)
        main_layout.addWidget(button_box, 0, 1)
        main_layout.addWidget(extension, 1, 0, 1, 2)
        self.setLayout(main_layout)

        self.setWindowTitle("Extension")
        extension.hide()


if __name__ == '__main__':

    import sys

    app = QtWidgets.QApplication(sys.argv)
    dialog = FindDialog()
    sys.exit(dialog.exec_())
