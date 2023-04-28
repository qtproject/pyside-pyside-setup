.. _qml-extension-objects-example:

Extending QML - Extension Objects Example
=========================================

This example builds on the the :ref:`qml-adding-types-example`.

Shows how to use QmlExtended decorator to provide an extension object to a
QLineEdit without modifying or subclassing it.

Firstly, the LineEditExtension class is registered with the QML system as an
extension of QLineEdit. We declare a foreign type to do this as we cannot
modify Qt's internal QLineEdit class.

.. code-block:: python

    @QmlNamedElement("QLineEdit")
    @QmlExtended(LineEditExtension)
    @QmlForeign(QLineEdit)
    class LineEditForeign(QObject):


Note the usage of ``QmlNamedElement()`` instead of ``QmlElement()``.
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

The extension type performs calls on the ``QLineEdit`` that otherwise will not
be accessible to the QML engine.
