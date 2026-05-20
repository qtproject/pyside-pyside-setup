Enables connectivity between NFC enabled devices.

The NFC API provides connectivity between NFC enabled devices.

Currently, the API is supported on Android, iOS and Linux using `Neard`_  v0.14
or later. This module also provides limited access to readers supporting the
:ref:`PC-SC-in-Qt-NFC` specification on Linux, macOS, and Windows.

NFC is a short-range (less than 20 centimeters) wireless technology with a
maximum transfer rate of 424 Kbps. NFC is ideal for transferring small packets
of data when two devices are placed together.

The NFC module provides APIs for interacting with NFC Forum Tags and NFC Forum
Devices. It can detect targets and losses, register NDEF message handlers, read
and write NDEF messages on NFC Forum Tags, and send tag-specific commands.

.. _`Neard`: https://github.com/linux-nfc/neard

Articles and Guides
^^^^^^^^^^^^^^^^^^^

    * :ref:`Qt-NFC-Overview`
    * :ref:`Supported-NFC-Features`
    * :ref:`Qt-NFC-on-Android`
    * :ref:`PC-SC-in-Qt-NFC`

Logging Categories
^^^^^^^^^^^^^^^^^^

The QtNfc module exports the following logging categories:

    +----------------+-------------------------------------------------+
    |Logging Category|Description                                      |
    +================+=================================================+
    |qt.nfc.neard    |Enables logging of the Neard/Linux implementation|
    +----------------+-------------------------------------------------+
