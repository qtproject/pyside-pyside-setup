Test a wheel
============

There is a tool that you can use to test a set of wheels called 'testwheel' but
it's currently in a different repository (``qt/qtqa``):

- Use ``scripts/packagetesting/testwheel.py`` from the
  `qtqa repository <https://code.qt.io/cgit/qt/qtqa.git>`_.

To test the wheels:

- Create a virtual environment and activate it.
- Install the dependencies listed on the ``requirements.txt`` file.
- Install all the wheels: ``shiboken6``, ``shiboken6-generator``,
  and ``PySide6-Essentials``.
- Run the ``testwheel`` tool.
- Install ``PySide6-Addons`` wheels.
- Run again the ``testwheel`` tool.
- In case you have access to commercial wheels, don't forget the
  ``PySide6-M2M`` as well, and re-run the ``testwheel`` tool.

Build on the command line
=========================

- Consider using ``build_scripts/qp5_tool.py``.

De-Virtualize the Python Files
==============================

The Python files in the Shiboken module are completely virtual, i.E.
they are nowhere existent in the file system for security reasons.

For debugging purposes or to change something, it might be desirable
to move these files into the normal file system, again.

- Setting the environment variable "SBK_EMBED" once to false unpacks these
  files when PySide6 or shiboken6 are imported. The files are written
  into "side-packages/shiboken6/files.dir" and are used from then on.

- Setting the variable to true removes "files.dir".

- Without the "SBK_EMBED" variable, the embedding status remains sticky.
