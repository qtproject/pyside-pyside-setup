The Qt Positioning API provides positioning information via QML and Python interfaces.

Currently the API is supported on Android, iOS, macOS, Linux, and Windows (with
GPS receivers exposed as a serial port providing NMEA sentences or using
``Windows.Devices.Geolocation``\).

Overview
^^^^^^^^

The Qt Positioning API gives developers the ability to determine a position by
using a variety of possible sources, including satellite, or wifi, or text
file, and so on. That information can then be used to for example determine a
position on a map. In addition satellite information can be retrieved and area
based monitoring can be performed.

Using the Module
^^^^^^^^^^^^^^^^

To include the definitions of modules classes, use the following
directive:

::

    import PySide6.QtPositioning

The module also provides `QML types <http://doc.qt.io/qt-6/qtpositioning-qmlmodule.html>`_ .

To load the Qt Positioning module, add the following statement to your .qml files

    ::

        import QtPositioning

Articles and Guides
^^^^^^^^^^^^^^^^^^^

    * :ref:`Positioning introduction for C++<Positioning--C--->`
    * :ref:`Positioning introduction for QML<Positioning--QML->`
    * :ref:`Qt Positioning Plugins<Qt-Positioning-Plugins>`
    * :ref:`Interfaces between C++ and QML Code in Qt Positioning<Interfaces-between-C---and-QML-Code-in-Qt-Positioning>`
