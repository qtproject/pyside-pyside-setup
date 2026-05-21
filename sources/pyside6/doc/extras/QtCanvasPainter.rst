Provides hardware-accelerated painting API on :class:`~PySide6.QtGui.QRhi`.

The Qt Canvas Painter module provides classes for hardware-accelerated
imperative 2D painting. This painting API is available for both
:mod:`~PySide6.QtQuick` and :mod:`~PySide6.QtWidgets`,
and can also be used directly with :class:`~PySide6.QtGui.QRhi`.

The API design generally follows HTML canvas 2d context, with some reductions and some additions.

Compared to :class:`~PySide6.QtGui.QPainter`, the Qt Canvas Painter is more
compact and has fewer abstractions, aiming to perform optimally on
:class:`~PySide6.QtGui.QRhi`. Qt Canvas Painter is designed for GPU rendering
and does not have a CPU backend as :class:`~PySide6.QtGui.QPainter` does.

.. note:: Qt Canvas Painter in 6.11 is in *Technology Preview*\, excluding
          its API from Qt's compatibility promises.
