The Qt OpenGL module offers classes that make it easy to use OpenGL in Qt applications.

Qt has two main approaches to UI development: :mod:`PySide6.QtQuick` and
:mod:`PySide6.QtWidgets`. They exist to support different types of user
interfaces, and build on separate graphics engines that have been optimized
for each of these types.

It is possible to combine code written in the OpenGL graphics API with both of
these user interface types in Qt. This can be useful when the application has
its own OpenGL-dependent code, or when it is integrating with a third-party
OpenGL-based renderer.

The Qt OpenGL module contains convenience classes to make this type of integration easier and faster.

Qt OpenGL and Qt Widgets
^^^^^^^^^^^^^^^^^^^^^^^^

Qt Widgets is typically rendered by a highly optimized and accurate software
rasterizer, and the final content reproduced on screen using a method
appropriate for the platform where the application is running.

But it is also possible to combine Qt Widgets with OpenGL. The main entry point
for this is the :class:`~PySide6.QtOpenGLWidgets.QOpenGLWidget`
class. This class can be used to enable OpenGL rendering for a certain part of
the widget tree, and the classes in the Qt OpenGL module can be used to
facilitate any application-side OpenGL code.

Qt OpenGL and Qt Quick
^^^^^^^^^^^^^^^^^^^^^^

Qt Quick is optimized for hardware-accelerated rendering. By default, it will
be built on the low-level graphics API most appropriate for the target
platform.

For instance, it will default to *Direct3D* on Windows, whereas on macOS, it
will default to *Metal*\. But it is also possible to manually select OpenGL
as the active graphics API on platforms where this is supported.

For more details on enabling OpenGL with Qt Quick, see
:ref:`Qt-Quick-Scene-Graph`.

Using the Module
^^^^^^^^^^^^^^^^

To include the definitions of modules classes, use the following directive:

::

    import PySide6.QtOpenGL
