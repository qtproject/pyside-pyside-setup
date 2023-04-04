Porting Applications from PySide2 to PySide6
============================================

Module Availability
-------------------

Qt for Python 6.2.0 provides all modules planned for inclusion in Qt 6.

Module-Level Changes
--------------------

* The modules *QtMacExtras*, *Qt Quick Controls 1*, *QtWinExtras*,
  *QtXmlPatterns* and *QtX11Extras* have been removed.
* ``QStateMachine`` and related classes have been extracted to a new
  *QtStateMachine* module.
* The modules *QtWebKit* and *QtWebKitWidgets* have been replaced by the new
  *QtWebEngineCore*, *QtWebEngineQuick* and *QtWebEngineWidgets* modules.
* ``QXmlReader`` and related classes (*SAX API*) have been removed.
* The content of the *QtOpenGL* module has been replaced. The class
  ``QGLWidget`` and related classes (``QGLContext``, ``QGLFunctions``,
  ``QGLShaderProgram``) have been removed. Parts of the *Open GL*
  functionality from *QtGui* have been extracted into this module, for example
  ``QOpenGLBuffer`` and ``QOpenGLShaderProgram``.
  There is a new module *QtOpenGLWidgets* which contains the class
  ``QOpenGLWidget``, a replacement for ``QGLWidget``.

As *Open GL*  is phasing out,
`QRhi <https://doc.qt.io/qt-6/topics-graphics.html>`_ should be considered
for graphics applications.

Imports
-------

The first thing to do when porting applications is to replace the
import statements:

.. code-block:: python

    from PySide2.QtWidgets import QApplication...
    from PySide2 import QtCore

needs to be changed to:

.. code-block:: python

    from PySide6.QtWidgets import QApplication...
    from PySide6 import QtCore


Some classes are in a different module now, for example
``QAction`` and ``QShortcut`` have been moved from ``QtWidgets`` to ``QtGui``.

For *Qt Charts* and *Qt Data Visualization*, the additional namespaces have been
removed. It is now possible to use:

.. code-block:: python

    from PySide6.QtCharts import QChartView

directly.


Class/Function Deprecations
---------------------------

Then, the code base needs to be checked for usage of deprecated API and adapted
accordingly. For example:

* The High DPI scaling attributes ``Qt.AA_EnableHighDpiScaling``,
  ``Qt.AA_DisableHighDpiScaling`` and ``Qt.AA_UseHighDpiPixmaps`` are
  deprecated. High DPI is by default enabled in Qt 6 and cannot be turned off.
* ``QDesktopWidget`` has been removed. ``QScreen`` should be used instead,
  which can be retrieved using ``QWidget.screen()``,
  ``QGuiApplication.primaryScreen()`` or ``QGuiApplication.screens()``.
* ``QFontMetrics.width()`` has been renamed to ``horizontalAdvance()``.
* ``QMouseEvent.pos()`` and ``QMouseEvent.globalPos()`` returning a ``QPoint``
  as well as ``QMouseEvent.x()`` and ``QMouseEvent.y()`` returning ``int``
  are now deprecated. ``QMouseEvent.position()`` and
  ``QMouseEvent.globalPosition()`` returning a ``QPointF`` should be used
  instead.
* ``Qt.MidButton`` has been renamed to ``Qt.MiddleButton``.
* ``QOpenGLVersionFunctionsFactory.get()`` instead of
  ``QOpenGLContext.versionFunctions()`` should be used to obtain
  *Open GL* functions.
* ``QRegExp`` has been replaced by ``QRegularExpression``.
* ``QWidget.mapToGlobal()`` and ``QWidget.mapFromGlobal()`` now also accept
  and return ``QPointF``.
* Functions named ``exec_`` (classes ``QCoreApplication``, ``QDialog``,
  ``QEventLoop``) have been renamed to ``exec`` which became possible
  in Python 3.

More information can be found in the
`Porting to Qt 6 <https://doc.qt.io/qt-6/portingguide.html>`_ Guide
and the `Qt 6.2 Documentation <https://doc.qt.io/qt-6/index.html>`_ .
