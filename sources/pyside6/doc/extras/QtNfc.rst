Enables connectivity between NFC enabled devices.

The NFC API provides connectivity between NFC enabled devices.

Overview
^^^^^^^^

NFC is an extremely short-range (less than 20 centimeters) wireless technology
and has a maximum transfer rate of 424 kbit/s. NFC is ideal for transferring
small packets of data when two devices are touched together.

The NFC API provides APIs for interacting with NFC Forum Tags and NFC Forum
Devices, including target detection and loss, registering NDEF message
handlers, reading and writing NDEF messages on NFC Forum Tags and sending tag
specific commands.

Using the Module
^^^^^^^^^^^^^^^^

To include the definitions of modules classes, use the following
directive:

::

    import PySide6.QtNfc

Guides
^^^^^^

    * `Qt NFC Overview <https://doc.qt.io/qt-6/qtnfc-overview.html>`_
    * `Qt NFC on Android <https://doc.qt.io/qt-6/nfc-android.html>`_
