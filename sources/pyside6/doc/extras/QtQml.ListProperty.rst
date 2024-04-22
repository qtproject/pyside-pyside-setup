.. currentmodule:: PySide6.QtQml
.. py:class:: ListProperty

    The ``ListProperty`` class allows applications to expose list-like properties of
    :class:`~PySide6.QtCore.QObject`-derived classes to QML.
    The usage is shown in the :ref:`qml-object-and-list-property-types-example`
    and the :ref:`qml-chapter5-listproperties` example.

    .. py:method:: __init__(type, append, count=None, at=None, clear=None, removeLast=None, doc="", notify=None, designable=True, scriptable=True, stored=True, user=False, constant=False, final=False)

      :param type type: Element type
      :param callable append: A function to append an item
      :param callable count: A function returning the list count
      :param callable at: A function returning the item at an index
      :param callable clear: A function to clear the list
      :param removeLast: A function to remove the last item
      :param str doc: Doc string
      :param Signal notify: A signal emitted when a change occurs
      :param bool designable: Not used in QML
      :param bool scriptable: Not used in QML
      :param bool stored: Whether the property is stored
      :param bool user: Not used in QML
      :param bool constant: Whether the property is constant
      :param bool final: Whether the property is final
