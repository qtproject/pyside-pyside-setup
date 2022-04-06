Shiboken
********

.. ifconfig:: output_format == 'html'

   Shiboken is a fundamental piece on the `Qt for Python <../index.html>`__ project that serves two purposes:

.. ifconfig:: output_format == 'qthelp'

   Shiboken is a fundamental piece on the `Qt for Python <../pyside6/index.html>`__ project that serves two purposes:


* Generator_: Extract information from C or C++ headers and generate CPython_ code that allow
  to bring C or C++ projects to Python. This process uses a library called ApiExtractor_ which
  internally uses Clang_.
* Module_: An utility Python module that exposed new Python types, functions to handle pointers,
  among other things, that is written in CPython_ and can use independently of the generator.

.. _Generator: shibokengenerator.html
.. _Module: shibokenmodule.html
.. _CPython: https://github.com/python/cpython
.. _Clang: https://clang.llvm.org/
.. _ApiExtractor: typesystem.html

Documentation
=============

.. panels::
    :body: text-center
    :container: container-lg pb-3
    :column: col-lg-4 col-md-4 col-sm-6 col-xs-12 p-2

    Install and build from source.

    +++

    .. link-button:: gettingstarted
        :type: ref
        :text: Getting Started
        :classes: btn-qt btn-block stretched-link
    ---

    Binding generator executable.

    +++

    .. link-button:: shibokengenerator
        :type: ref
        :text: Shiboken Generator
        :classes: btn-qt btn-block stretched-link
    ---

    Python utility module.

    +++

    .. link-button:: shibokenmodule
        :type: ref
        :text: Shiboken Module
        :classes: btn-qt btn-block stretched-link

    ---

    Reference and functionallities.

    +++

    .. link-button:: typesystem
        :type: ref
        :text: Type System
        :classes: btn-qt btn-block stretched-link

    ---

    Using Shiboken.

    +++

    .. link-button:: examples/index
        :type: ref
        :text: Examples
        :classes: btn-qt btn-block stretched-link

    ---

    Known issues and FAQ.

    +++

    .. link-button:: considerations
        :type: ref
        :text: Considerations
        :classes: btn-qt btn-block stretched-link


.. toctree::
   :hidden:
   :glob:

   gettingstarted.rst
   shibokengenerator.rst
   shibokenmodule.rst
   typesystem.rst
   examples/index.rst
   considerations.rst
