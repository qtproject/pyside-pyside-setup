Provides functionality to create state machines from SCXML files.

The Qt SCXML module provides functionality to create state machines from
`SCXML <http://www.w3.org/TR/scxml/>`_ files. This includes both dynamically
creating state machines (loading the SCXML file and instantiating states and
transitions) and generating a C++ file that has a class implementing the state
machine. It also contains functionality to support data models and executable
content.

Getting Started
^^^^^^^^^^^^^^^

To include the definitions of modules classes, use the following
directive:

::

    import PySide6.QtScxml

Articles and Guides
^^^^^^^^^^^^^^^^^^^

    * `Qt SCXML Overview <https://doc.qt.io/qt-6/qtscxml-overview.html>`_
    * `Instantiating State Machines <https://doc.qt.io/qt-6/qtscxml-instantiating-state-machines.html>`_
    * `SCXML Compliance <https://doc.qt.io/qt-6/qtscxml-scxml-compliance.html>`_
