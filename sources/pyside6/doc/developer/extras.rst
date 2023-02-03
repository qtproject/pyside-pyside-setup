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
