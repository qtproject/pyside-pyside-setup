Provides a set of UI controls for Qt Quick.

Qt Quick Controls provides a set of controls that can be used to build complete
interfaces in Qt Quick.

    .. image:: images/qtquickcontrols-styles.png

Qt Quick Controls comes with a selection of customizable styles. See
:ref:`Styling-Qt-Quick-Controls` for more details.

Controls
^^^^^^^^

For the full list of Qt Quick Controls, see `QML Types`_ .

Button Controls
---------------

    +-----------------------------------------------------------------------------------+---------------------------------------------------------------------------+
    |`AbstractButton <https://doc.qt.io/qt-6/qml-qtquick-controls-abstractbutton.html>`_|Abstract base type providing functionality common to buttons.              |
    +-----------------------------------------------------------------------------------+---------------------------------------------------------------------------+
    |`Button <https://doc.qt.io/qt-6/qml-qtquick-controls-button.html>`_                |Push-button that can be clicked to perform a command or answer a question. |
    +-----------------------------------------------------------------------------------+---------------------------------------------------------------------------+
    |`CheckBox <https://doc.qt.io/qt-6/qml-qtquick-controls-checkbox.html>`_            |Check button that can be toggled on or off.                                |
    +-----------------------------------------------------------------------------------+---------------------------------------------------------------------------+
    |`DelayButton <https://doc.qt.io/qt-6/qml-qtquick-controls-delaybutton.html>`_      |Check button that triggers when held down long enough.                     |
    +-----------------------------------------------------------------------------------+---------------------------------------------------------------------------+
    |`RadioButton <https://doc.qt.io/qt-6/qml-qtquick-controls-radiobutton.html>`_      |Exclusive radio button that can be toggled on or off.                      |
    +-----------------------------------------------------------------------------------+---------------------------------------------------------------------------+
    |`RoundButton <https://doc.qt.io/qt-6/qml-qtquick-controls-roundbutton.html>`_      |A push-button control with rounded corners that can be clicked by the user.|
    +-----------------------------------------------------------------------------------+---------------------------------------------------------------------------+
    |`Switch <https://doc.qt.io/qt-6/qml-qtquick-controls-switch.html>`_                |Switch button that can be toggled on or off.                               |
    +-----------------------------------------------------------------------------------+---------------------------------------------------------------------------+
    |`ToolButton <https://doc.qt.io/qt-6/qml-qtquick-controls-toolbutton.html>`_        |Button with a look suitable for a ToolBar.                                 |
    +-----------------------------------------------------------------------------------+---------------------------------------------------------------------------+

Container Controls
------------------

    +-----------------------------------------------------------------------------------------------+--------------------------------------------------------------------+
    |`ApplicationWindow <https://doc.qt.io/qt-6/qml-qtquick-controls-applicationwindow.html>`_      |Styled top-level window with support for a header and footer.       |
    +-----------------------------------------------------------------------------------------------+--------------------------------------------------------------------+
    |`Container <https://doc.qt.io/qt-6/qml-qtquick-controls-container.html>`_                      |Abstract base type providing functionality common to containers.    |
    +-----------------------------------------------------------------------------------------------+--------------------------------------------------------------------+
    |`Frame <https://doc.qt.io/qt-6/qml-qtquick-controls-frame.html>`_                              |Visual frame for a logical group of controls.                       |
    +-----------------------------------------------------------------------------------------------+--------------------------------------------------------------------+
    |`GroupBox <https://doc.qt.io/qt-6/qml-qtquick-controls-groupbox.html>`_                        |Visual frame and title for a logical group of controls.             |
    +-----------------------------------------------------------------------------------------------+--------------------------------------------------------------------+
    |`HorizontalHeaderView <https://doc.qt.io/qt-6/qml-qtquick-controls-horizontalheaderview.html>`_|Provides a horizontal header view to accompany a TableView.         |
    +-----------------------------------------------------------------------------------------------+--------------------------------------------------------------------+
    |`VerticalHeaderView <https://doc.qt.io/qt-6/qml-qtquick-controls-verticalheaderview.html>`_    |Offers a vertical header view to accompany a TableView.             |
    +-----------------------------------------------------------------------------------------------+--------------------------------------------------------------------+
    |`Page <https://doc.qt.io/qt-6/qml-qtquick-controls-page.html>`_                                |Styled page control with support for a header and footer.           |
    +-----------------------------------------------------------------------------------------------+--------------------------------------------------------------------+
    |`Pane <https://doc.qt.io/qt-6/qml-qtquick-controls-pane.html>`_                                |Provides a background matching with the application style and theme.|
    +-----------------------------------------------------------------------------------------------+--------------------------------------------------------------------+
    |`ScrollView <https://doc.qt.io/qt-6/qml-qtquick-controls-scrollview.html>`_                    |Scrollable view.                                                    |
    +-----------------------------------------------------------------------------------------------+--------------------------------------------------------------------+
    |`SplitView <https://doc.qt.io/qt-6/qml-qtquick-controls-splitview.html>`_                      |Lays out items with a draggable splitter between each item.         |
    +-----------------------------------------------------------------------------------------------+--------------------------------------------------------------------+
    |`StackView <https://doc.qt.io/qt-6/qml-qtquick-controls-stackview.html>`_                      |Provides a stack-based navigation model.                            |
    +-----------------------------------------------------------------------------------------------+--------------------------------------------------------------------+
    |`SwipeView <https://doc.qt.io/qt-6/qml-qtquick-controls-swipeview.html>`_                      |Enables the user to navigate pages by swiping sideways.             |
    +-----------------------------------------------------------------------------------------------+--------------------------------------------------------------------+
    |`TabBar <https://doc.qt.io/qt-6/qml-qtquick-controls-tabbar.html>`_                            |Allows the user to switch between different views or subtasks.      |
    +-----------------------------------------------------------------------------------------------+--------------------------------------------------------------------+
    |`ToolBar <https://doc.qt.io/qt-6/qml-qtquick-controls-toolbar.html>`_                          |Container for context-sensitive controls.                           |
    +-----------------------------------------------------------------------------------------------+--------------------------------------------------------------------+

Delegate Controls
-----------------

    +---------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+
    |`CheckDelegate <https://doc.qt.io/qt-6/qml-qtquick-controls-checkdelegate.html>`_                              |Item delegate with a check indicator that can be toggled on or off.          |
    +---------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+
    |`HorizontalHeaderviewDelegate <https://doc.qt.io/qt-6/qml-qtquick-controls-horizontalheaderviewdelegate.html>`_|                                                                             |
    +---------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+
    |`VerticalHeaderviewDelegate <https://doc.qt.io/qt-6/qml-qtquick-controls-verticalheaderviewdelegate.html>`_    |                                                                             |
    +---------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+
    |`ItemDelegate <https://doc.qt.io/qt-6/qml-qtquick-controls-itemdelegate.html>`_                                |Basic item delegate that can be used in various views and controls.          |
    +---------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+
    |`RadioDelegate <https://doc.qt.io/qt-6/qml-qtquick-controls-radiodelegate.html>`_                              |Exclusive item delegate with a radio indicator that can be toggled on or off.|
    +---------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+
    |`SwipeDelegate <https://doc.qt.io/qt-6/qml-qtquick-controls-swipedelegate.html>`_                              |Swipable item delegate.                                                      |
    +---------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+
    |`SwitchDelegate <https://doc.qt.io/qt-6/qml-qtquick-controls-switchdelegate.html>`_                            |Item delegate with a switch indicator that can be toggled on or off.         |
    +---------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+
    |`TableviewDelegate <https://doc.qt.io/qt-6/qml-qtquick-controls-tableviewdelegate.html>`_                      |A delegate that can be assigned to a TableView.                              |
    +---------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+
    |`TreeviewDelegate <https://doc.qt.io/qt-6/qml-qtquick-controls-treeviewdelegate.html>`_                        |A delegate that can be assigned to a TreeView.                               |
    +---------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+

Indicator Controls
------------------

    +-------------------------------------------------------------------------------------+--------------------------------------------------------------------------+
    |`BusyIndicator <https://doc.qt.io/qt-6/qml-qtquick-controls-busyindicator.html>`_    |Indicates background activity, for example, while content is being loaded.|
    +-------------------------------------------------------------------------------------+--------------------------------------------------------------------------+
    |`PageIndicator <https://doc.qt.io/qt-6/qml-qtquick-controls-pageindicator.html>`_    |Indicates the currently active page.                                      |
    +-------------------------------------------------------------------------------------+--------------------------------------------------------------------------+
    |`ProgressBar <https://doc.qt.io/qt-6/qml-qtquick-controls-progressbar.html>`_        |Indicates the progress of an operation.                                   |
    +-------------------------------------------------------------------------------------+--------------------------------------------------------------------------+
    |`ScrollBar <https://doc.qt.io/qt-6/qml-qtquick-controls-scrollbar.html>`_            |Vertical or horizontal interactive scroll bar.                            |
    +-------------------------------------------------------------------------------------+--------------------------------------------------------------------------+
    |`ScrollIndicator <https://doc.qt.io/qt-6/qml-qtquick-controls-scrollindicator.html>`_|Vertical or horizontal non-interactive scroll indicator.                  |
    +-------------------------------------------------------------------------------------+--------------------------------------------------------------------------+

Input Controls
--------------

    +---------------------------------------------------------------------------------+----------------------------------------------------------------------+
    |`ComboBox <https://doc.qt.io/qt-6/qml-qtquick-controls-combobox.html>`_          |Combined button and popup list for selecting options.                 |
    +---------------------------------------------------------------------------------+----------------------------------------------------------------------+
    |`Dial <https://doc.qt.io/qt-6/qml-qtquick-controls-dial.html>`_                  |Circular dial that is rotated to set a value.                         |
    +---------------------------------------------------------------------------------+----------------------------------------------------------------------+
    |`DoubleSpinBox <https://doc.qt.io/qt-6/qml-qtquick-controls-doublespinbox.html>`_|Allows the user to select from a set of preset floating-point values. |
    +---------------------------------------------------------------------------------+----------------------------------------------------------------------+
    |`RangeSlider <https://doc.qt.io/qt-6/qml-qtquick-controls-rangeslider.html>`_    |Used to select a range of values by sliding two handles along a track.|
    +---------------------------------------------------------------------------------+----------------------------------------------------------------------+
    |`SearchField <https://doc.qt.io/qt-6/qml-qtquick-controls-searchfield.html>`_    |A specialized input field designed to use for search functionality.   |
    +---------------------------------------------------------------------------------+----------------------------------------------------------------------+
    |`Slider <https://doc.qt.io/qt-6/qml-qtquick-controls-slider.html>`_              |Used to select a value by sliding a handle along a track.             |
    +---------------------------------------------------------------------------------+----------------------------------------------------------------------+
    |`SpinBox <https://doc.qt.io/qt-6/qml-qtquick-controls-spinbox.html>`_            |Allows the user to select from a set of preset values.                |
    +---------------------------------------------------------------------------------+----------------------------------------------------------------------+
    |`TextArea <https://doc.qt.io/qt-6/qml-qtquick-controls-textarea.html>`_          |Multi-line text input area.                                           |
    +---------------------------------------------------------------------------------+----------------------------------------------------------------------+
    |`TextField <https://doc.qt.io/qt-6/qml-qtquick-controls-textfield.html>`_        |Single-line text input field.                                         |
    +---------------------------------------------------------------------------------+----------------------------------------------------------------------+
    |`Tumbler <https://doc.qt.io/qt-6/qml-qtquick-controls-tumbler.html>`_            |Spinnable wheel of items that can be selected.                        |
    +---------------------------------------------------------------------------------+----------------------------------------------------------------------+

Menu Controls
-------------

    +-----------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------+
    |`ContextMenu <https://doc.qt.io/qt-6/qml-qtquick-controls-contextmenu.html>`_|The ContextMenu attached type provides a way to open a context menu in a platform-appropriate manner.|
    +-----------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------+
    |`Menu <https://doc.qt.io/qt-6/qml-qtquick-controls-menu.html>`_              |Menu popup that can be used as a context menu or popup menu.                                         |
    +-----------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------+
    |`MenuBar <https://doc.qt.io/qt-6/qml-qtquick-controls-menubar.html>`_        |Provides a window menu bar.                                                                          |
    +-----------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------+
    |`MenuBarItem <https://doc.qt.io/qt-6/qml-qtquick-controls-menubaritem.html>`_|Presents a drop-down menu within a MenuBar.                                                          |
    +-----------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------+
    |`MenuItem <https://doc.qt.io/qt-6/qml-qtquick-controls-menuitem.html>`_      |Presents an item within a Menu.                                                                      |
    +-----------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------+

Navigation Controls
-------------------

    +-------------------------------------------------------------------------+---------------------------------------------------------------+
    |`Drawer <https://doc.qt.io/qt-6/qml-qtquick-controls-drawer.html>`_      |Side panel that can be opened and closed using a swipe gesture.|
    +-------------------------------------------------------------------------+---------------------------------------------------------------+
    |`StackView <https://doc.qt.io/qt-6/qml-qtquick-controls-stackview.html>`_|Provides a stack-based navigation model.                       |
    +-------------------------------------------------------------------------+---------------------------------------------------------------+
    |`SwipeView <https://doc.qt.io/qt-6/qml-qtquick-controls-swipeview.html>`_|Enables the user to navigate pages by swiping sideways.        |
    +-------------------------------------------------------------------------+---------------------------------------------------------------+
    |`TabBar <https://doc.qt.io/qt-6/qml-qtquick-controls-tabbar.html>`_      |Allows the user to switch between different views or subtasks. |
    +-------------------------------------------------------------------------+---------------------------------------------------------------+
    |`TabButton <https://doc.qt.io/qt-6/qml-qtquick-controls-tabbutton.html>`_|Button with a look suitable for a TabBar.                      |
    +-------------------------------------------------------------------------+---------------------------------------------------------------+

Popup Controls
--------------

    +---------------------------------------------------------------------+----------------------------------------------------------------------------------------------+
    |`Dialog <https://doc.qt.io/qt-6/qml-qtquick-controls-dialog.html>`_  |Popup dialog with standard buttons and a title, used for short-term interaction with the user.|
    +---------------------------------------------------------------------+----------------------------------------------------------------------------------------------+
    |`Drawer <https://doc.qt.io/qt-6/qml-qtquick-controls-drawer.html>`_  |Side panel that can be opened and closed using a swipe gesture.                               |
    +---------------------------------------------------------------------+----------------------------------------------------------------------------------------------+
    |`Menu <https://doc.qt.io/qt-6/qml-qtquick-controls-menu.html>`_      |Menu popup that can be used as a context menu or popup menu.                                  |
    +---------------------------------------------------------------------+----------------------------------------------------------------------------------------------+
    |`Popup <https://doc.qt.io/qt-6/qml-qtquick-controls-popup.html>`_    |Base type of popup-like user interface controls.                                              |
    +---------------------------------------------------------------------+----------------------------------------------------------------------------------------------+
    |`ToolTip <https://doc.qt.io/qt-6/qml-qtquick-controls-tooltip.html>`_|Provides tool tips for any control.                                                           |
    +---------------------------------------------------------------------+----------------------------------------------------------------------------------------------+

Separator Controls
------------------

    +---------------------------------------------------------------------------------+------------------------------------------------------------+
    |`MenuSeparator <https://doc.qt.io/qt-6/qml-qtquick-controls-menuseparator.html>`_|Separates a group of items in a menu from adjacent items.   |
    +---------------------------------------------------------------------------------+------------------------------------------------------------+
    |`ToolSeparator <https://doc.qt.io/qt-6/qml-qtquick-controls-toolseparator.html>`_|Separates a group of items in a toolbar from adjacent items.|
    +---------------------------------------------------------------------------------+------------------------------------------------------------+

Using the Module
^^^^^^^^^^^^^^^^

To include the definitions of modules classes, use the following
directive:

::

    import PySide6.QtQuickControls2

Articles and Guides
^^^^^^^^^^^^^^^^^^^

* :ref:`Getting-Started-with-Qt-Quick-Controls`
* `Qt Quick Controls Guidelines`_
* :ref:`Styling-Qt-Quick-Controls`
* :ref:`Icons-in-Qt-Quick-Controls`
* :ref:`Customizing-Qt-Quick-Controls`
* :ref:`Using-File-Selectors-with-Qt-Quick-Controls`
* :ref:`Deploying-Qt-Quick-Controls-Applications`
* :ref:`Qt-Quick-Controls-Configuration-File`
* :ref:`Supported-Environment-Variables-in-Qt-Quick-Controls`

Related Modules
^^^^^^^^^^^^^^^

* :mod:`PySide6.QtQuick`
* `Qt Quick Layouts`_
* `Qt Quick Templates 2`_
* `Qt Labs Platform`_

.. _`QML Types`: https://doc.qt.io/qt-6/qtquick-controls-qmlmodule.html
.. _`Qt Quick Controls Guidelines`: https://doc.qt.io/qt-6/qtquickcontrols-guidelines.html
.. _`Qt Quick Layouts`: https://doc.qt.io/qt-6/qtquicklayouts-index.html
.. _`Qt Quick Templates 2`: https://doc.qt.io/qt-6/qtquicktemplates2-index.html
.. _`Qt Labs Platform`: https://doc.qt.io/qt-6/qtlabsplatform-index.html
