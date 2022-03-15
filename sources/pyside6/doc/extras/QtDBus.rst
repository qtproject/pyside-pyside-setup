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

The Buses
^^^^^^^^^

D-Bus buses are used when many-to-many communication is desired. In
order to achieve that, a central server is launched before any
applications can connect to the bus: this server is responsible for
keeping track of the applications that are connected and for properly
routing messages from their source to their destination.

In addition, D-Bus defines two well-known buses, called the system bus
and the session bus. These buses are special in the sense that they
have well-defined semantics: some services are defined to be found in
one or both of these buses.

For example, an application wishing to query the list of hardware
devices attached to the computer will probably communicate to a
service available on the system bus, while the service providing
opening of the user's web browser will probably be found on the
session bus.

On the system bus, one can also expect to find restrictions on what
services each application is allowed to offer. Therefore, one can be
reasonably certain that, if a certain service is present, it is being
offered by a trusted application.

Messages
^^^^^^^^

On the low level, applications communicate over D-Bus by sending
messages to one another. Messages are used to relay the remote
procedure calls as well as the replies and errors associated with
them. When used over a bus, messages have a destination, which means
they are routed only to the interested parties, avoiding congestion
due to "swarming" or broadcasting.

A special kind of message called a "signal message" (a concept based
on Qt's :ref:`Signals and Slots<Signals---Slots>` mechanism), however,
does not have a pre-defined destination. Since its purpose is to be
used in a one-to-many context, signal messages are designed to work
over an "opt-in" mechanism.

The Qt D-Bus module fully encapsulates the low-level concept of
messages into a simpler, object-oriented approach familiar to Qt
developers. In most cases, the developer need not worry about sending
or receiving messages.

Service Names
^^^^^^^^^^^^^

When communicating over a bus, applications obtain what is called a
"service name": it is how that application chooses to be known by
other applications on the same bus. The service names are brokered by
the D-Bus bus daemon and are used to route messages from one
application to another. An analogous concept to service names are IP
addresses and hostnames: a computer normally has one IP address and
may have one or more hostnames associated with it, according to the
services that it provides to the network.

On the other hand, if a bus is not used, service names are also not
used. If we compare this to a computer network again, this would
equate to a point-to-point network: since the peer is known, there is
no need to use hostnames to find it or its IP address.

The format of a D-Bus service name is in fact very similar to a host
name: it is a dot-separated sequence of letters and digits. The common
practice is even to name one's service name according to the domain
name of the organization that defined that service.

For example, the D-Bus service is defined by ``freedesktop.org`` and
can be found on the bus under the service name:

    ::

        org.freedesktop.DBus

Object Paths
^^^^^^^^^^^^

Like network hosts, applications provide specific services to other
applications by exporting objects. Those objects are hierarchically
organized, much like the parent-child relationship that classes
derived from :class:`QObject<PySide6.QtCore.QObject>` possess. One
difference, however, is that there is the concept of "root object",
which all objects have as the ultimate parent.

If we continue our analogy with Web services, object paths equate to
the path part of a URL.

Like them, object paths in D-Bus are formed resembling path names on
the filesystem: they are slash-separated labels, each consisting of
letters, digits and the underscore character ("\_"). They must always
start with a slash and must not end with one.

Interfaces
^^^^^^^^^^

Interfaces are similar to C++ abstract classes and Java's
``interface`` keyword and declare the "contract" that is established
between caller and callee. That is, they establish the names of the
methods, signals, and properties that are available as well as the
behavior that is expected from either side when communication is
established.

Qt uses a very similar mechanism in its Plugin system: Base classes in
C++ are associated with a unique identifier by way of the
:meth:`Q\_DECLARE\_INTERFACE()<~QtDBus.Q_DECLARE_INTERFACE>` macro.

D-Bus interface names are, in fact, named in a manner similar to what
is suggested by the Qt Plugin System: an identifier usually
constructed from the domain name of the entity that defined that
interface.

Cheat Sheet
^^^^^^^^^^^

To facilitate remembering of the naming formats and their purposes,
the following table can be used:

    +-------------+------------------+---------------------------------------+
    |D-Bus Concept|Analogy           |Name format                            |
    +-------------+------------------+---------------------------------------+
    |Service name |Network hostnames |Dot-separated ("looks like a hostname")|
    +-------------+------------------+---------------------------------------+
    |Object path  |URL path component|Slash-separated ("looks like a path")  |
    +-------------+------------------+---------------------------------------+
    |Interface    |Plugin identifier |Dot-separated                          |
    +-------------+------------------+---------------------------------------+

Debugging
^^^^^^^^^

When developing applications that use D-Bus, it is sometimes useful to
be able to see information about the messages that are sent and
received across the bus by each application.

This feature can be enabled on a per-application basis by setting the
``QDBUS_DEBUG`` environment variable before running each application.
For example, we can enable debugging only for the car in the
:ref:`D-Bus Remote Controlled Car
Example<D-Bus-Remote-Controlled-Car-Example>` by running the
controller and the car in the following way:

    ::

        QDBUS_DEBUG=1 python examples/dbus/pingpong/pong.py

Information about the messages will be written to the console the
application was launched from.

Using the Module
^^^^^^^^^^^^^^^^

To include the definitions of modules classes, use the following
directive:

::

    import PySide6.QtDBus

Further Reading
^^^^^^^^^^^^^^^

The following documents contain information about Qt's D-Bus integration features, and provide details about the mechanisms used to send and receive type information over the bus:

    * `Using Qt D-Bus Adaptors <https://doc.qt.io/qt-6/usingadaptors.html>`_
    * `The Qt D-Bus Type System <https://doc.qt.io/qt-6/qdbustypesystem.html>`_
    * `Qt D-Bus XML compiler (qdbusxml2cpp) <https://doc.qt.io/qt-6/qdbusxml2cpp.html>`_
    * `D-Bus Viewer <https://doc.qt.io/qt-6/qdbusviewer.html>`_
