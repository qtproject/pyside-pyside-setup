Extending QML - Extension Objects Example
=========================================

This example builds on the the :ref:`example_qml_tutorials_extending-qml-advanced_adding`.

Shows how to use :deco:`~PySide6.QtQml.QmlExtended` to provide an extension object to a
QLineEdit without modifying or subclassing it.

Firstly, the LineEditExtension class is registered with the QML system as an
extension of :class:`~PySide6.QtWidgets.QLineEdit`. We declare a foreign type to do
this as we cannot modify Qt's internal QLineEdit class.

.. code-block:: python

    @QmlNamedElement("QLineEdit")
    @QmlExtended(LineEditExtension)
    @QmlForeign(QLineEdit)
    class LineEditForeign(QObject):


Note the usage of :deco:`~PySide6.QtQml.QmlNamedElement` instead of
:deco:`~PySide6.QtQml.QmlElement`.
``QmlElement()`` uses the name of the containing type by default,
``LineEditExtension`` in this case. As the class being an extension class is
an implementation detail, we choose the more natural name ``QLineEdit``
instead.

The QML engine then instantiates a QLineEdit.

In QML, a property is set on the line edit that only exists in the
``LineEditExtension`` class:

.. code-block:: javascript

    QLineEdit {
        left_margin: 20
    }

The extension type performs calls on the :class:`~PySide6.QtWidgets.QLineEdit` that
otherwise will not be accessible to the QML engine.
