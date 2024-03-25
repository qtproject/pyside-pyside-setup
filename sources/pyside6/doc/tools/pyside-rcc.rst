.. _pyside6-rcc:

pyside6-rcc
===========

.. note:: This tool is automatically called by :ref:`pyside6-project`
   so you don't need to call it manually. *Qt Creator* will take care
   of this step as well while executing a project.


``pyside6-rcc`` is a command line tool for converting ``.qrc`` files into ``.py``
files, so they can be used within your Python code.

The tool is a wrapper around the `rcc`_ tool, which was originally
designed to generate C++ code, but it also has Python support.

Even though the equivalent of ``pyside6-rcc`` is running ``rcc -g python``
we strongly recommend you to rely on ``pyside6-rcc`` in order to avoid
mismatches between versions for the generated code.

Usage
-----

Once you have gathered your resources on a qrc file,
you can transform your ``.qrc`` file with the following command:

.. code-block:: bash

    pyside6-rcc your_file.qrc -o rc_your_file.py

It is important to use the ``-o`` option to generate the Python file with the
conversion, otherwise you will receive all the output as stdout in your terminal.

To enable the usage of those resources in your program, you need to import
the file:

.. code-block:: Python

    import rc_your_file

then you can use a specific resource, for example an image, with the prefix ``:/``,
for example:

.. code-block:: Python

    pixmap = QPixmap(":/icons/image.png")


For additional options, you can use ``pyside6-rcc -h`` in order to get
more information about additional options.

Visit the tutorial :ref:`using_qrc_files` for a hands-on example.

.. _`rcc`: https://doc.qt.io/qt-6/rcc.html

