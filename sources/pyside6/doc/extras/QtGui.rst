The Qt GUI module provides classes for windowing system integration,
event handling, OpenGL and OpenGL ES integration, 2D graphics, basic
imaging, fonts, and text. These classes are used internally by Qt's
user interface technologies and can also be used directly, for
instance to write applications using low-level OpenGL ES graphics
APIs.

For application developers writing user interfaces, Qt provides higher
level APIs, like Qt Quick, that are much more suitable than the
enablers found in the Qt GUI module.

Application Windows
^^^^^^^^^^^^^^^^^^^

The most important classes in the Qt GUI module are
:class:`QGuiApplication<PySide6.QtGui.QGuiApplication>` and
:class:`QWindow<PySide6.QtGui.QWindow>` . A Qt application that wants
to show content on screen will need to make use of these.
:class:`QGuiApplication<PySide6.QtGui.QGuiApplication>` contains the
main event loop, where all events from the window system and other
sources are processed and dispatched. It also handles the
application's initialization and finalization.

The :class:`QWindow<PySide6.QtGui.QWindow>` class represents a window
in the underlying windowing system. It provides a number of virtual
functions to handle events ( :class:`QEvent<PySide6.QtCore.QEvent>` )
from the windowing system, such as touch-input, exposure, focus, key
strokes, and geometry changes.

2D Graphics
^^^^^^^^^^^

The Qt GUI module contains classes for 2D graphics, imaging, fonts,
and advanced typography.

A :class:`QWindow<PySide6.QtGui.QWindow>` created with the surface
type :attr:`RasterSurface<QSurface.SurfaceType>` can be used in
combination with :class:`QBackingStore<PySide6.QtGui.QBackingStore>`
and :class:`QPainter<PySide6.QtGui.QPainter>` , Qt's highly optimized
2D vector graphics API. :class:`QPainter<PySide6.QtGui.QPainter>`
supports drawing lines, polygons, vector paths, images, and text. For
more information, see :ref:`Paint System<Paint-System>` and
:ref:`Raster Window Example<Raster-Window-Example>` .

Qt can load and save images using the
:class:`QImage<PySide6.QtGui.QImage>` and
:class:`QPixmap<PySide6.QtGui.QPixmap>` classes. By default, Qt
supports the most common image formats including JPEG and PNG among
others. Users can add support for additional formats via the
:class:`QImageIOPlugin<~.QImageIOPlugin>` class. For more information,
see :ref:`Reading and Writing Image
Files<Reading-and-Writing-Image-Files>` .

Typography in Qt is done with
:class:`QTextDocument<PySide6.QtGui.QTextDocument>` , which uses the
:class:`QPainter<PySide6.QtGui.QPainter>` API in combination with Qt's
font classes, primarily :class:`QFont<PySide6.QtGui.QFont>` .
Applications that prefer more low-level APIs to text and font handling
can use classes like :class:`QRawFont<PySide6.QtGui.QRawFont>` and
:class:`QGlyphRun<PySide6.QtGui.QGlyphRun>` .

OpenGL and OpenGL ES Integration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:class:`QWindow<PySide6.QtGui.QWindow>` supports rendering using
OpenGL and OpenGL ES, depending on what the platform supports. OpenGL
rendering is enabled by setting the
:class:`QWindow<PySide6.QtGui.QWindow>` 's surface type to
:attr:`OpenGLSurface<QSurface.SurfaceType>` , choosing the format
attributes with :class:`QSurfaceFormat<PySide6.QtGui.QSurfaceFormat>`
, and then creating a
:class:`QOpenGLContext<PySide6.QtGui.QOpenGLContext>` to manage the
native OpenGL context. In addition, Qt has
:class:`QOpenGLPaintDevice<PySide6.QtOpenGL.QOpenGLPaintDevice>` ,
which enables the use of OpenGL accelerated
:class:`QPainter<PySide6.QtGui.QPainter>` rendering, as well as
convenience classes that simplify the writing of OpenGL code and hides
the complexities of extension handling and the differences between
OpenGL ES 2 and desktop OpenGL. The convenience classes include
:class:`QOpenGLFunctions<PySide6.QtGui.QOpenGLFunctions>` that lets an
application use all the OpenGL ES 2 functions on desktop OpenGL
without having to manually resolve the OpenGL function pointers. This
enables cross-platform development of applications targeting mobile or
embedded devices, and provides classes that wrap native OpenGL
functionality in a simpler Qt API.

For more information, see the :ref:`OpenGL Window Example<OpenGL-Window-Example>` .

The Qt GUI module also contains a few math classes to aid with the
most common mathematical operations related to 3D graphics. These
classes include :class:`QMatrix4x4<PySide6.QtGui.QMatrix4x4>` ,
:class:`QVector4D<PySide6.QtGui.QVector4D>` , and
:class:`QQuaternion<PySide6.QtGui.QQuaternion>` .

A :class:`QWindow<PySide6.QtGui.QWindow>` created with the
:attr:`OpenGLSurface<QSurface.SurfaceType>` can be used in combination
with :class:`QPainter<PySide6.QtGui.QPainter>` and
:class:`QOpenGLPaintDevice<PySide6.QtOpenGL.QOpenGLPaintDevice>` to
have OpenGL hardware-accelerated 2D graphics by sacrificing some of
the visual quality.

Vulkan Integration
^^^^^^^^^^^^^^^^^^

Qt GUI has support for the `Vulkan <https://www.khronos.org/vulkan/>`_
API. Qt applications require the presence of the `LunarG Vulkan SDK
<https://www.lunarg.com/vulkan-sdk/>`_ .

On Windows, the SDK sets the environment variable ``VULKAN_SDK``\,
which will be detected by the ``configure`` script.

On Android, Vulkan headers were added in API level 24 of the NDK.

Relevant classes:

* QVulkanDeviceFunctions
    * :class:`QVulkanExtension<~.QVulkanExtension>`
    * QVulkanFunctions
    * :class:`QVulkanInfoVector<~.QVulkanInfoVector>`
    * :class:`QVulkanInstance<~.QVulkanInstance>`
    * :class:`QVulkanWindow<~.QVulkanWindow>`
    * :class:`QVulkanWindowRenderer<~.QVulkanWindowRenderer>`

For more information, see the
:ref:`Hello Vulkan Widget Example<Hello-Vulkan-Widget-Example>` and the
:ref:`Hello Vulkan Window Example<Hello-Vulkan-Window-Example>` .

Drag and Drop
^^^^^^^^^^^^^

Qt GUI includes support for drag and drop. The
:ref:`Drag and Drop<Drag-and-Drop>` overview has more information.

Using the Module
^^^^^^^^^^^^^^^^

To include the definitions of modules classes, use the following
directive:

::

    import PySide6.QtGui
