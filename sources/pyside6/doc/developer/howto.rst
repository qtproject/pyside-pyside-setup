.. _developer-howto:

***************
Developer HOWTO
***************

Add a new module
================

Add bindings
------------

- Find the correct name (look at the include path of Qt).
- Add it to ``sources/pyside6/cmake/PySideHelpers.cmake``.
- Add it to ``build_scripts/wheel_files.py`` (plugins, translations).
- Copy an existing module to ``sources/pyside6/PySide6/<name>``.
- Adapt the ``typesystem.xml`` and ``CMakeList.txt`` (using for example
  Qt Creator's case-preserving replace function).
- Make sure the dependencies are correct.
- Find the exported public classes, add them to the ``typesystem.xml`` file,
  checking whether they are ``value-type`` or ``object-type``. Add their enums
  and flags.
- Add the wrapper files to ``CMakeList.txt``.
- Create a test dir under ``sources/pyside6/tests`` with an empty
  ``CMakeList.txt``.
- Try to build with the module added to the ``--module-subset`` option of
  ``setup.py``.
- Watch out for shiboken warnings in the log.
- Be aware that ``ninja`` mixes stdout and stderr, so, the first warning is
  typically hidden behind a progress message.
- A convenient way of doing this is using
  ``qt-creator/scripts/shiboken2tasks.py`` from the
  `Qt Creator repository <https://code.qt.io/cgit/qt-creator/qt-creator.git>`_
  converting them to a ``.tasks`` file which can be loaded into Qt Creator's
  issue pane.
- Link errors may manifest when ``generate_pyi`` imports the module trying
  to create signatures. They indicate a missing source file entry
  or a bug in the module itself.

.. note:: For the build to succeed, the module must follow the Qt convention
   of using ``#include <QtModule/header.h>`` since module include paths
   are not passed in PySide.

Add documentation
-----------------

- Add entry to ``sources/pyside6/doc/modules.rst``.
- Add a .qdocconf.in file in ``sources/pyside6/doc/qtmodules``.
- Add module description ``.rst`` file in ``sources/pyside6/doc/extras``.

Port an example
===============

- Quickly check the C++ example, fix outdated code.
- Port the sources using ``tools/tools/qtcpp2py.py`` (front-end for
  ``snippets-translate``).
- Note that our examples need to have unique names due to the doc build.
- Verify that all slots are decorated using ``@Slot``.
- Add a ``.pyproject`` file (verify later on that docs build).
- Add a ``doc`` directory and descriptive ``.rst`` file,
  and a screenshot if suitable (use ``optipng`` to reduce file size).
- Add the """Port of the ... example from Qt 6""" doc string.
- Try to port variable and function names to snake case convention.
- Verify that a flake check is mostly silent.
- Remove C++ documentation from ``sources/pyside6/doc/additionaldocs.lst``.

Add a tool
==========

- Add script and optional library under ``sources/pyside-tools``.
- Install the files (``sources/pyside-tools/CMakeLists.txt``).
- Add an entry point in ``build_scripts/config.py``.
- Copy the files to the wheels in ``build_scripts/platforms/*.py``.
- Add an entry to ``sources/pyside6/doc/package_details.rst``.
- Add an entry to ``create_wheels.py``.
- Build with ``--standalone``, verify it is working.

Test a wheel
============

- Use ``scripts/packagetesting/testwheel.py`` from the
  `qtqa repository <https://code.qt.io/cgit/qt/qtqa.git>`_.

Build on the command line
=========================

- Consider using ``build_scripts/qp5_tool.py``.
