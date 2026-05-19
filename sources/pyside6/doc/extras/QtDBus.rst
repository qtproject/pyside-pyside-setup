An introduction to Inter-Process Communication and Remote Procedure
Calling with D-Bus.

Introduction
^^^^^^^^^^^^

D-Bus is an Inter-Process Communication (IPC) and Remote Procedure
Calling (RPC) mechanism originally developed for Linux to replace
existing and competing IPC solutions with one unified protocol. It has
also been designed to allow communication between system-level
processes (such as printer and hardware driver services) and normal
user processes.

It uses a fast, binary message-passing protocol, which is suitable for
same-machine communication due to its low latency and low overhead.
Its specification is currently defined by the ``freedesktop.org``
project, and is available to all parties.

Communication in general happens through a central server application,
called the "bus" (hence the name), but direct
application-to-application communication is also possible. When
communicating on a bus, applications can query which other
applications and services are available, as well as activate one on
demand.

Using the Module
^^^^^^^^^^^^^^^^

To include the definitions of modules classes, use the following
directive:

::

    import PySide6.QtDBus


Articles and Guides
^^^^^^^^^^^^^^^^^^^

The following documents contain information about Qt's D-Bus integration
features, and provide details about the mechanisms used to send and receive
type information over the bus:

    * :ref:`Qt-D-Bus-Overview`
    * :ref:`Using-Qt-D-Bus-Adaptors`
    * :ref:`The-Qt-D-Bus-Type-System`
    * :ref:`Qt-D-Bus-XML-compiler--qdbusxml2cpp-`
    * :ref:`Qt-D-Bus-Viewer`
