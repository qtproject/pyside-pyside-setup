|project|
*********

.. ifconfig:: output_format == 'html'

    **Qt for Python** offers the official Python bindings for `Qt`_, and
    has two main components:

    * `PySide6`_, so that you can use Qt6 APIs in your Python applications, and
    * `Shiboken6 <shiboken6/index.html>`__, a binding generator tool, which can
      be used to expose C++ projects to Python, and a Python module with
      some utility functions.

.. ifconfig:: output_format == 'qthelp'

    **Qt for Python** offers the official Python bindings for `Qt`_, and
    has two main components:

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
.. _`Porting from PySide2 to PySide6`: porting_from2.html



Documentation
=============

.. panels::
    :body: align-items-center jutify-content-center text-center
    :container: container-lg pb-3
    :column: col-lg-4 col-md-4 col-sm-6 col-xs-12 p-2
    :img-top-cls: d-flex align-self-center img-responsive card-img-top-main

    :img-top: images/Desktop.svg

    Write your first Qt application.

    +++

    .. link-button:: quickstart
        :type: ref
        :text: Check it out!
        :classes: btn-qt btn-block stretched-link
    ---
    :img-top: images/Support.svg

    Install and build from source.

    +++

    .. link-button:: gettingstarted
        :type: ref
        :text: Getting Started
        :classes: btn-qt btn-block stretched-link
    ---
    :img-top: images/Dev.svg

    PySide API reference.

    +++

    .. link-button:: api
        :type: ref
        :text: API Docs
        :classes: btn-qt btn-block stretched-link

    ---
    :img-top: images/Tutorials.svg

    Learn with step-by-step guides.

    +++

    .. link-button:: tutorials/index
        :type: ref
        :text: Tutorials
        :classes: btn-qt btn-block stretched-link
    ---
    :img-top: images/Examples.svg

    Check all the available examples.

    +++

    .. link-button:: examples/index
        :type: ref
        :text: Examples
        :classes: btn-qt btn-block stretched-link
    ---
    :img-top: images/Training.svg

    Watch webinars, talks, and more.

    +++

    .. link-button:: videos
        :type: ref
        :text: Videos
        :classes: btn-qt btn-block stretched-link

    ---
    :img-top: images/Deployment.svg

    Learn to deploy your applications.

    +++

    .. link-button:: deployment-guides
        :type: ref
        :text: Deployment
        :classes: btn-qt btn-block stretched-link
    ---
    :img-top: images/stopwatch.svg

    API differences and known issues.

    +++

    .. link-button:: considerations
        :type: ref
        :text: Considerations
        :classes: btn-qt btn-block stretched-link
    ---
    :img-top: images/cpp_python.svg

    Generate C++ to Python bindings.

    +++

    .. link-button:: shiboken6/index.html
        :text: Shiboken
        :classes: btn-qt btn-block stretched-link


We have also a `wiki page`_ where you can find how to report bugs, contribute or contact the community.

.. _`wiki page`: https://wiki.qt.io/Qt_for_Python

.. toctree::
   :hidden:
   :glob:

   contents.rst
   gettingstarted*
   overviews/*
   feature-why
