The Qt Serial Bus API provides classes and functions to access the various
industrial serial buses and protocols, such as CAN, ModBus, and others.

Getting Started
^^^^^^^^^^^^^^^

To include the definitions of modules classes, use the following
directive:

::

    import PySide6.QtSerialBus

Supported Buses and Protocols
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    * Qt CAN Bus
    * Qt Modbus

Logging Categories
^^^^^^^^^^^^^^^^^^

The QtSerialBus module exports the following logging categories:

.. list-table::
   :header-rows: 1

   * - Logging Category
     - Description
   * - qt.canbus
     - Enables standard logging inside the Qt CAN Bus classes
   * - qt.canbus.plugins
     - Enables low level logging inside the Qt CAN Bus plugin classes. To set logging for a specific plugin, use ``qt.canbus.plugins.pluginname``, e.g. ``qt.canbus.plugins.socketcan``. ``qt.canbus.plugins*`` affects all plugins.
   * - qt.modbus
     - Enables standard logging inside the Qt Modbus classes
   * - qt.modbus.lowlevel
     - Enables low level logging including individual packet content inside the Qt Modbus classes

Logging categories can be used to enable additional warning and debug output
for QtSerialBus.

A quick way to enable all Qt Modbus logging is to add the following line:

.. code-block:: python

    QLoggingCategory.setFilterRules("qt.modbus* = true")
