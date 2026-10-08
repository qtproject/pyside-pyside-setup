Qt Canvas Painter - Hello Widget Example
========================================

The example demonstrates the use of
:class:`~PySide6.QtCanvasPainter.QCanvasanvasPainter`
and :class:`~PySide6.QtCanvasPainter.QCanvasPainterWidget`

The example implements a :class:`~PySide6.QtCanvasPainter.QCanvasPainterWidget`
subclass. One or more instances of this widget can then be added into a
:class:`~PySide6.QtWidgets.QMdiArea` inside the
:class:`~PySide6.QtWidgets.QMainWindow`.
:class:`~PySide6.QtCanvasPainter.QCanvasPainterWidget` itself derives from
:class:`~PySide6.QtWidgets.QRhiWidget`, and is always using accelerated 3D
rendering via :class:`~PySide6.QtGui.QRhi`.

Subclasses of :class:`~PySide6.QtCanvasPainter.QCanvasPainterWidget` will
at minimum want to implement :meth:`~PySide6.QtCanvasPainter.QCanvasPainterWidget.paint`.
This example also uses an image, loaded from a ``PNG`` file.

The ``paint()`` function can start drawing using the provider
:class:`~PySide6.QtCanvasPainter.QCanvasPainter` right away.

See :class:`~PySide6.QtCanvasPainter.QCanvasPainter`,
:class:`~PySide6.QtCanvasPainter.QCanvasBrush`,
:class:`~PySide6.QtCanvasPainter.QCanvasRadialGradient`,
:class:`~PySide6.QtCanvasPainter.QCanvasImagePattern`,
:class:`~PySide6.QtCanvasPainter.QCanvasImage` and
:class:`~PySide6.QtGui.QFont` for more information on the features used by
this example.

The image is used as a pattern, for filling the heart shape.

When resources like :class:`~PySide6.QtCanvasPainter.QCanvasImage` and
:class:`~PySide6.QtCanvasPainter.QCanvasOffscreenCanvas` and
are involved, these are
managed in :meth:`~PySide6.QtCanvasPainter.QCanvasPainterWidget.initializeResources` and
:meth:`~PySide6.QtCanvasPainter.QCanvasPainterWidget.graphicsResourcesInvalidated`.

``initializeResources()`` is merely a convenience. Instead of implementing it,
one could also write the following in paint():

.. code-block:: python

     if self.m_image.isNull():
         self.m_image = p.addImage(QImage(":/qt-translucent.png"),
                                   QCanvasPainter.ImageFlag.Repeat)

This example does not reparent widgets between windows, so graphics resources
are not going to be lost. It is nonetheless a good pattern to assign a default,
empty object to all :class:`~PySide6.QtCanvasPainter.QCanvasImage` and
:class:`~PySide6.QtCanvasPainter.QCanvasOffscreenCanvas` variables in
``graphicsResourcesInvalidated()``.

The main() function creates a :class:`~PySide6.QtWidgets.QMainWindow` and a
:class:`~PySide6.QtWidgets.QMdiArea`. Multiple instances of the ``CanvasWidget``
class can be added as sub-windows. Due to
:meth:`~PySide6.QtCanvasPainter.QCanvasPainterWidget.hasSharedPainter` defaulting
to true, and due to being placed within the same top-level widget, all the painter
widgets will share the same :class:`~PySide6.QtCanvasPainter.QCanvasPainter` and
the associated rendering infrastructure, instead of creating dedicated ones.

.. image:: hellowidget.webp
   :width: 720
   :alt: Hello Widget Example Screenshot
