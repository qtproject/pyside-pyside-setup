The Qt Core module is part of Qt's essential modules.

The Qt Core module adds these features to C++:

    * a very powerful mechanism for seamless object communication called signals and slots
    * queryable and designable object properties
    * hierarchical and queryable object trees

The following pages provide more information about Qt's core features:

    * :ref:`The Meta-Object System<The-Meta-Object-System>`
    * :ref:`The Property System<The-Property-System>`
    * :ref:`Object Model<Object-Model>`
    * :ref:`Object Trees & Ownership<Object-Trees---Ownership>`
    * :ref:`Signals & Slots<Signals---Slots>`

Using the Module
^^^^^^^^^^^^^^^^

To include the definitions of modules classes, use the following
directive:

::

    import PySide6.QtCore

Threading and Concurrent Programming
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Qt provides thread support in the form of platform-independent
threading classes, a thread-safe way of posting events, and
signal-slot connections across threads. Multithreaded programming is
also a useful paradigm for performing time-consuming operations
without freezing the user interface of an application.

The Thread Support in Qt page contains information on implementing
threads in applications. Additional concurrent classes are provided by
the :ref:`Qt Concurrent<Qt-Concurrent>` module.

Input/Output and Resources
^^^^^^^^^^^^^^^^^^^^^^^^^^

Qt provides a resource system for organizing application files and
assets, a set of containers, and classes for receiving input and
printing output.

    * :ref:`Serializing Qt Data Types<Serializing-Qt-Data-Types>`

In addition, Qt Core provides a platform-independent mechanism for
storing binary files in the application's executable.

    * :ref:`The Qt Resource System<using_qrc_files>`

Additional Frameworks
^^^^^^^^^^^^^^^^^^^^^

Qt Core also provides some of Qt's key frameworks.

    * :ref:`The Animation Framework<The-Animation-Framework>`
    * `JSON Support in Qt <https://doc.qt.io/qt-6/json.html>`_
    * :ref:`The Event System<The-Event-System>`
