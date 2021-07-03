.. currentmodule:: PySide6.QtCore
.. _ClassInfo:

ClassInfo
*********

This class is used to associate extra information to the class, which is available
using QObject.metaObject(). Qt and PySide doesn't use this information.

The extra information takes the form of a dictionary with key and value in a literal string.

The recommended usage is to provide the key/value using python keyword syntax, where the
keyword becomes the key, and the provided string becomes the value.

If the key needs to contain special characters (spaces, commas, '::', start with a number, etc),
it is also possible to pass a python dictionary with arbitrary strings for both the key and
value and enabling special characters in the key.

.. note:: This Class is a implementation of Q_CLASSINFO macro.


Example
-------

::

    # Recommended syntax
    @ClassInfo(Author='PySide Team', URL='http://www.pyside.org')
    class MyObject(QObject):
        ...


    # Provided to support keys not supported by Python's keyword syntax
    @ClassInfo({'Some key text $': 'This syntax supports special characters in keys'})
    class MyObject(QObject):
        ...
