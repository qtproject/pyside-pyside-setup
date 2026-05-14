.. _Security-Considerations:

Security Considerations
=======================

This page lists some topics relevant in context of the upcoming
`CRA`_ regulation in the EU.

Deployment
----------

Getting your projects installed on other computers or people is a task most
Python developers would face at some point. When trying a local copy of the
Python files, you need to be certain that the source code hasn't been tampered
with or maliciously modified. For that reason, we recommend that, for the
distribution of PySide projects, you always deploy them. Please check our
section on :ref:`deployment-guides`, where you can find how to do this using
:ref:`pyside6-deploy` or other tools.

The Python Interpreter
----------------------

The `CRA`_ does not include the Python interpreter, since that would be
`very problematic`_\, but there is an exception for non-commercial
Open Source software. Because of that, the security scope of Qt for Python
as an offering does not include the interpreter the applications are using.

Security-relevant Topics in Qt for Python
-----------------------------------------

* `Shiboken.VoidPtr`_
* :func:`PySide6.QtUiTools.loadUiType`
* :ref:`Qt Widgets Designer Custom Widgets<designer-tool-custom-widgets>`

Security in Qt
--------------

* :ref:`Security-in-Qt`
* :ref:`Qt-Shared-Security-Model`
* :ref:`overviews_untrusted-data`

.. _`Shiboken.VoidPtr`: https://doc.qt.io/qtforpython-6/shiboken6/shibokenmodule.html#Shiboken.VoidPtr
.. _`CRA`: https://www.qt.io/cyber-resilience-act
.. _`very problematic`: https://pyfound.blogspot.com/2023/04/the-eus-proposed-cra-law-may-have.html
