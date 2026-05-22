Provides a widget class for displaying a Qt Quick user interface.

The Qt Quick Widgets module is a convenience wrapper for
:class:`~PySide6.QtQuick.QQuickWindow` . It will automatically load and display
a QML scene when given the URL of the main ``qml`` file. Alternatively, you can
instantiate QML objects using :class:`~PySide6.QtQml.QQmlComponent` and place
them in a manually set-up :class:`~PySide6.QtQuickWidgets.QQuickWidget` .

Typical usage:

    ::

            view = QQuickWidget()
            view.setSource(QUrl.fromLocalFile("myqmlfile.qml"))
            view.show()


:class:`~PySide6.QtQuickWidgets.QQuickWidget` also manages resizing the view
and the root item. By default, the
:meth:`~PySide6.QtQuickWidgets.QQuickWidget.resizeMode` is set to
``QQuickWidget.ResizeMode.SizeViewToRootObject`` ,
which will load the component and resize it to fit the view. Alternatively,
you can set
:meth:`~PySide6.QtQuickWidgets.QQuickWidget.resizeMode` to
``QQuickWidget.ResizeMode.SizeViewToRootObject``,
which will resize the view to the root item.
