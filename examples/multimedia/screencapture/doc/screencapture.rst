Screen Capture Example
======================

Screen Capture demonstrates how to capture a screen or window using
:class:`~PySide6.QtMultimedia.QScreenCapture` and :class:`~PySide6..QtMultimedia.QWindowCapture`.
The example shows a list of screens and windows and displays a live preview of the selected
item using a :class:`~PySide6.QtMultimedia.QMediaCaptureSession` and a
:class:`~PySide6.QtMultimediaWidgets.QVideoWidget`. Capturing can be started and
stopped with a :class:`~PySide6.QtWidgets.QPushButton`.

Application Structure
+++++++++++++++++++++

The example consists of three custom classes. The UI and all screen capture
functionality is implemented in the class ``ScreenCapturePreview``. The classes
``ScreenListModel`` and ``WindowListModel`` only serve as models behind the two
:class:`~PySide6.QtWidgets.QListView` widgets. The main function creates a ``ScreenCapturePreview``
object, which in turn creates instances of :class:`~PySide6.QtMultimedia.QScreenCapture` and
:class:`~PySide6.QtMultimedia.QWindowCapture`, and a
:class:`~PySide6.QtMultimedia.QMediaCaptureSession`
and :class:`~PySide6.QtMultimediaWidgets.QVideoWidget`, in addition to all the UI widgets.

The screen and window models are populated with the return values of
:meth:`~PySide6.QtGui.QGuiApplication.screens` and
:meth:`~PySide6.QtMultimedia.QWindowCapture.capturableWindows`, respectively.

When a list item is selected, it is connected to the :class:`~PySide6.QtMultimedia.QScreenCapture`
object with :meth:`~PySide6.QtMultimedia.QScreenCapture.setScreen`, or to the
:class:`~PySide6.QtMultimedia.QWindowCapture` object with
``QWindowCapture.setWindow().`` The capture object is connected to the
:class:`~PySide6.QtMultimedia.QMediaCaptureSession` object with
:meth:`~PySide6.QtMultimedia.QMediaCaptureSession.setScreenCapture` and
:meth:`~PySide6.QtMultimedia.QMediaCaptureSession.setWindowCapture`, respectively.
The capture session in turn is connected to the :class:`~PySide6.QtMultimediaWidgets.QVideoWidget`
object with :meth:`~PySide6.QtMultimedia.QMediaCaptureSession.setVideoOutput`. Thus,
the capture output is previewed in the video widget on the right hand side of the UI.

The start/stop button calls :meth:`~PySide6.QtMultimedia.QScreenCapture.start` and
:meth:`~PySide6.QtMultimedia.QScreenCapture.stop`,
or :meth:`~PySide6.QtMultimedia.QWindowCapture.start` and
:meth:`~PySide6.QtMultimedia.QWindowCapture.stop`.

A :class:`~PySide6.QtWidgets.QMessageBox` pops up if an ``errorOccurred`` signal is emitted.

.. image. screencapture.webp
   :width: 600
   :alt: screen capture example
