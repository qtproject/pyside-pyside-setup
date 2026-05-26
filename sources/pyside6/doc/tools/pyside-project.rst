.. _pyside6-project:

pyside6-project
===============

`pyside6-project` is a command line tool for creating, building and deploying
|project| applications. It operates on project files which are also supported
by `Qt Creator`_.

A project file contains a list of the source files used in the project. Typically they are
``.py``, ``.qml``, ``.qrc``, ``.ts``, or ``.ui`` files. It can also include other subproject files.
Generated files such as compiled resources or compiled translations should not be included in the
project file.

Currently, two project file formats are supported. Since PySide6 version 6.9.0, the ``*.pyproject``
file format is deprecated in favor of the new ``pyproject.toml`` file format. The ``*.pyproject``
file format is still supported for backward compatibility, but it is recommended to migrate to the
new ``pyproject.toml`` file format. See
:ref:`Migrating from *.pyproject to pyproject.toml<migrating_from_pyproject_to_pyproject_toml>`
for more information.

``pyproject.toml``
------------------

PySide6 version 6.9.0 added support for the new Python standard ``pyproject.toml`` project file
format. It is intended to replace the deprecated ``*.pyproject`` file format. The project source
files are listed in the ``tool.pyside6-project`` table. For example:

.. code-block:: toml

    [project]
    name = "myproject"

    [tool.pyside6-project]
    files = ["main.py", "main_window.py"]

It is also possible to specify options for the :ref:`pyside6-rcc` and
:ref:`pyside6-uic` tools:

.. code-block:: toml

    [tool.pyside6-rcc]
    options = ["--compress-algo", "zlib"]

    [tool.pyside6-uic]
    options = [" --star-imports"]

More information about the ``pyproject.toml`` file format can be found in
`Python Packaging User Guide specification: "Writing your pyproject.toml"`_.

``*.pyproject``
---------------

The deprecated ``*.pyproject`` project file uses a simple `JSON`_-based format. The source files
are listed in the ``files`` array of the JSON root object. For example:

.. code-block:: json

    {
        "files": ["main.py", "main_window.py"]
    }

Usage
-----

The tool has several subcommands. New projects can be created using
the below commands, passing the project name (directory):

*new-ui*
    Creates a new QtWidgets project with a *Qt Widgets Designer*-based main window.

*new-widget*
    Creates a new QtWidgets project with a main window.

*new-quick*
    Creates a new QtQuick project.

Using the optional ``--legacy-pyproject`` flag, the tool will create a legacy ``.pyproject`` file
instead of a ``pyproject.toml`` file.

The following commands can receive a project file as an optional argument.
It is also possible to specify a directory containing the project file.

*build*
    Builds the project. Compiles resources, UI files, and QML files if existing and necessary.
    (see :ref:`tutorial_uifiles`, :ref:`tutorial_qrcfiles`).

*run*
    Builds the project and runs the main. Additional command line arguments
    can be passed following the project file argument.

*deploy*
    Deploys the application (see see :ref:`pyside6-deploy`).

*lupdate*
    Updates translation (.ts) files (see :ref:`tutorial_translations`).

*clean*
    Cleans the build artifacts. For example, compiled resources.

*qmllint*
    Runs the ``qmllint`` tool, checking the QML files.

*migrate-pyproject*
    Migrates the content of one or more ``*.pyproject`` files to a ``pyproject.toml`` file.
    See :ref:`migrating_from_pyproject_to_pyproject_toml`.

Considerations
--------------

For each file entry in the project files, ``pyside6-project`` does the following:

  * ``<other project file>``: Recursively handle subproject
  * ``<name>.qrc``: Runs the resource compiler to create a file rc_<name>.py
  * ``<name>.ui``: Runs the user interface compiler to create a file ui_<name>.py

For a Python file declaring a QML module, a directory matching the URI is
created and populated with .qmltypes and qmldir files for use by code analysis
tools. Currently, only one QML module consisting of several classes can be
handled per project file.

.. _migrating_from_pyproject_to_pyproject_toml:

Migrating from ``*.pyproject`` to ``pyproject.toml``
----------------------------------------------------

Since PySide6 6.9.0, ``pyside6-project`` tool can create a new ``pyproject.toml`` file or update an
existing one with the existing ``*.pyproject`` file content. To migrate an existing project, run
``pyside6-project`` command with the ``migrate-pyproject`` argument. For example:

.. code-block:: bash

    pyside6-project migrate-pyproject

If no file is specified, the tool will read the ``*.pyproject`` files in the current working
directory. In the case of having multiple ``*.pyproject`` files in the same directory, its contents
will be merged. A new ``pyproject.toml`` file will be created if not existing. If the file already
exists, a confirmation message is displayed to the user asking for confirmation before
updating the file with the new content. For example:

.. code-block:: bash

    mkdir myproject
    cd myproject
    echo {"files": ["main.py", "my_widget.py"]} > myproject.pyproject
    pyside6-project migrate-pyproject

Generated pyproject.toml file:

.. code-block:: toml

    [project]
    name = "myproject"

    [tool.pyside6-project]
    files = ["main.py", "my_widget.py"]

.. _`Qt Creator`: https://www.qt.io/product/development-tools
.. _`Python Packaging User Guide specification: "Writing your pyproject.toml"`: https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
.. _`JSON`: https://www.json.org/
