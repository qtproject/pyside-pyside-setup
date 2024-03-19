.. _pyside6-lupdate:

pyside6-lupdate
===============

.. note:: This tool is automatically called by :ref:`pyside6-project`
   so you don't need to call it manually.

``pyside6-lupdate`` is a command line tool wrapping `lupdate`_. It finds
translatable strings in Python, ``.ui``, and ``.qml`` files and generates or
updates ``.ts`` files (see :ref:`translations`).

Usage
-----

To create or update the ``.ts`` file of the :ref:`qt-linguist-example`,
run:

.. code-block:: bash

    pyside6-lupdate main.py main.qml form.ui -ts example_de.ts

.. _`lupdate`: https://doc.qt.io/qt-6/linguist-lupdate.html
