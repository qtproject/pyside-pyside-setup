.. _pyside6-qmlimportscanner:

pyside6-qmlimportscanner
========================

``pyside6-qmlimportscanner`` is a command line tool that wraps the
``qmlimportscanner`` tool of Qt.


The tool is automatically run by the :ref:`pyside6-project` tool
when passing the ``qmllint`` argument instructing it to check
the QML source files.

Usage
-----

Invoking the tool in the directory of the :ref:`filesystemexplorer_example`
example using:

.. code-block:: bash

    pyside6-qmlimportscanner -rootPath .

produces:

.. code-block:: json

    [
        {
            "name": "QtQuick",
            "type": "module"
        },
        {
            "name": "QtQuick.Controls.Basic",
            "type": "module"
        },
        {
            "name": "QtQuick.Layouts",
            "type": "module"
        },
        {
            "name": "FileSystemModule",
            "type": "module"
        },
        {
            "name": "QtQuick.Controls",
            "type": "module"
        },
        {
            "name": "QtQuick.Effects",
            "type": "module"
        }
    ]
