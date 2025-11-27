.. _vscode-ext:

Qt Python VSCode Extension
**************************

The `Qt Python extension`_ for Visual Studio Code is a comprehensive development tool
that enhances your PySide6 development workflow with integrated debugging, project
templates, and build tasks.

Installation
============

Install the extension from the Visual Studio Code Marketplace:

1. Open VSCode
2. Go to the Extensions view
3. Search for "Qt Python"
4. Click Install on the extension published by **The Qt Company**

Alternatively, install from the command line:

.. code-block:: bash

    code --install-extension TheQtCompany.qt-python

Features
========

Project Creation
----------------

Create new PySide6 projects using templates:

1. Open the Command Palette
2. Type and select **Qt: Create a new Project or file**
3. Choose from available templates:

   * **Python QtQuick Application** - Creates a Qt Quick/QML project structure
   * **Python QtWidgets Application** - Creates a Qt Widgets project structure

PySide6 Installation
--------------------

Quickly install PySide6 in your current Python environment:

1. Open the Command Palette
2. Type and select **Qt-Python: Install PySide6**

Build Tasks
-----------

The extension provides PySide6-specific tasks accessible via **Tasks: Run Task**:

* **PySide: build** - Build your PySide6 project (compiles UI files, resources, etc.)
* **PySide: run** - Run your PySide6 application
* **PySide: clean** - Clean build artifacts
* **PySide: deploy** - Deploy your application using pyside6-deploy

Debugging
---------

The extension provides debugging capabilities for PySide6 applications with support
for both Python and QML code. See :ref:`tutorial_qml_debugging` for detailed information
on debugging Qt Quick applications with mixed Python/QML debugging.

Learn More
==========

For detailed documentation, feature updates, and usage instructions, visit the
`Qt Python extension marketplace page`_.

.. _`Qt Python extension`: https://marketplace.visualstudio.com/items?itemName=TheQtCompany.qt-python
.. _`Qt Python extension marketplace page`: https://marketplace.visualstudio.com/items?itemName=TheQtCompany.qt-python
