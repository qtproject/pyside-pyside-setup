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

.. grid:: 1 3 3 3
    :gutter: 2

    .. grid-item-card::
        :class-item: text-center

        Install and build from source.
        +++
        .. button-ref:: gettingstarted
            :color: primary
            :outline:
            :expand:

            Getting Started

    .. grid-item-card::
        :class-item: text-center

        Binding generator executable.
        +++
        .. button-ref:: shibokengenerator
            :color: primary
            :outline:
            :expand:

            Shiboken Generator

    .. grid-item-card::
        :class-item: text-center

        Python utility module.
        +++
        .. button-ref:: shibokenmodule
            :color: primary
            :outline:
            :expand:

            Shiboken Module

    .. grid-item-card::
        :class-item: text-center

        Reference and functionallities.
        +++
        .. button-ref:: typesystem
            :color: primary
            :outline:
            :expand:

            Type System

    .. grid-item-card::
        :class-item: text-center

        Using Shiboken.
        +++
        .. button-ref:: examples/index
            :color: primary
            :outline:
            :expand:

            Examples

    .. grid-item-card::
        :class-item: text-center

        Known issues and FAQ.
        +++
        .. button-ref:: considerations
            :color: primary
            :outline:
            :expand:

            Considerations

.. toctree::
   :hidden:
   :glob:

   gettingstarted.rst
   shibokengenerator.rst
   shibokenmodule.rst
   typesystem.rst
   examples/index.rst
   considerations.rst
