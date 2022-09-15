OpenGL under QML Squircle
=========================

The OpenGL under QML example shows how an application can make use of the
QQuickWindow::beforeRendering() signal to draw custom OpenGL content under a Qt
Quick scene. This signal is emitted at the start of every frame, before the
scene graph starts its rendering, thus any OpenGL draw calls that are made as
a response to this signal, will stack under the Qt Quick items.

As an alternative, applications that wish to render OpenGL content on top of
the Qt Quick scene, can do so by connecting to the
QQuickWindow::afterRendering() signal.

In this example, we will also see how it is possible to have values that are
exposed to QML which affect the OpenGL rendering. We animate the threshold
value using a NumberAnimation in the QML file and this value is used by the
OpenGL shader program that draws the squircles.

.. image:: squircle.png
   :width: 400
   :alt: Squircle Screenshot
