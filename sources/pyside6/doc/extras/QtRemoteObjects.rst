Provides APIs for inter-process communication.

Remote Object Concepts
^^^^^^^^^^^^^^^^^^^^^^

Qt Remote Objects (QtRO) is an Inter-Process Communication (IPC) module
developed for Qt. This module extends Qt's existing functionalities to enable
information exchange between processes or computers, easily.

One of Qt's key features, to enable this information exchange, is the
distinction between an object's API (defined by its properties, signals, and
slots) and the implementation of that API. QtRO's purpose is to meet that
expected API, even if the true :class:`QObject<PySide6.QtCore.QObject>` is in a
different process. A slot called on a copy of an object (the
:ref:`Replica<Qt-Remote-Objects-Replica>` in QtRO) is forwarded to the true
object (the :ref:`Source<Qt-Remote-Objects-Source>` in QtRO) for handling.
Every Replica receives updates to the Source, either property changes or
emitted signals.

A :ref:`Replica<Qt-Remote-Objects-Replica>` is a light-weight proxy for the
:ref:`Source<Qt-Remote-Objects-Source>` object, but a Replica supports the same
connections and behavior of QObjects, which makes it usable in the same way as
any other :class:`QObject<PySide6.QtCore.QObject>` that Qt provides. Behind the
scenes, QtRO handles everything that's necessary for the Replica to look like
its Source.

Note that Remote Objects behave differently from traditional Remote Procedure
Call (RPC) implementations, for example:

    * In RPC, the client makes a request and waits for the response.
    * In RPC, the server doesn't push anything to the client unless it's in response to a request.
    * Often, the design of RPC is such that different clients are independent of each other:
      for instance, two clients can ask a mapping service for directions and get
      different results.

While it is possible to implement this RPC-style behavior in QtRO, as Sources
without properties, and slots that have return values, QtRO hides the fact that
the processing is really remote. You let a node give you the Replica instead of
creating it yourself, possibly use the status signals (
:meth:`isReplicaValid()<PySide6.QtRemoteObjects.QRemoteObjectReplica.isReplicaValid>`
), but then interact with the object like you would with any other
:class:`QObject<PySide6.QtCore.QObject>` -based type.

Use Case: GPS
^^^^^^^^^^^^^

Consider a sensor such as a Global Positioning System (GPS) receiver. In QtRO terms:

    * The :ref:`Source<Qt-Remote-Objects-Source>` would be the process that directly
      interacts with the GPS hardware and derives your current location.
    * The location would be exposed as :class:`QObject<PySide6.QtCore.QObject>` properties;
      the periodic updates to the location would update these properties and emit property
      changed signals.
    * :ref:`Replicas<Qt-Remote-Objects-Replica>` would be created in other processes
      and would always know your current location, but wouldn't need any of the logic
      to compute the location from the sensor data.
    * Connecting to the location changed signal on the Replica would work as
      expected: the signal emitted from the Source would trigger the signal
      emission on every Replica.

Use Case: Printer Access
^^^^^^^^^^^^^^^^^^^^^^^^

Consider a service that provides access to a printer. In QtRO terms:

    * The :ref:`Source<Qt-Remote-Objects-Source>` would be the process
      controlling the printer directly.
    * The ink levels and printer status would be monitored by
      :class:`QObject<PySide6.QtCore.QObject>` properties. Updates to these
      properties would emit property changed signals.
    * The key feature -- being able to print something -- needs to be passed
      back to the printer. Incidentally, this aligns with the Qt slot mechanism,
      which QtRO uses as the way for :ref:`Replicas<Qt-Remote-Objects-Replica>`
      to make calls on the Source. In effect, properties and signals go from Source
      to Replicas; slots go from Replica to Source.
    * When a print request is accepted, the printer status would change,
      triggering a change in the status property. This would then be reported
      to all Replicas.

Using the Module
^^^^^^^^^^^^^^^^

To include the definitions of modules classes, use the following
directive:

::

    import PySide6.QtRemoteObjects

Articles and Guides
^^^^^^^^^^^^^^^^^^^

    * `Getting Started with Qt Remote Objects  <https://doc.qt.io/qt-6/qtremoteobjects-gettingstarted.html>`_
    * `Nodes  <https://doc.qt.io/qt-6/qtremoteobjects-node.html>`_
    * `Sources  <https://doc.qt.io/qt-6/qtremoteobjects-source.html>`_
    * `Replicas  <https://doc.qt.io/qt-6/qtremoteobjects-replica.html>`_
    * `Registry  <https://doc.qt.io/qt-6/qtremoteobjects-registry.html>`_
    * `Compiler <https://doc.qt.io/qt-6/qtremoteobjects-repc.html>`_
    * `Remote Object Interaction  <https://doc.qt.io/qt-6/qtremoteobjects-interaction.html>`__
    * `Troubleshooting <https://doc.qt.io/qt-6/qtremoteobjects-troubleshooting.html>`_
    * `Protocol Versioning <https://doc.qt.io/qt-6/qtremoteobjects-compatibility.html>`_
