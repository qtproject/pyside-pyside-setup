.. currentmodule:: PySide6.QtQml
.. _qmlRegisterSingletonInstance:

qmlRegisterSingletonInstance
****************************

.. py:function:: qmlRegisterSingletonInstance(pytype: type,\
                                              uri: str,\
                                              versionMajor: int,\
                                              versionMinor: int,\
                                              typeName: str,\
                                              instanceObject: object) -> int

   :param type pytype: Python class
   :param str uri: uri to use while importing the component in QML
   :param int versionMajor: major version
   :param int versionMinor: minor version
   :param str typeName: name exposed to QML
   :param object instanceObject: singleton object to be registered
   :return: int (the QML type id)

   This function registers a singleton Python object *instanceObject*, with a particular *uri* and
   *typeName*. Its version is a combination of *versionMajor* and *versionMinor*.

   Use this function to register an object of the given type *pytype* as a singleton type.
