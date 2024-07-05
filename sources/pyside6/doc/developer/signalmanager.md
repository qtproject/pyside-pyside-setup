# Signalmanager

# Description

The class `Signalmanager` in *p/sources/pyside6/libpyside* takes care of routing
Qt signals to the receivers (files *signalmanager.cpp*, *qobjectconnect.cpp*,
*pysidesignal.cpp*).

There are several kinds of receivers:
- Slots of C++ classes
- Slots of `QObject`-derived classes declared in Python using `@Slot`
- Functions of `QObject`-derived classes declared in Python. They will
  be turned into proper slots at runtime using the private Qt class
  `QMetaObjectBuilder`. This causes a warning to be emitted,
  visible when activating the logging category `qt.pyside.libpyside`.
- Methods of non-`QObject`-derived classes
- Other callables (free functions, lambdas, partially bound functions)

Proper Qt connections where `QObject.disconnect()`, `QObject.sender()` and
`QObject.connectNotify()` work are desirable also for receivers that are not
`QObject`s. This is achieved by using a `QObject`-derived class
`GlobalReceiverV2` for a receiver which has a dynamic slot created by
`QMetaObjectBuilder` to route connected signals to the Python receiver (based
on internal class `DynamicSlotDataV2`).

The instances of  `GlobalReceiverV2` are stored in a hash on the receiver
Python objects in `Signalmanager`.

`QMetaObject::connect(QObject*,int,QObject*,int)` is used to make the
connections based on meta method indexes.

Normally, a reference should be kept on the receiver callable. However, in the
case of a method of a non-`QObject`-derived class, the connection should be
automatically severed when the instance is deleted. The callable passed in this
case (`signal.connect(foo.slot)`) is a partially bound function which has the
`self` parameter. It is decomposed into the `self` parameter and the method. A
reference is kept on the method. A weak reference with destruction callback is
kept for `self`.

## Issues

- [Receiver Leak PYSIDE-1057](https://bugreports.qt.io/browse/PYSIDE-1057)
- [Partial function receiver Leak PYSIDE-2793](https://bugreports.qt.io/browse/PYSIDE-2793)
- Various issues related to threading and object deletion, solved by workarounds
  ([PYSIDE-2646](https://bugreports.qt.io/browse/PYSIDE-2646))
- Complicated code, hard to maintain
- Disconnect does not work for `QObject.connect()` with context argument; it also
  leaks methods

## Plans

Change
[QObject: Add connect() overload with context arg acab25a3ccb836818e5089b23d40196bc7414b7a](https://codereview.qt-project.org/c/pyside/pyside-setup/+/536298)
implements a connection based on `QtPrivate::QSlotObjectBase` and
`QObjectPrivate::connect(QObject*,int,QObject*,QtPrivate::QSlotObjectBase*)`
(*pysideqslotobject.cpp*). This could in principle enable removing
`GlobalReceiverV2`, but requires keeping the `QMetaObject::Connection` for
disconnecting.
