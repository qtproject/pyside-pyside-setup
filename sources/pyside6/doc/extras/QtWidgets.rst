A module which provides a set of C++ technologies for building user
interfaces

The QtWidgets module provides a set of UI elements to create classic
desktop-style user interfaces.

Widgets
^^^^^^^

Widgets are the primary elements for creating user interfaces in Qt. They can
display data and status information, receive user input, and provide a
container for other widgets that should be grouped together. A widget that is
not embedded in a parent widget is called a window.

    .. image:: images/parent-child-widgets.png

The :class:`QWidget<PySide6.QtWidgets.QWidget>` class provides the
basic capability to render to the screen, and to handle user input
events. All UI elements that Qt provides are either subclasses of
:class:`QWidget<PySide6.QtWidgets.QWidget>` , or are used in
connection with a :class:`QWidget<PySide6.QtWidgets.QWidget>`
subclass. Creating custom widgets is done by subclassing
:class:`QWidget<PySide6.QtWidgets.QWidget>` or a suitable subclass and
reimplementing the virtual event handlers.

    * :ref:`Window and Dialog Widgets<Window-and-Dialog-Widgets>`
    * :ref:`Application Main Window<Application-Main-Window>`
    * :ref:`Dialog Windows<Dialog-Windows>`
    * :ref:`Keyboard Focus in Widgets<Keyboard-Focus-in-Widgets>`

Styles
^^^^^^

:ref:`Styles<Styles-and-Style-Aware-Widgets>` draw on behalf of
widgets and encapsulate the look and feel of a GUI. Qt's built-in
widgets use the :class:`QStyle<PySide6.QtWidgets.QStyle>` class to
perform nearly all of their drawing, ensuring that they look exactly
like the equivalent native widgets.

:ref:`Qt Style Sheets<Qt-Style-Sheets>` are a powerful mechanism that
allows you to customize the appearance of widgets, in addition to what
is already possible by subclassing
:class:`QStyle<PySide6.QtWidgets.QStyle>` .

Layouts
^^^^^^^

:ref:`Layouts<Layout-Management>` are an elegant and flexible way to
automatically arrange child widgets within their container. Each
widget reports its size requirements to the layout through the
:meth:`sizeHint<PySide6.QtWidgets.QWidget.sizeHint>` and
:meth:`sizePolicy<PySide6.QtWidgets.QWidget.sizePolicy>` properties,
and the layout distributes the available space accordingly.

:ref:`Qt Designer<using_ui_files>` is a powerful tool for interactively
creating and arranging widgets in layouts.

Model/View Classes
^^^^^^^^^^^^^^^^^^

The :ref:`model/view<Model-View-Programming>` architecture provides
classes that manage the way data is presented to the user. Data-driven
applications which use lists and tables are structured to separate the
data and view using models, views, and delegates.

    .. image:: images/windows-treeview.png

Graphics View
^^^^^^^^^^^^^

The :ref:`Graphics View Framework<Graphics-View-Framework>` is for
managing and interacting with a large number of custom-made 2D
graphical items, and a view widget for visualizing the items, with
support for zooming and rotation.

    .. image:: images/graphicsview-items.png

Using the Module
^^^^^^^^^^^^^^^^

To include the definitions of modules classes, use the following
directive:

::

    import PySide6.QtWidgets
