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

from PySide6 import QtCore, QtGui, QtWidgets

import classwizard_rc


class ClassWizard(QtWidgets.QWizard):
    def __init__(self, parent=None):
        super(ClassWizard, self).__init__(parent)

        self.addPage(IntroPage())
        self.addPage(ClassInfoPage())
        self.addPage(CodeStylePage())
        self.addPage(OutputFilesPage())
        self.addPage(ConclusionPage())

        self.setPixmap(QtWidgets.QWizard.BannerPixmap,
                QtGui.QPixmap(':/images/banner.png'))
        self.setPixmap(QtWidgets.QWizard.BackgroundPixmap,
                QtGui.QPixmap(':/images/background.png'))

        self.setWindowTitle("Class Wizard")

    def accept(self):
        class_name = self.field('className')
        base_class = self.field('baseClass')
        macro_name = self.field('macroName')
        base_include = self.field('baseInclude')

        output_dir = self.field('outputDir')
        header = self.field('header')
        implementation = self.field('implementation')

        block = ''

        if self.field('comment'):
            block += '/*\n'
            block += '    ' + header + '\n'
            block += '*/\n'
            block += '\n'

        if self.field('protect'):
            block += '#ifndef ' + macro_name + '\n'
            block += '#define ' + macro_name + '\n'
            block += '\n'

        if self.field('includeBase'):
            block += '#include ' + base_include + '\n'
            block += '\n'

        block += 'class ' + class_name
        if base_class:
            block += ' : public ' + base_class

        block += '\n'
        block += '{\n'

        if self.field('qobjectMacro'):
            block += '    Q_OBJECT\n'
            block += '\n'

        block += 'public:\n'

        if self.field('qobjectCtor'):
            block += '    ' + class_name + '(QObject *parent = 0);\n'
        elif self.field('qwidgetCtor'):
            block += '    ' + class_name + '(QWidget *parent = 0);\n'
        elif self.field('defaultCtor'):
            block += '    ' + class_name + '();\n'

            if self.field('copyCtor'):
                block += '    ' + class_name + '(const ' + class_name + ' &other);\n'
                block += '\n'
                block += '    ' + class_name + ' &operator=' + '(const ' + class_name + ' &other);\n'

        block += '};\n'

        if self.field('protect'):
            block += '\n'
            block += '#endif\n'

        header_file = QtCore.QFile(output_dir + '/' + header)

        if not header_file.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text):
            name = header_file.fileName()
            reason = header_file.errorString()
            QtWidgets.QMessageBox.warning(None, "Class Wizard",
                    f"Cannot write file {name}:\n{reason}")
            return

        header_file.write(QtCore.QByteArray(block.encode("utf-8")))

        block = ''

        if self.field('comment'):
            block += '/*\n'
            block += '    ' + implementation + '\n'
            block += '*/\n'
            block += '\n'

        block += '#include "' + header + '"\n'
        block += '\n'

        if self.field('qobjectCtor'):
            block += class_name + '::' + class_name + '(QObject *parent)\n'
            block += '    : ' + base_class + '(parent)\n'
            block += '{\n'
            block += '}\n'
        elif self.field('qwidgetCtor'):
            block += class_name + '::' + class_name + '(QWidget *parent)\n'
            block += '    : ' + base_class + '(parent)\n'
            block += '{\n'
            block += '}\n'
        elif self.field('defaultCtor'):
            block += class_name + '::' + class_name + '()\n'
            block += '{\n'
            block += '    // missing code\n'
            block += '}\n'

            if self.field('copyCtor'):
                block += '\n'
                block += class_name + '::' + class_name + '(const ' + class_name + ' &other)\n'
                block += '{\n'
                block += '    *this = other;\n'
                block += '}\n'
                block += '\n'
                block += class_name + ' &' + class_name + '::operator=(const ' + class_name + ' &other)\n'
                block += '{\n'

                if base_class:
                    block += '    ' + base_class + '::operator=(other);\n'

                block += '    // missing code\n'
                block += '    return *this;\n'
                block += '}\n'

        implementation_file = QtCore.QFile(output_dir + '/' + implementation)

        if not implementation_file.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text):
            name = implementation_file.fileName()
            reason = implementation_file.errorString()
            QtWidgets.QMessageBox.warning(None, "Class Wizard",
                    f"Cannot write file {name}:\n{reason}")
            return

        implementation_file.write(QtCore.QByteArray(block.encode("utf-8")))

        super(ClassWizard, self).accept()


class IntroPage(QtWidgets.QWizardPage):
    def __init__(self, parent=None):
        super(IntroPage, self).__init__(parent)

        self.setTitle("Introduction")
        self.setPixmap(QtWidgets.QWizard.WatermarkPixmap,
                QtGui.QPixmap(':/images/watermark1.png'))

        label = QtWidgets.QLabel("This wizard will generate a skeleton C++ class "
                "definition, including a few functions. You simply need to "
                "specify the class name and set a few options to produce a "
                "header file and an implementation file for your new C++ "
                "class.")
        label.setWordWrap(True)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)


class ClassInfoPage(QtWidgets.QWizardPage):
    def __init__(self, parent=None):
        super(ClassInfoPage, self).__init__(parent)

        self.setTitle("Class Information")
        self.setSubTitle("Specify basic information about the class for "
                "which you want to generate skeleton source code files.")
        self.setPixmap(QtWidgets.QWizard.LogoPixmap,
                QtGui.QPixmap(':/images/logo1.png'))

        class_name_label = QtWidgets.QLabel("&Class name:")
        class_name_line_edit = QtWidgets.QLineEdit()
        class_name_label.setBuddy(class_name_line_edit)

        base_class_label = QtWidgets.QLabel("B&ase class:")
        base_class_line_edit = QtWidgets.QLineEdit()
        base_class_label.setBuddy(base_class_line_edit)

        qobject_macro_check_box = QtWidgets.QCheckBox("Generate Q_OBJECT &macro")

        group_box = QtWidgets.QGroupBox("C&onstructor")

        qobject_ctor_radio_button = QtWidgets.QRadioButton("&QObject-style constructor")
        qwidget_ctor_radio_button = QtWidgets.QRadioButton("Q&Widget-style constructor")
        default_ctor_radio_button = QtWidgets.QRadioButton("&Default constructor")
        copy_ctor_check_box = QtWidgets.QCheckBox("&Generate copy constructor and operator=")

        default_ctor_radio_button.setChecked(True)

        default_ctor_radio_button.toggled.connect(copy_ctor_check_box.setEnabled)

        self.registerField('className*', class_name_line_edit)
        self.registerField('baseClass', base_class_line_edit)
        self.registerField('qobjectMacro', qobject_macro_check_box)
        self.registerField('qobjectCtor', qobject_ctor_radio_button)
        self.registerField('qwidgetCtor', qwidget_ctor_radio_button)
        self.registerField('defaultCtor', default_ctor_radio_button)
        self.registerField('copyCtor', copy_ctor_check_box)

        group_box_layout = QtWidgets.QVBoxLayout()
        group_box_layout.addWidget(qobject_ctor_radio_button)
        group_box_layout.addWidget(qwidget_ctor_radio_button)
        group_box_layout.addWidget(default_ctor_radio_button)
        group_box_layout.addWidget(copy_ctor_check_box)
        group_box.setLayout(group_box_layout)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(class_name_label, 0, 0)
        layout.addWidget(class_name_line_edit, 0, 1)
        layout.addWidget(base_class_label, 1, 0)
        layout.addWidget(base_class_line_edit, 1, 1)
        layout.addWidget(qobject_macro_check_box, 2, 0, 1, 2)
        layout.addWidget(group_box, 3, 0, 1, 2)
        self.setLayout(layout)


class CodeStylePage(QtWidgets.QWizardPage):
    def __init__(self, parent=None):
        super(CodeStylePage, self).__init__(parent)

        self.setTitle("Code Style Options")
        self.setSubTitle("Choose the formatting of the generated code.")
        self.setPixmap(QtWidgets.QWizard.LogoPixmap,
                QtGui.QPixmap(':/images/logo2.png'))

        comment_check_box = QtWidgets.QCheckBox("&Start generated files with a "
                "comment")
        comment_check_box.setChecked(True)

        protect_check_box = QtWidgets.QCheckBox("&Protect header file against "
                "multiple inclusions")
        protect_check_box.setChecked(True)

        macro_name_label = QtWidgets.QLabel("&Macro name:")
        self._macro_name_line_edit = QtWidgets.QLineEdit()
        macro_name_label.setBuddy(self._macro_name_line_edit)

        self._include_base_check_box = QtWidgets.QCheckBox("&Include base class "
                "definition")
        self._base_include_label = QtWidgets.QLabel("Base class include:")
        self._base_include_line_edit = QtWidgets.QLineEdit()
        self._base_include_label.setBuddy(self._base_include_line_edit)

        protect_check_box.toggled.connect(macro_name_label.setEnabled)
        protect_check_box.toggled.connect(self._macro_name_line_edit.setEnabled)
        self._include_base_check_box.toggled.connect(self._base_include_label.setEnabled)
        self._include_base_check_box.toggled.connect(self._base_include_line_edit.setEnabled)

        self.registerField('comment', comment_check_box)
        self.registerField('protect', protect_check_box)
        self.registerField('macroName', self._macro_name_line_edit)
        self.registerField('includeBase', self._include_base_check_box)
        self.registerField('baseInclude', self._base_include_line_edit)

        layout = QtWidgets.QGridLayout()
        layout.setColumnMinimumWidth(0, 20)
        layout.addWidget(comment_check_box, 0, 0, 1, 3)
        layout.addWidget(protect_check_box, 1, 0, 1, 3)
        layout.addWidget(macro_name_label, 2, 1)
        layout.addWidget(self._macro_name_line_edit, 2, 2)
        layout.addWidget(self._include_base_check_box, 3, 0, 1, 3)
        layout.addWidget(self._base_include_label, 4, 1)
        layout.addWidget(self._base_include_line_edit, 4, 2)
        self.setLayout(layout)

    def initializePage(self):
        class_name = self.field('className')
        self._macro_name_line_edit.setText(class_name.upper() + "_H")

        base_class = self.field('baseClass')
        is_baseClass = bool(base_class)

        self._include_base_check_box.setChecked(is_baseClass)
        self._include_base_check_box.setEnabled(is_baseClass)
        self._base_include_label.setEnabled(is_baseClass)
        self._base_include_line_edit.setEnabled(is_baseClass)

        if not is_baseClass:
            self._base_include_line_edit.clear()
        elif QtCore.QRegularExpression('^Q[A-Z].*$').match(base_class).hasMatch():
            self._base_include_line_edit.setText('<' + base_class + '>')
        else:
            self._base_include_line_edit.setText('"' + base_class.lower() + '.h"')


class OutputFilesPage(QtWidgets.QWizardPage):
    def __init__(self, parent=None):
        super(OutputFilesPage, self).__init__(parent)

        self.setTitle("Output Files")
        self.setSubTitle("Specify where you want the wizard to put the "
                "generated skeleton code.")
        self.setPixmap(QtWidgets.QWizard.LogoPixmap,
                QtGui.QPixmap(':/images/logo3.png'))

        output_dir_label = QtWidgets.QLabel("&Output directory:")
        self._output_dir_line_edit = QtWidgets.QLineEdit()
        output_dir_label.setBuddy(self._output_dir_line_edit)

        header_label = QtWidgets.QLabel("&Header file name:")
        self._header_line_edit = QtWidgets.QLineEdit()
        header_label.setBuddy(self._header_line_edit)

        implementation_label = QtWidgets.QLabel("&Implementation file name:")
        self._implementation_line_edit = QtWidgets.QLineEdit()
        implementation_label.setBuddy(self._implementation_line_edit)

        self.registerField('outputDir*', self._output_dir_line_edit)
        self.registerField('header*', self._header_line_edit)
        self.registerField('implementation*', self._implementation_line_edit)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(output_dir_label, 0, 0)
        layout.addWidget(self._output_dir_line_edit, 0, 1)
        layout.addWidget(header_label, 1, 0)
        layout.addWidget(self._header_line_edit, 1, 1)
        layout.addWidget(implementation_label, 2, 0)
        layout.addWidget(self._implementation_line_edit, 2, 1)
        self.setLayout(layout)

    def initializePage(self):
        class_name = self.field('className')
        self._header_line_edit.setText(class_name.lower() + '.h')
        self._implementation_line_edit.setText(class_name.lower() + '.cpp')
        self._output_dir_line_edit.setText(QtCore.QDir.toNativeSeparators(QtCore.QDir.tempPath()))


class ConclusionPage(QtWidgets.QWizardPage):
    def __init__(self, parent=None):
        super(ConclusionPage, self).__init__(parent)

        self.setTitle("Conclusion")
        self.setPixmap(QtWidgets.QWizard.WatermarkPixmap,
                QtGui.QPixmap(':/images/watermark2.png'))

        self.label = QtWidgets.QLabel()
        self.label.setWordWrap(True)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def initializePage(self):
        finish_text = self.wizard().buttonText(QtWidgets.QWizard.FinishButton)
        finish_text.replace('&', '')
        self.label.setText(f"Click {finish_text} to generate the class skeleton.")


if __name__ == '__main__':

    import sys

    app = QtWidgets.QApplication(sys.argv)
    wizard = ClassWizard()
    wizard.show()
    sys.exit(app.exec_())
