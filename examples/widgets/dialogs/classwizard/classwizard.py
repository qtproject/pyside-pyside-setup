#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited.
## Copyright (C) 2021 The Qt Company Ltd.
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

import os
from pathlib import Path
import sys

from PySide6.QtCore import (QByteArray, QDir, QFile, QFileInfo,
                            QRegularExpression, Qt, QUrl, Slot)
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtWidgets import (QApplication, QComboBox, QCheckBox, QFormLayout,
                               QFileDialog, QGroupBox, QGridLayout,
                               QHBoxLayout, QLabel, QLineEdit, QMessageBox,
                               QPushButton, QRadioButton, QToolButton,
                               QVBoxLayout, QWizard, QWizardPage)

from listchooser import ListChooser, PropertyChooser, SignalChooser

import classwizard_rc


BASE_CLASSES = ['<None>', 'PySide6.QtCore.QObject',
                'PySide6.QtWidgets.QDialog', 'PySide6.QtWidgets.QMainWindow',
                'PySide6.QtWidgets.QWidget']


PYTHON_TYPES = ['int', 'list', 'str']


INTRODUCTION = ("This wizard will generate a skeleton Python class definition, "
                "including a few functions. You simply need to specify the class name and set "
                "a few options to produce a Python file.")


def property_accessors(property_type, name):
    """Generate the property accessor functions."""
    return (f'    @Property({property_type})\n'
            f'    def {name}(self):\n'
            f'        return self._{name}\n\n'
            f'    @{name}.setter\n'
            f'    def {name}(self, value):\n'
            f'        self._{name} = value\n')


def property_initialization(property_type, name):
    """Generate the property initialization for __init__()."""
    return f'        self._{name} = {property_type}()\n'


def signal_initialization(signature):
    """Generate the Signal initialization from the function signature."""
    paren_pos = signature.find('(')
    name = signature[:paren_pos]
    parameters = signature[paren_pos:]
    return f'    {name} = Signal{parameters}\n'


class ClassWizard(QWizard):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.addPage(IntroPage())
        self._class_info_index = self.addPage(ClassInfoPage())
        self._qobject_index = self.addPage(QObjectPage())
        self._output_index = self.addPage(OutputFilesPage())
        self.addPage(ConclusionPage())

        self.setPixmap(QWizard.BannerPixmap,
                       QPixmap(':/images/banner.png'))
        self.setPixmap(QWizard.BackgroundPixmap,
                       QPixmap(':/images/background.png'))

        self.setWindowTitle("Class Wizard")

    def nextId(self):
        """Overrides QWizard.nextId() to insert the property/signal
           page in case the class is a QObject."""
        idx = self.currentId()
        if self.currentId() == self._class_info_index:
            qobject = self.field('qobject')
            return self._qobject_index if qobject else self._output_index
        return super(ClassWizard, self).nextId()

    def generate_code(self):
        imports = []  # Classes to be imported
        module_imports = {}  # Module->class list

        def add_import(class_str):
            """Add a class to the import list or module hash depending on
               whether it is 'class' or 'module.class'. Returns the
               class name."""
            dot = class_str.rfind('.')
            if dot < 0:
                imports.append(class_str)
                return class_str
            module = class_str[0:dot]
            class_name = class_str[dot + 1:]
            class_list = module_imports.get(module)
            if class_list:
                if class_name not in class_list:
                    class_list.append(class_name)
            else:
                module_imports[module] = [class_name]
            return class_name

        class_name = self.field('className')
        qobject = self.field('qobject')
        base_class = self.field('baseClass')
        if base_class.startswith('<'):  # <None>
            base_class = ''
        if qobject and not base_class:
            base_class = 'PySide6.QtCore.QObject'

        if base_class:
            base_class = add_import(base_class)

        signals = self.field('signals')
        if signals:
            add_import('PySide6.QtCore.Signal')

        property_types = []
        property_names = []
        for p in self.field('properties'):
            property_type, property_name = str(p).split(' ')
            if property_type not in PYTHON_TYPES:
                property_type = add_import(property_type)
            property_types.append(property_type)
            property_names.append(property_name)

        if property_names:
            add_import('PySide6.QtCore.Property')

        signals = self.field('signals')
        if signals:
            add_import('PySide6.QtCore.Signal')

        property_types = []
        property_names = []
        for p in self.field('properties'):
            property_type, property_name = str(p).split(' ')
            if property_type not in PYTHON_TYPES:
                property_type = add_import(property_type)
            property_types.append(property_type)
            property_names.append(property_name)

        if property_names:
            add_import('PySide6.QtCore.Property')

        # Generate imports
        block = '# This Python file uses the following encoding: utf-8\n\n'
        for module, class_list in module_imports.items():
            class_list.sort()
            class_list_str = ', '.join(class_list)
            block += f'from {module} import {class_list_str}\n'
        for klass in imports:
            block += f'import {klass}\n'

        # Generate class definition
        block += f'\n\nclass {class_name}'
        if base_class:
            block += f'({base_class})'
        block += ':\n'
        description = self.field('description')
        if description:
            block += f'    """{description}"""\n'

        if signals:
            block += '\n'
            for s in signals:
                block += signal_initialization(str(s))

        # Generate __init__ function
        block += '\n    def __init__(self'
        if qobject:
            block += ', parent=None'
        block += '):\n'

        if base_class:
            block += f'        super().__init__('
            if qobject:
                block += 'parent'
            block += ')\n'

        for i, name in enumerate(property_names):
            block += property_initialization(property_types[i], name)

        if not base_class and not property_names:
            block += '        pass\n'

        # Generate property accessors
        for i, name in enumerate(property_names):
            block += '\n' + property_accessors(property_types[i], name)

        return block

    def accept(self):
        file_name = self.field('file')
        output_dir = self.field('outputDir')
        python_file = Path(output_dir) / file_name
        name = os.fspath(python_file)
        try:
            python_file.write_text(self.generate_code())
        except (OSError, PermissionError) as e:
            reason = str(e)
            QMessageBox.warning(None, "Class Wizard",
                                f"Cannot write file {name}:\n{reason}")
            return

        if self.field('launch'):
            url = QUrl.fromLocalFile(QDir.fromNativeSeparators(name))
            QDesktopServices.openUrl(url)

        super(ClassWizard, self).accept()


class IntroPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Introduction")
        self.setPixmap(QWizard.WatermarkPixmap,
                       QPixmap(':/images/watermark1.png'))

        label = QLabel(INTRODUCTION)
        label.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.addWidget(label)


class ClassInfoPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Class Information")
        self.setSubTitle("Specify basic information about the class for "
                         "which you want to generate a skeleton source code file.")
        self.setPixmap(QWizard.LogoPixmap,
                       QPixmap(':/qt-project.org/logos/pysidelogo.png'))

        class_name_line_edit = QLineEdit()
        class_name_line_edit.setClearButtonEnabled(True)

        self._base_class_combo = QComboBox()
        self._base_class_combo.addItems(BASE_CLASSES)
        self._base_class_combo.setEditable(True)

        base_class_line_edit = self._base_class_combo.lineEdit()
        base_class_line_edit.setPlaceholderText('Module.Class')
        self._base_class_combo.currentTextChanged.connect(self._base_class_changed)

        description_line_edit = QLineEdit()
        description_line_edit.setClearButtonEnabled(True)

        self._qobject_check_box = QCheckBox("Inherits QObject")

        self.registerField('className*', class_name_line_edit)
        self.registerField('baseClass', base_class_line_edit)
        self.registerField('description', description_line_edit)
        self.registerField('qobject', self._qobject_check_box)

        layout = QFormLayout(self)
        layout.addRow("&Class name:", class_name_line_edit)
        layout.addRow("B&ase class:", self._base_class_combo)
        layout.addRow("&Description:", description_line_edit)
        layout.addRow(self._qobject_check_box)

    @Slot(str)
    def _base_class_changed(self, text):
        is_qobject = text.startswith('PySide')
        self._qobject_check_box.setChecked(is_qobject)


class QObjectPage(QWizardPage):
    """Allows for adding properties and signals to a QObject."""
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("QObject parameters")
        self.setSubTitle("Specify the signals, slots and properties.")
        self.setPixmap(QWizard.LogoPixmap,
                       ':/qt-project.org/logos/pysidelogo.png')
        layout = QVBoxLayout(self)
        self._properties_chooser = PropertyChooser()
        self.registerField('properties', self._properties_chooser, 'items')
        layout.addWidget(self._properties_chooser)
        self._signals_chooser = SignalChooser()
        self.registerField('signals', self._signals_chooser, 'items')
        layout.addWidget(self._signals_chooser)


class OutputFilesPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Output Files")
        self.setSubTitle("Specify where you want the wizard to put the "
                         "generated skeleton code.")
        self.setPixmap(QWizard.LogoPixmap,
                       QPixmap(':/qt-project.org/logos/pysidelogo.png'))

        output_dir_label = QLabel("&Output directory:")
        output_dir_layout = QHBoxLayout()
        self._output_dir_line_edit = QLineEdit()
        output_dir_layout.addWidget(self._output_dir_line_edit)
        output_dir_label.setBuddy(self._output_dir_line_edit)
        output_dir_button = QToolButton()
        output_dir_button.setText('...')
        output_dir_button.clicked.connect(self._choose_output_dir)
        output_dir_layout.addWidget(output_dir_button)

        self._file_line_edit = QLineEdit()

        self.registerField('outputDir*', self._output_dir_line_edit)
        self.registerField('file*', self._file_line_edit)

        layout = QFormLayout(self)
        layout.addRow(output_dir_label, output_dir_layout)
        layout.addRow("&File name:", self._file_line_edit)

    def initializePage(self):
        class_name = self.field('className')
        self._file_line_edit.setText(class_name.lower() + '.py')
        self.set_output_dir(QDir.tempPath())

    def set_output_dir(self, directory):
        self._output_dir_line_edit.setText(QDir.toNativeSeparators(directory))

    def output_dir(self):
        return QDir.fromNativeSeparators(self._output_dir_line_edit.text())

    def file_name(self):
        return f"{self.output_dir()}/{self._file_line_edit.text()}"

    def _choose_output_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Output Directory",
                                               self.output_dir())
        if directory:
            self.set_output_dir(directory)

    def validatePage(self):
        """Ensure we do not overwrite existing files."""
        name = self.file_name()
        if QFileInfo.exists(name):
            question = f'{name} already exists. Would you like to overwrite it?'
            r = QMessageBox.question(self, 'File Exists', question)
            if r != QMessageBox.Yes:
                return False
        return True


class ConclusionPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Conclusion")
        self.setPixmap(QWizard.WatermarkPixmap,
                       QPixmap(':/images/watermark1.png'))

        self.label = QLabel()
        self.label.setWordWrap(True)

        self._launch_check_box = QCheckBox("Launch")
        self.registerField('launch', self._launch_check_box)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self._launch_check_box)

    def initializePage(self):
        finish_text = self.wizard().buttonText(QWizard.FinishButton)
        finish_text = finish_text.replace('&', '')
        self.label.setText(f"Click {finish_text} to generate the class skeleton.")
        self._launch_check_box.setChecked(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wizard = ClassWizard()
    wizard.show()
    sys.exit(app.exec())
