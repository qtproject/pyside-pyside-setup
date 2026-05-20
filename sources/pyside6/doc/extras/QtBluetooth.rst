Qt Bluetooth enables connectivity between Bluetooth enabled devices.

The Bluetooth API provides connectivity between Bluetooth enabled devices.

Currently, the API is supported on the following platforms:

    +-----------------------+-------+---+-----------------+-----+-------+
    |API Feature            |Android|iOS|Linux (BlueZ 5.x)|macOS|Windows|
    +=======================+=======+===+=================+=====+=======+
    |Classic Bluetooth      |x      |   |x                |x    |x      |
    +-----------------------+-------+---+-----------------+-----+-------+
    |Bluetooth LE Central   |x      |x  |x                |x    |x      |
    +-----------------------+-------+---+-----------------+-----+-------+
    |Bluetooth LE Peripheral|x      |x  |x                |x    |       |
    +-----------------------+-------+---+-----------------+-----+-------+


Overview
^^^^^^^^

Bluetooth is a short-range (less than 100 meters) wireless technology. It has a
data transfer rate of 2.1 Mbps, which makes it ideal for transferring data
between devices. Bluetooth connectivity is based on basic device management,
such as scanning for devices, gathering information about them, and exchanging
data between them.

Qt Bluetooth supports Bluetooth Low Energy development for client/central role
use cases. Further details can be found in the :ref:`Bluetooth-Low-Energy-Overview` section.

Permissions
^^^^^^^^^^^

Starting from Qt 6.6, the Qt Bluetooth module uses new
:class:`~PySide6.QtCore.QPermission` API to handle Bluetooth permissions.
This means that Qt itself no longer queries for these permissions, so this
needs to be done directly from the client application.

Please refer to the :ref:`Application-Permissions` page for an example of how to
integrate the new QPermission API into the application.

Using the Module
^^^^^^^^^^^^^^^^

To include the definitions of modules classes, use the following
directive:

::

    import PySide6.QtBluetooth


Linux Specific
^^^^^^^^^^^^^^

Since Qt 6.5 the Linux peripheral support has two backend alternatives:
*BlueZ DBus* and *Bluetooth Kernel API*. The DBus backend is the default
backend since Qt 6.7.

*BlueZ DBus* is the newer *BlueZ* stack and possibly the eventual successor of the
older Kernel API. It is a bit more limited in terms of features, but in a
typical usage this should not matter. One notable benefit of using the DBus
backend is that the user process no longer needs to have the ``CAP_NET_ADMIN``
capability (for example by running as ``root`` user).

The DBus backend requires *BlueZ* version 5.56 or higher, and that it provides
the needed DBus APIs. If these requirements are not met, Qt automatically falls
back to the *Bluetooth Kernel API* backend.

The older kernel backend can also be selected manually by setting the
``QT_BLUETOOTH_USE_KERNEL_PERIPHERAL`` environment variable.

macOS Specific
^^^^^^^^^^^^^^

The Bluetooth API on macOS requires a certain type of event dispatcher that in
Qt causes a dependency to :class:`~PySide6.QtGui.QGuiApplication`.
However, you can set the environment variable
`QT_EVENT_DISPATCHER_CORE_FOUNDATION=1`` to circumvent this issue.

Applications that don't use Classic Bluetooth will find a subset of
QtBluetooth is available, as CoreBluetooth (Bluetooth LE) don't require
:class:`~PySide6.QtWidgets.QApplication` or :class:`~PySide6.QtGui.QGuiApplication`.

Articles and Guides
^^^^^^^^^^^^^^^^^^^

    * :ref:`Qt-Bluetooth-Overview`
    * :ref:`Bluetooth-Low-Energy-Overview`

Logging Categories
^^^^^^^^^^^^^^^^^^

The QtBluetooth module exports the following logging categories:

    +--------------------+-----------------------------------------------------------+
    |Logging Category    |Description                                                |
    +====================+===========================================================+
    |qt.bluetooth        |Enables logging of cross platform code path in QtBluetooth |
    +--------------------+-----------------------------------------------------------+
    |qt.bluetooth.android|Enables logging of the Android implementation              |
    +--------------------+-----------------------------------------------------------+
    |qt.bluetooth.bluez  |Enables logging of the BLuez/Linux implementation          |
    +--------------------+-----------------------------------------------------------+
    |qt.bluetooth.ios    |Enables logging of the iOS implementation                  |
    +--------------------+-----------------------------------------------------------+
    |qt.bluetooth.osx    |Enables logging of the macOS implementation                |
    +--------------------+-----------------------------------------------------------+
    |qt.bluetooth.windows|Enables logging of the Windows implementation              |
    +--------------------+-----------------------------------------------------------+

Logging categories enable additional warning and debug output for QtBluetooth. More
detailed information about logging is found in
:class:`~PySide6.QtCore.QLoggingCategory`. A quick way to enable all QtBluetooth
logging is to add the following line:

    ::

            QLoggingCategory.setFilterRules("qt.bluetooth* = true")
