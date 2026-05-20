The Qt Positioning API provides positioning information via QML and C++ interfaces.

Currently, the API is supported on Android, iOS, macOS, Linux, and Windows
(with GPS receivers exposed as a serial port providing NMEA sentences or using
*Windows.Devices.Geolocation*\).

Overview
^^^^^^^^

The Qt Positioning API lets you to determine a position by using a variety of
possible sources, including satellite, wifi, or text files. That information
can then be used to, for example, determine a position on a map. In addition,
you can use to the API to retrieve satellite information and perform area based
monitoring.

Permissions
^^^^^^^^^^^

Starting from Qt 6.6, the Qt Positioning module uses new
:class:`~PySide6.QtCore.QPermission` API to handle location permissions.
This means that Qt itself no longer queries for these permissions, so this
needs to be done directly from the client application.

Please refer to the :ref:`Application-Permissions` page for an example of how to
integrate the new QPermission API into the application.

Using the Module
^^^^^^^^^^^^^^^^

To include the definitions of modules classes, use the following
directive:

::

    import PySide6.QtPositioning

To load the Qt Positioning module, add the following statement to your .qml files

    ::

        import QtPositioning

Articles and Guides
^^^^^^^^^^^^^^^^^^^

    * :ref:`Positioning--C---`
    * :ref:`Positioning--QML-`
    * :ref:`Qt-Positioning-Plugins`
    * :ref:`Interfaces-between-C---and-QML-Code-in-Qt-Positioning`
    * :ref:`Qt-Positioning-on-Android`
    * :ref:`Qt-Positioning-on-iOS`
