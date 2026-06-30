Provides functionality for 2D and 3D graphs.

The Qt Graphs module enables you to visualize data in 2D and 3D graphs.

In the 3D realm there is support for bar, scatter, and surface graphs. It's
especially useful for visualizing depth maps and large quantities of rapidly
changing data, such as data received from multiple sensors. The look and feel
of graphs can be customized by using themes or by adding custom items and
labels.

In the 2D realm, there is support for area, bar, donut, line, pie, scatter, and
spline graphs, and they are easily combinable with any other QML content.

Qt Graphs is built on Qt 6 and the 3D graphs on Qt Quick 3D to take advantage
of hardware acceleration and Qt Quick.

QtGraphs QML API
^^^^^^^^^^^^^^^^

The QML types of the module are available through the ``QtGraphs`` import. To
use the types, add the following import statement to your ``.qml`` file:

    ::

        import QtGraphs


Building a widget application
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* :mod:`PySide6.QtGraphsWidgets`

Articles and Guides
^^^^^^^^^^^^^^^^^^^

Limiting Features
-----------------

In cases the target of an application is some embedded hardware with limited
specifications, it is possible to build only 2D or 3D support into the module.

For more information, see :ref:`Qt-Graphs-Configure-Options` .

Qt Graphs for 2D
----------------

* :ref:`Qt-Graphs-Overview-for-2D`
* :ref:`Qt-Graphs-Migration-from-Qt-Charts`

Qt Graphs for 3D
----------------

* :ref:`Qt-Graphs-Overview-for-3D`
* :ref:`Qt-Graphs-Data-Handling-with-3D`
* :ref:`Qt-Graphs-Interacting-with-Data-in-3D`
* :ref:`Qt-Graphs-Migration-from-Qt-DataVisualization`
* :ref:`Qt-Graphs-Integration-with-Qt-Quick-3D`
* :ref:`Qt-Graphs-Known-Issues`

Qt Graphs Common
----------------

* :ref:`Qt-Graphs-Theme-Overview`
