.. _pyside6-lrelease:

pyside6-lrelease
================

.. note:: This tool is automatically called by :ref:`pyside6-project`
   so you don't need to call it manually. *Qt Creator* will take care
   of this step as well while executing a project.

``pyside6-lrelease`` is a command line tool wrapping `lrelease`_. It produces
``.qm`` files out of ``.ts`` files. The ``.qm`` file format is a compact binary
format that the localized application uses. It provides extremely fast lookup
for translations (see :ref:`translations`).

Usage
-----

To convert a ``.ts`` file of the :ref:`qt-linguist-example`
into its binary representation, run:

.. code-block:: bash

    pyside6-lrelease example_de.ts -qm example_de.qm

.. _`lrelease`: https://doc.qt.io/qt-6/linguist-lrelease.html
