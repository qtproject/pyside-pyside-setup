Surface Example
===============

Using Q3DSurface in a widget application.

The surface example shows how to make a simple 3D surface graph using
Q3DSurface and combining the use of widgets for adjusting several adjustable
qualities. It requires building PySide6 with the ``--pyside-numpy-support``
option. This example demonstrates the following features:

* How to set up a QSurfaceDataProxy from a 2-dimensional numpy array.
* How to use QHeightMapSurfaceDataProxy for showing 3D height maps.
* Three different selection modes for studying the graph.
* Axis range usage for displaying selected portions of the graph.
* Changing theme.
* How to set a custom surface gradient.

For instructions about how to interact with the graph, see `this page`_.

.. image:: surface_mountain.png
   :width: 400
   :alt: Surface Example Screenshot

.. _`this page`: https://doc.qt.io/qt-6/qtdatavisualization-interacting-with-data.html
