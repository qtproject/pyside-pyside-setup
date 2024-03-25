.. _pyside6-project:

pyside6-project
===============

`pyside6-project` is a command line tool for creating, building and deploying
|project| applications. It operates on a project file which is also used by
`Qt Creator`_.

Project file format
-------------------

The project file format is a simple `JSON`_-based format with the suffix
``.pyproject`` listing all files of the project excluding generated files
(typically ``.py``, ``.qml``, ``.qrc``, ``.ts``, or ``.ui`` files):

.. code-block:: json

    {
        "files": ["main.py"]
    }


Usage
-----

The tool has several subcommands. New projects can be created using
the below commands, passing the project name (directory):

*new-ui*
    Creates a new QtWidgets project with a *Qt Widgets Designer*-based main
    window.

*new-widget*
    Creates a new QtWidgets project with a main window.

*new-quick*
    Creates a new QtQuick project.

The other commands take the project file as an argument.
It is also possible to specify a directory containing the project file.

*build*
    Builds the project, generating the required build artifacts
    (see :ref:`using_ui_files`, :ref:`using_qrc_files`).

*run*
    Builds the project and runs the main.

*deploy*
    Deploys the application (see see :ref:`pyside6-deploy`).

*lupdate*
    Updates translation (.ts) files (see :ref:`translations`).

*clean*
    Cleans the build artifacts.

*qmllint*
    Runs the ``qmllint`` tool, checking the QML files.


.. _`Qt Creator`: https://www.qt.io/product/development-tools
.. _`JSON`: https://www.json.org/
