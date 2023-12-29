Object List Model Example
=========================

.. tags:: Android

A list of QObject values can also be used as a model.
A list[QObject,] provides the properties of the objects in the list as roles.

The following application creates a DataObject class with Property values
that will be accessible as named roles when a list[DataObject,] is exposed to QML:

.. image:: objectlistmodel.png
   :width: 400
   :alt: Object List Model Screenshot
