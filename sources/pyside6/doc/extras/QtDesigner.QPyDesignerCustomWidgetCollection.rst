.. currentmodule:: PySide6.QtDesigner
.. _QPyDesignerCustomWidgetCollection:

QPyDesignerCustomWidgetCollection
*********************************

Synopsis
--------

Functions
^^^^^^^^^

+------------------------------------------------------------------------------------------------+
|def :meth:`registerCustomWidget<QPyDesignerCustomWidgetCollection.registerCustomWidget>` (type) |
+------------------------------------------------------------------------------------------------+
|def :meth:`addCustomWidget<QPyDesignerCustomWidgetCollection.addCustomWidget>` (custom_widget)  |
+------------------------------------------------------------------------------------------------+

Detailed Description
--------------------

    The :class:`~.QPyDesignerCustomWidgetCollection` implements
    `QDesignerCustomWidgetCollectionInterface <https://doc.qt.io/qt-6/qdesignercustomwidgetcollectioninterface.html>`_
    and provides static helper functions for registering custom widgets by
    type or by implementing
    `QDesignerCustomWidgetInterface <https://doc.qt.io/qt-6/qdesignercustomwidgetinterface.html>`_ .

    The usage is explained in :ref:`designer_custom_widgets`.

.. py:staticmethod:: QPyDesignerCustomWidgetCollection.registerCustomWidget(type[, xml=""[, tool_tip=""[, icon=""[, group=""[container=False]]]]])

   Registers an instance of a Python-implemented QWidget by type with Qt Designer.

   The optional keyword arguments correspond to the getters of
   `QDesignerCustomWidgetInterface <https://doc.qt.io/qt-6/qdesignercustomwidgetinterface.html>`_ :

   :param str xml: A snippet of XML code in ``.ui`` format that specifies how the widget is created and sets initial property values.
   :param str tool_tip: Tool tip to be shown in the widget box.
   :param str icon: Path to an icon file be shown in the widget box.
   :param str group: Category for grouping widgets in the widget box.
   :param str module: Module name for generating the import code by `uic <https://doc.qt.io/qt-6/uic.html>`_ .
   :param bool container: Indicates whether the widget is a container like `QGroupBox`, that is, child widgets can be placed on it.

   .. seealso::  :meth:`registerCustomWidget()<PySide6.QtUiTools.QUiLoader.registerCustomWidget>`

.. py:staticmethod:: QPyDesignerCustomWidgetCollection.addCustomWidget(custom_widget)

    Adds a custom widget (implementation of
    `QDesignerCustomWidgetInterface <https://doc.qt.io/qt-6/qdesignercustomwidgetinterface.html>`_)
    with Qt Designer.

   :param QDesignerCustomWidgetInterface custom_widget: Custom widget instance
