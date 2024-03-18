.. _pyside6-qmltyperegistrar:

pyside6-qmltyperegistrar
========================

``pyside6-qmltyperegistrar`` is a command line tool that wraps the
``qmltyperegistrar`` tool of Qt.

It takes the file produced by :ref:`pyside6-metaobjectdump`
as input and generates C++ code to register C++ classes to QML
and a ``.qmltypes`` file containing a JSON description of the
classes. For Qt for Python, only the ``.qmltypes`` file
is of interest as input for :ref:`pyside6-qmllint`.

The tool is automatically run by the :ref:`pyside6-project` tool
when passing the ``qmllint`` argument instructing it to check
the QML source files.
