Qt Bluetooth enables connectivity between Bluetooth enabled devices.

The Bluetooth API provides connectivity between Bluetooth enabled devices.

Currently, the API is supported on the following platforms:

    +-------------------------------------+-------+---+-----------------+-----------------------------------------+--------------+
    |API Feature                          |Android|iOS|Linux (BlueZ 5.x)|:ref:`macOS<Qt-WebEngine-Platform-Notes>`|Qt for Windows|
    +-------------------------------------+-------+---+-----------------+-----------------------------------------+--------------+
    |Classic Bluetooth                    |x      |   |x                |x                                        |x             |
    +-------------------------------------+-------+---+-----------------+-----------------------------------------+--------------+
    |Bluetooth LE Central                 |x      |x  |x                |x                                        |x             |
    +-------------------------------------+-------+---+-----------------+-----------------------------------------+--------------+
    |Bluetooth LE Peripheral              |x      |x  |x                |x                                        |              |
    +-------------------------------------+-------+---+-----------------+-----------------------------------------+--------------+
    |Bluetooth LE Advertisement & Scanning|       |   |                 |                                         |              |
    +-------------------------------------+-------+---+-----------------+-----------------------------------------+--------------+

Qt 5.14 adds a native Win32 port supporting Classic Bluetooth on Windows 7 or
newer, and Bluetooth LE on Windows 8 or newer. It must be enabled at build time
by configuration option -native-win32-bluetooth. The UWP backend is used by
default if this option is not set and the Win32 target platform supports the
required UWP APIs (minimal requirement is Windows 10 version 1507, with
slightly improved service discovery since Windows 10 version 1607).

Overview
^^^^^^^^

Bluetooth is a short-range (less than 100 meters) wireless technology. It has a
reasonably high data transfer rate of 2.1 Mbit/s, which makes it ideal for
transferring data between devices. Bluetooth connectivity is based on basic
device management, such as scanning for devices, gathering information about
them, and exchanging data between them.

Qt Bluetooth supports Bluetooth Low Energy development for client/central role
use cases. Further details can be found in the :ref:`Bluetooth Low Energy
Overview<Bluetooth-Low-Energy-Overview>` section.

Using the Module
^^^^^^^^^^^^^^^^

To include the definitions of modules classes, use the following
directive:

::

    import PySide6.QtBluetooth

macOS Specific
^^^^^^^^^^^^^^

The Bluetooth API on macOS requires a certain type of event dispatcher that in
Qt causes a dependency to
:class:`QGuiApplication<PySide6.QtGui.QGuiApplication>` . However, you can set
the environment variable ``QT_EVENT_DISPATCHER_CORE_FOUNDATION=1`` to
circumvent this issue.

Applications that don't use Classic Bluetooth will find a subset of
`QtBluetooth <https://doc.qt.io/qt-6/qtbluetooth-module.html>`_ is available,
as CoreBluetooth (Bluetooth LE) do not require either of
:class:`QApplication<PySide6.QtWidgets.QApplication>` or
:class:`QGuiApplication<PySide6.QtGui.QGuiApplication>` .

Guides
^^^^^^

    * :ref:`Classic Bluetooth Overview<Qt-Bluetooth-Overview>`
    * :ref:`Bluetooth Low Energy Overview<Bluetooth-Low-Energy-Overview>`


Logging Categories
^^^^^^^^^^^^^^^^^^

The `QtBluetooth <https://doc.qt.io/qt-6/qtbluetooth-module.html>`_ module
exports the following :class:`logging categories<~.Configuring Categories>` :

    +--------------------+--------------------------------------------------------------------------------------------------------------+
    |Logging Category    |Description                                                                                                   |
    +--------------------+--------------------------------------------------------------------------------------------------------------+
    |qt.bluetooth        |Enables logging of cross platform code path in `QtBluetooth <https://doc.qt.io/qt-6/qtbluetooth-module.html>`_|
    +--------------------+--------------------------------------------------------------------------------------------------------------+
    |qt.bluetooth.android|Enables logging of the Android implementation                                                                 |
    +--------------------+--------------------------------------------------------------------------------------------------------------+
    |qt.bluetooth.bluez  |Enables logging of the BLuez/Linux implementation                                                             |
    +--------------------+--------------------------------------------------------------------------------------------------------------+
    |qt.bluetooth.ios    |Enables logging of the iOS implementation                                                                     |
    +--------------------+--------------------------------------------------------------------------------------------------------------+
    |qt.bluetooth.osx    |Enables logging of the macOS implementation                                                                   |
    +--------------------+--------------------------------------------------------------------------------------------------------------+
    |qt.bluetooth.windows|Enables logging of the Qt for Windows implementation                                                          |
    +--------------------+--------------------------------------------------------------------------------------------------------------+

Logging categories can be used to enable additional warning and debug output
for `QtBluetooth <https://doc.qt.io/qt-6/qtbluetooth-module.html>`_ . More
detailed information about logging can be found in
:class:`QLoggingCategory<~.QLoggingCategory>` . A quick way to enable all
`QtBluetooth <https://doc.qt.io/qt-6/qtbluetooth-module.html>`_ logging is to
add the following line to the ``main()`` function:

    ::

            QLoggingCategory.setFilterRules("qt.bluetooth* = true")
