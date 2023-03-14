|project|
*********

.. ifconfig:: output_format == 'html'

    **Qt for Python** offers the official Python bindings for `Qt`_,
    which enables you to use Python to write your Qt applications.
    The project has two main components:

    * `PySide6`_, so that you can use Qt6 APIs in your Python applications, and
    * `Shiboken6 <shiboken6/index.html>`__, a binding generator tool, which can
      be used to expose C++ projects to Python, and a Python module with
      some utility functions.

.. ifconfig:: output_format == 'qthelp'

    **Qt for Python** offers the official Python bindings for `Qt`_,
    which enables you to use Python to write your Qt applications.
    The project has two main components:

    * `PySide6`_, so that you can use Qt6 APIs in your Python applications, and
    * `Shiboken6 <../shiboken6/index.html>`__, a binding generator tool, which can
      be used to expose C++ projects to Python, and a Python module with
      some utility functions.

`Porting from PySide2 to PySide6`_ provides information on porting existing PySide2
applications.

This project is available under the LGPLv3/GPLv3 and the `Qt commercial license`_.

.. _Qt: https://doc.qt.io
.. _PySide6: quickstart.html
.. _`Qt commercial license`: https://www.qt.io/licensing/
.. _`Porting from PySide2 to PySide6`: gettingstarted/porting_from2.html

Quick Start
===========

You can obtain the latest stable version by running ``pip install pyside6``.
If you want to build it yourself, check the `getting started guide`_.

To learn how to use it, check out `write your first application`_,
and to learn what is installed with the ``pyside6``, check the
`package content, structure, and tools`_ page.


.. _`getting started guide`: gettingstarted/index.html
.. _`write your first application`: quickstart.html
.. _`package content, structure, and tools`: gettingstarted/package_details.html

Documentation
=============

.. grid:: 1 3 3 3
    :gutter: 2

    .. grid-item-card::
        :img-top: images/Desktop.svg
        :class-item: text-center

        Write your first Qt application.
        +++
        .. button-ref:: quick-start
            :color: primary
            :outline:
            :expand:

            Start here!

    .. grid-item-card::
        :img-top: images/Support.svg
        :class-item: text-center

        Modules, docs, and cross compilation.
        +++
        .. button-ref:: gettingstarted/index
            :color: primary
            :outline:
            :expand:

            Build Instructions

    .. grid-item-card::
        :img-top: images/Commercial.svg
        :class-item: text-center

        Packages, installation, and details.
        +++
        .. button-ref:: commercial-page
            :color: primary
            :outline:
            :expand:

            Commercial

    .. grid-item-card::
        :img-top: images/Dev.svg
        :class-item: text-center

        PySide API reference.
        +++
        .. button-ref:: api
            :color: primary
            :outline:
            :expand:

            API Docs

    .. grid-item-card::
        :img-top: images/Tutorials.svg
        :class-item: text-center

        Learn with step-by-step guides.
        +++
        .. button-ref:: tutorials/index
            :color: primary
            :outline:
            :expand:

            Tutorials

    .. grid-item-card::
        :img-top: images/Examples.svg
        :class-item: text-center

        Check all the available examples.
        +++
        .. button-ref:: examples/index
            :color: primary
            :outline:
            :expand:

            Examples

    .. grid-item-card::
        :img-top: images/Training.svg
        :class-item: text-center

        Watch webinars, talks, and more.
        +++
        .. button-ref:: videos
            :color: primary
            :outline:
            :expand:

            Videos

    .. grid-item-card::
        :img-top: images/Deployment.svg
        :class-item: text-center

        Learn to deploy your applications.
        +++
        .. button-ref:: deployment-guides
            :color: primary
            :outline:
            :expand:

            Deployment

    .. grid-item-card::
        :img-top: images/cpp_python.svg
        :class-item: text-center

        Generate C++ to Python bindings.
        +++
        .. button-link:: shiboken6/index.html
            :color: primary
            :outline:
            :expand:

            Shiboken

    .. grid-item-card::
        :img-top: images/stopwatch.svg
        :class-item: text-center

        API differences and known issues.
        +++
        .. button-ref:: considerations
            :color: primary
            :outline:
            :expand:

            Considerations

    .. grid-item-card::
        :img-top: images/Development.svg
        :class-item: text-center

        Notes for Developers.
        +++
        .. button-ref:: developer-notes
            :color: primary
            :outline:
            :expand:

            Developers


We have also a `wiki page`_ where you can find how to report bugs, contribute or contact the community.

.. _`wiki page`: https://wiki.qt.io/Qt_for_Python

.. toctree::
   :hidden:
   :glob:

   contents.rst
