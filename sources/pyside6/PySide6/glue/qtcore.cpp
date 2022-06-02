/****************************************************************************
**
** Copyright (C) 2018 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:LGPL$
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** GNU Lesser General Public License Usage
** Alternatively, this file may be used under the terms of the GNU Lesser
** General Public License version 3 as published by the Free Software
** Foundation and appearing in the file LICENSE.LGPL3 included in the
** packaging of this file. Please review the following information to
** ensure the GNU Lesser General Public License version 3 requirements
** will be met: https://www.gnu.org/licenses/lgpl-3.0.html.
**
** GNU General Public License Usage
** Alternatively, this file may be used under the terms of the GNU
** General Public License version 2.0 or (at your option) the GNU General
** Public license version 3 or any later version approved by the KDE Free
** Qt Foundation. The licenses are as published by the Free Software
** Foundation and appearing in the file LICENSE.GPL2 and LICENSE.GPL3
** included in the packaging of this file. Please review the following
** information to ensure the GNU General Public License requirements will
** be met: https://www.gnu.org/licenses/gpl-2.0.html and
** https://www.gnu.org/licenses/gpl-3.0.html.
**
** $QT_END_LICENSE$
**
****************************************************************************/

/*********************************************************************
 * INJECT CODE
 ********************************************************************/

// @snippet include-pyside
#include <pysideinit.h>
#include <limits>
#include "glue/core_snippets_p.h"
// @snippet include-pyside

// @snippet qsettings-value
// If we enter the kwds, means that we have a defaultValue or
// at least a type.
// This avoids that we are passing '0' as defaultValue.
// defaultValue can also be passed as positional argument,
// not only as keyword.
// PySide-535: Allow for empty dict instead of nullptr in PyPy
QVariant out;
if ((kwds && PyDict_Size(kwds) > 0) || numArgs > 1) {
    Py_BEGIN_ALLOW_THREADS
    out = %CPPSELF.value(%1, %2);
    Py_END_ALLOW_THREADS
} else {
    Py_BEGIN_ALLOW_THREADS
    out = %CPPSELF.value(%1);
    Py_END_ALLOW_THREADS
}

PyTypeObject *typeObj = reinterpret_cast<PyTypeObject*>(%PYARG_3);

if (typeObj && !Shiboken::ObjectType::checkType(typeObj)) {
    if (typeObj == &PyList_Type) {
        QByteArray out_ba = out.toByteArray();
        if (!out_ba.isEmpty()) {
            QByteArrayList valuesList = out_ba.split(',');
            const Py_ssize_t valuesSize = valuesList.size();
            if (valuesSize > 0) {
                PyObject *list = PyList_New(valuesSize);
                for (Py_ssize_t i = 0; i < valuesSize; ++i) {
                    PyObject *item = PyUnicode_FromString(valuesList.at(i).constData());
                    PyList_SET_ITEM(list, i, item);
                }
                %PYARG_0 = list;

            } else {
                %PYARG_0 = %CONVERTTOPYTHON[QVariant](out);
            }
        } else {
            %PYARG_0 = PyList_New(0);
        }
    } else if (typeObj == &PyBytes_Type) {
        QByteArray asByteArray = out.toByteArray();
        %PYARG_0 = PyBytes_FromString(asByteArray.constData());
    } else if (typeObj == &PyUnicode_Type) {
        QByteArray asByteArray = out.toByteArray();
        %PYARG_0 = PyUnicode_FromString(asByteArray.constData());
    } else if (typeObj == &PyLong_Type) {
        float asFloat = out.toFloat();
        pyResult = PyLong_FromDouble(asFloat);
    } else if (typeObj == &PyFloat_Type) {
        float asFloat = out.toFloat();
        %PYARG_0 = PyFloat_FromDouble(asFloat);
    } else if (typeObj == &PyBool_Type) {
        if (out.toBool()) {
            Py_INCREF(Py_True);
            %PYARG_0 = Py_True;
        } else {
            Py_INCREF(Py_False);
            %PYARG_0 = Py_False;
        }
    } else {
        // TODO: PyDict_Type and PyTuple_Type
        PyErr_SetString(PyExc_TypeError,
                        "Invalid type parameter.\n"
                        "\tUse 'list', 'bytes', 'str', 'int', 'float', 'bool', "
                        "or a Qt-derived type");
        return nullptr;
    }
}
else {
    if (!out.isValid()) {
        Py_INCREF(Py_None);
        %PYARG_0 = Py_None;
    } else {
        %PYARG_0 = %CONVERTTOPYTHON[QVariant](out);
    }
}

// @snippet qsettings-value

// @snippet conversion-pytypeobject-qmetatype
auto *pyType = reinterpret_cast<PyTypeObject *&>(%in);
if (Shiboken::String::checkType(pyType))
    %out = QMetaType(QMetaType::QString);
else if (%in == reinterpret_cast<PyObject *>(&PyFloat_Type))
    %out = QMetaType(QMetaType::Double);
else if (%in == reinterpret_cast<PyObject *>(&PyLong_Type))
    %out = QMetaType(QMetaType::Int);
else if (Py_TYPE(%in) == SbkObjectType_TypeF())
    %out = QMetaType::fromName(Shiboken::ObjectType::getOriginalName(pyType));
else
    %out = QMetaType::fromName(pyType->tp_name);
// @snippet conversion-pytypeobject-qmetatype

// @snippet conversion-qmetatype-pytypeobject
auto pyType = Shiboken::Conversions::getPythonTypeObject(%in.name());
%out = pyType ? (reinterpret_cast<PyObject *>(pyType)) : Py_None;
Py_INCREF(%out);
return %out;
// @snippet conversion-qmetatype-pytypeobject

// @snippet qvariant-conversion
static QVariant QVariant_convertToVariantMap(PyObject *map)
{
    Py_ssize_t pos = 0;
    Shiboken::AutoDecRef keys(PyDict_Keys(map));
    if (!QVariant_isStringList(keys))
        return QVariant();
    PyObject *key;
    PyObject *value;
    QMap<QString,QVariant> ret;
    while (PyDict_Next(map, &pos, &key, &value)) {
        QString cppKey = %CONVERTTOCPP[QString](key);
        QVariant cppValue = %CONVERTTOCPP[QVariant](value);
        ret.insert(cppKey, cppValue);
    }
    return QVariant(ret);
}
static QVariant QVariant_convertToVariantList(PyObject *list)
{
    if (QVariant_isStringList(list)) {
        QList<QString > lst = %CONVERTTOCPP[QList<QString>](list);
        return QVariant(QStringList(lst));
    }
    QVariant valueList = QVariant_convertToValueList(list);
    if (valueList.isValid())
        return valueList;

    if (PySequence_Size(list) < 0) {
        // clear the error if < 0 which means no length at all
        PyErr_Clear();
        return QVariant();
    }

    QList<QVariant> lst;
    Shiboken::AutoDecRef fast(PySequence_Fast(list, "Failed to convert QVariantList"));
    const Py_ssize_t size = PySequence_Fast_GET_SIZE(fast.object());
    for (Py_ssize_t i = 0; i < size; ++i) {
        PyObject *pyItem = PySequence_Fast_GET_ITEM(fast.object(), i);
        QVariant item = %CONVERTTOCPP[QVariant](pyItem);
        lst.append(item);
    }
    return QVariant(lst);
}
// @snippet qvariant-conversion

// @snippet qt-qabs
double _abs = qAbs(%1);
%PYARG_0 = %CONVERTTOPYTHON[double](_abs);
// @snippet qt-qabs

// @snippet qt-addpostroutine
PySide::addPostRoutine(%1);
// @snippet qt-addpostroutine

// @snippet qt-qaddpostroutine
qAddPostRoutine(PySide::globalPostRoutineCallback);
// @snippet qt-qaddpostroutine

// @snippet qt-version
QList<QByteArray> version = QByteArray(qVersion()).split('.');
PyObject *pyQtVersion = PyTuple_New(3);
for (int i = 0; i < 3; ++i)
    PyTuple_SET_ITEM(pyQtVersion, i, PyLong_FromLong(version[i].toInt()));
PyModule_AddObject(module, "__version_info__", pyQtVersion);
PyModule_AddStringConstant(module, "__version__", qVersion());
// @snippet qt-version

// @snippet qobject-connect
#include <qobjectconnect.h>
// @snippet qobject-connect

// @snippet qobject-connect-1
// %FUNCTION_NAME() - disable generation of function call.
%RETURN_TYPE %0 = PySide::qobjectConnect(%1, %2, %CPPSELF, %3, %4);
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet qobject-connect-1

// @snippet qobject-connect-2
// %FUNCTION_NAME() - disable generation of function call.
%RETURN_TYPE %0 = PySide::qobjectConnect(%1, %2, %3, %4, %5);
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet qobject-connect-2

// @snippet qobject-connect-3
// %FUNCTION_NAME() - disable generation of function call.
%RETURN_TYPE %0 = PySide::qobjectConnect(%1, %2, %3, %4, %5);
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet qobject-connect-3

// @snippet qobject-connect-4
// %FUNCTION_NAME() - disable generation of function call.
%RETURN_TYPE %0 = PySide::qobjectConnectCallback(%1, %2, %PYARG_3, %4);
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet qobject-connect-4

// @snippet qobject-connect-5
// %FUNCTION_NAME() - disable generation of function call.
%RETURN_TYPE %0 = PySide::qobjectConnectCallback(%CPPSELF, %1, %PYARG_2, %3);
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet qobject-connect-5

// @snippet qobject-connect-6
// %FUNCTION_NAME() - disable generation of function call.
%RETURN_TYPE %0 = PySide::qobjectConnect(%CPPSELF, %1, %2, %3, %4);
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet qobject-connect-6

// @snippet qobject-emit
%RETURN_TYPE %0 = PySide::SignalManager::instance().emitSignal(%CPPSELF, %1, %PYARG_2);
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet qobject-emit

// @snippet qobject-disconnect-1
// %FUNCTION_NAME() - disable generation of function call.
%RETURN_TYPE %0 = PySide::qobjectDisconnectCallback(%CPPSELF, %1, %2);
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet qobject-disconnect-1

// @snippet qobject-disconnect-2
// %FUNCTION_NAME() - disable generation of function call.
%RETURN_TYPE %0 = PySide::qobjectDisconnectCallback(%1, %2, %3);
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet qobject-disconnect-2

// @snippet qfatal
// qFatal doesn't have a stream version, so we do a
// qWarning call followed by a qFatal() call using a
// literal.
Py_BEGIN_ALLOW_THREADS
qWarning() << %1;
qFatal("[A qFatal() call was made from Python code]");
Py_END_ALLOW_THREADS
// @snippet qfatal

// @snippet moduleshutdown
PySide::runCleanupFunctions();
// @snippet moduleshutdown

// @snippet qt-qenum
%PYARG_0 = PySide::QEnum::QEnumMacro(%1, false);
// @snippet qt-qenum

// @snippet qt-qflag
%PYARG_0 = PySide::QEnum::QEnumMacro(%1, true);
// @snippet qt-qflag

// @snippet qt-init-feature
PySide::Feature::init();
// @snippet qt-init-feature

// @snippet qt-pysideinit
Shiboken::Conversions::registerConverterName(SbkPySide6_QtCoreTypeConverters[SBK_QSTRING_IDX], "unicode");
Shiboken::Conversions::registerConverterName(SbkPySide6_QtCoreTypeConverters[SBK_QSTRING_IDX], "str");
Shiboken::Conversions::registerConverterName(SbkPySide6_QtCoreTypeConverters[SBK_QTCORE_QLIST_QVARIANT_IDX], "QVariantList");
Shiboken::Conversions::registerConverterName(SbkPySide6_QtCoreTypeConverters[SBK_QTCORE_QMAP_QSTRING_QVARIANT_IDX], "QVariantMap");

PySide::registerInternalQtConf();
PySide::init(module);
Py_AtExit(QtCoreModuleExit);
// @snippet qt-pysideinit

// @snippet qt-messagehandler
// Define a global variable to handle qInstallMessageHandler callback
static PyObject *qtmsghandler = nullptr;

static void msgHandlerCallback(QtMsgType type, const QMessageLogContext &ctx, const QString &msg)
{
    Shiboken::GilState state;
    Shiboken::AutoDecRef arglist(PyTuple_New(3));
    PyTuple_SET_ITEM(arglist, 0, %CONVERTTOPYTHON[QtMsgType](type));
    PyTuple_SET_ITEM(arglist, 1, %CONVERTTOPYTHON[QMessageLogContext &](ctx));
    QByteArray array = msg.toUtf8();  // Python handler requires UTF-8
    const char *data = array.constData();
    PyTuple_SET_ITEM(arglist, 2, %CONVERTTOPYTHON[const char *](data));
    Shiboken::AutoDecRef ret(PyObject_CallObject(qtmsghandler, arglist));
}
static void QtCoreModuleExit()
{
    PySide::SignalManager::instance().clear();
}
// @snippet qt-messagehandler

// @snippet qt-installmessagehandler
if (%PYARG_1 == Py_None) {
  qInstallMessageHandler(0);
  %PYARG_0 = qtmsghandler ? qtmsghandler : Py_None;
  qtmsghandler = 0;
} else if (!PyCallable_Check(%PYARG_1)) {
  PyErr_SetString(PyExc_TypeError, "parameter must be callable");
} else {
  %PYARG_0 = qtmsghandler ? qtmsghandler : Py_None;
  Py_INCREF(%PYARG_1);
  qtmsghandler = %PYARG_1;
  qInstallMessageHandler(msgHandlerCallback);
}

if (%PYARG_0 == Py_None)
    Py_INCREF(%PYARG_0);
// @snippet qt-installmessagehandler

// @snippet qline-hash
namespace PySide {
    template<> inline Py_ssize_t hash(const QLine &l)
    {
        const int v[4] = {l.x1(), l.y1(), l.x2(), l.y2()};
        return qHashRange(v, v + 4);
    }
};
// @snippet qline-hash

// @snippet qlinef-intersect
QPointF p;
%RETURN_TYPE retval = %CPPSELF.%FUNCTION_NAME(%ARGUMENT_NAMES, &p);
%PYARG_0 = PyTuple_New(2);
PyTuple_SET_ITEM(%PYARG_0, 0, %CONVERTTOPYTHON[%RETURN_TYPE](retval));
PyTuple_SET_ITEM(%PYARG_0, 1, %CONVERTTOPYTHON[QPointF](p));
// @snippet qlinef-intersect

// @snippet qresource-data
const void *d = %CPPSELF.%FUNCTION_NAME();
if (d) {
    %PYARG_0 = Shiboken::Buffer::newObject(d, %CPPSELF.size());
} else {
    Py_INCREF(Py_None);
    %PYARG_0 = Py_None;
}
// @snippet qresource-data

// @snippet qdate-topython
if (!PyDateTimeAPI)
    PyDateTime_IMPORT;
%PYARG_0 = PyDate_FromDate(%CPPSELF.year(), %CPPSELF.month(), %CPPSELF.day());
// @snippet qdate-topython

// @snippet qdate-getdate
int year, month, day;
%CPPSELF.%FUNCTION_NAME(&year, &month, &day);
%PYARG_0 = PyTuple_New(3);
PyTuple_SET_ITEM(%PYARG_0, 0, %CONVERTTOPYTHON[int](year));
PyTuple_SET_ITEM(%PYARG_0, 1, %CONVERTTOPYTHON[int](month));
PyTuple_SET_ITEM(%PYARG_0, 2, %CONVERTTOPYTHON[int](day));
// @snippet qdate-getdate

// @snippet qdate-weeknumber
int yearNumber;
int week = %CPPSELF.%FUNCTION_NAME(&yearNumber);
%PYARG_0 = PyTuple_New(2);
PyTuple_SET_ITEM(%PYARG_0, 0, %CONVERTTOPYTHON[int](week));
PyTuple_SET_ITEM(%PYARG_0, 1, %CONVERTTOPYTHON[int](yearNumber));
// @snippet qdate-weeknumber

// @snippet qdatetime-1
QDate date(%1, %2, %3);
QTime time(%4, %5, %6, %7);
%0 = new %TYPE(date, time, Qt::TimeSpec(%8));
// @snippet qdatetime-1

// @snippet qdatetime-2
QDate date(%1, %2, %3);
QTime time(%4, %5, %6);
%0 = new %TYPE(date, time);
// @snippet qdatetime-2

// @snippet qdatetime-topython
QDate date = %CPPSELF.date();
QTime time = %CPPSELF.time();
if (!PyDateTimeAPI)
    PyDateTime_IMPORT;
%PYARG_0 = PyDateTime_FromDateAndTime(date.year(), date.month(), date.day(), time.hour(), time.minute(), time.second(), time.msec()*1000);
// @snippet qdatetime-topython

// @snippet qpoint
namespace PySide {
    template<> inline Py_ssize_t hash(const QPoint &v) {
        return qHash(qMakePair(v.x(), v.y()));
    }
};
// @snippet qpoint

// @snippet qrect
namespace PySide {
    template<> inline Py_ssize_t hash(const QRect &r) {
        const int v[4] = {r.x(), r.y(), r.width(), r.height()};
        return qHashRange(v, v + 4);
    }
};
// @snippet qrect

// @snippet qsize
namespace PySide {
    template<> inline Py_ssize_t hash(const QSize &v) {
        return qHash(qMakePair(v.width(), v.height()));
    }
};
// @snippet qsize

// @snippet qtime-topython
if (!PyDateTimeAPI)
    PyDateTime_IMPORT;
%PYARG_0 = PyTime_FromTime(%CPPSELF.hour(), %CPPSELF.minute(), %CPPSELF.second(), %CPPSELF.msec()*1000);
// @snippet qtime-topython

// @snippet qbitarray-len
return %CPPSELF.size();
// @snippet qbitarray-len

// @snippet qbitarray-getitem
if (_i < 0 || _i >= %CPPSELF.size()) {
    PyErr_SetString(PyExc_IndexError, "index out of bounds");
    return 0;
}
bool ret = %CPPSELF.at(_i);
return %CONVERTTOPYTHON[bool](ret);
// @snippet qbitarray-getitem

// @snippet qbitarray-setitem
PyObject *args = Py_BuildValue("(iiO)", _i, 1, _value);
PyObject *result = Sbk_QBitArrayFunc_setBit(self, args);
Py_DECREF(args);
Py_XDECREF(result);
return !result ? -1 : 0;
// @snippet qbitarray-setitem

// @snippet default-enter
Py_INCREF(%PYSELF);
pyResult = %PYSELF;
// @snippet default-enter

// @snippet qsignalblocker-unblock
%CPPSELF.unblock();
// @snippet qsignalblocker-unblock

// @snippet unlock
%CPPSELF.unlock();
// @snippet unlock

// @snippet qabstractitemmodel-createindex
%RETURN_TYPE %0 = %CPPSELF.%FUNCTION_NAME(%1, %2, %PYARG_3);
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet qabstractitemmodel-createindex

// @snippet qabstractitemmodel
qRegisterMetaType<QList<int> >("QList<int>");
// @snippet qabstractitemmodel

// @snippet qobject-metaobject
%RETURN_TYPE %0 = %CPPSELF.%FUNCTION_NAME();
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet qobject-metaobject

// @snippet qobject-findchild-2
QObject *child = qObjectFindChild(%CPPSELF, %2, reinterpret_cast<PyTypeObject *>(%PYARG_1), %3);
%PYARG_0 = %CONVERTTOPYTHON[QObject *](child);
// @snippet qobject-findchild-2

// @snippet qobject-findchildren
%PYARG_0 = PyList_New(0);
qObjectFindChildren(%CPPSELF, %2, reinterpret_cast<PyTypeObject *>(%PYARG_1), %3,
                    [%PYARG_0](QObject *child) {
                        Shiboken::AutoDecRef pyChild(%CONVERTTOPYTHON[QObject *](child));
                        PyList_Append(%PYARG_0, pyChild.object());
                    });
// @snippet qobject-findchildren

// @snippet qobject-tr
const QString result = qObjectTr(reinterpret_cast<PyTypeObject *>(%PYSELF), %1, %2, %3);
%PYARG_0 = %CONVERTTOPYTHON[QString](result);
// @snippet qobject-tr

// @snippet qobject-receivers
// Avoid return +1 because SignalManager connect to "destroyed()" signal to control object timelife
int ret = %CPPSELF.%FUNCTION_NAME(%1);
if (ret > 0 && ((strcmp(%1, SIGNAL(destroyed())) == 0) || (strcmp(%1, SIGNAL(destroyed(QObject*))) == 0)))
    ret -= PySide::SignalManager::instance().countConnectionsWith(%CPPSELF);

%PYARG_0 = %CONVERTTOPYTHON[int](ret);
// @snippet qobject-receivers

// @snippet qbytearray-mgetitem
if (PepIndex_Check(_key)) {
    const Py_ssize_t _i = PyNumber_AsSsize_t(_key, PyExc_IndexError);
    if (_i < 0 || _i >= %CPPSELF.size()) {
        PyErr_SetString(PyExc_IndexError, "index out of bounds");
        return nullptr;
    }
    char res[2] = {%CPPSELF.at(_i), '\0'};
    return PyBytes_FromStringAndSize(res, 1);
}

if (PySlice_Check(_key) == 0) {
    PyErr_Format(PyExc_TypeError,
                 "list indices must be integers or slices, not %.200s",
                 Py_TYPE(_key)->tp_name);
    return nullptr;
}

Py_ssize_t start, stop, step, slicelength;
if (PySlice_GetIndicesEx(_key, %CPPSELF.size(), &start, &stop, &step, &slicelength) < 0)
    return nullptr;

QByteArray ba;
if (slicelength <= 0)
    return %CONVERTTOPYTHON[QByteArray](ba);

if (step == 1) {
    Py_ssize_t max = %CPPSELF.size();
    start = qBound(Py_ssize_t(0), start, max);
    stop = qBound(Py_ssize_t(0), stop, max);
    if (start < stop)
        ba = %CPPSELF.mid(start, stop - start);
    return %CONVERTTOPYTHON[QByteArray](ba);
}

for (Py_ssize_t cur = start; slicelength > 0; cur += step, --slicelength)
    ba.append(%CPPSELF.at(cur));

return %CONVERTTOPYTHON[QByteArray](ba);
// @snippet qbytearray-mgetitem

// @snippet qbytearray-msetitem
if (PepIndex_Check(_key)) {
    Py_ssize_t _i = PyNumber_AsSsize_t(_key, PyExc_IndexError);
    if (_i == -1 && PyErr_Occurred())
        return -1;

    if (_i < 0)
        _i += %CPPSELF.size();

    if (_i < 0 || _i >= %CPPSELF.size()) {
        PyErr_SetString(PyExc_IndexError, "QByteArray index out of range");
        return -1;
    }

    // Provide more specific error message for bytes/str, bytearray, QByteArray respectively
    if (PyBytes_Check(_value)) {
        if (Py_SIZE(_value) != 1) {
            PyErr_SetString(PyExc_ValueError, "bytes must be of size 1");
            return -1;
        }
    } else if (PyByteArray_Check(_value)) {
        if (Py_SIZE(_value) != 1) {
            PyErr_SetString(PyExc_ValueError, "bytearray must be of size 1");
            return -1;
        }
    } else if (Py_TYPE(_value) == reinterpret_cast<PyTypeObject *>(SbkPySide6_QtCoreTypes[SBK_QBYTEARRAY_IDX])) {
        if (PyObject_Length(_value) != 1) {
            PyErr_SetString(PyExc_ValueError, "QByteArray must be of size 1");
            return -1;
        }
    } else {
        PyErr_SetString(PyExc_ValueError, "a bytes, bytearray, QByteArray of size 1 is required");
        return -1;
    }

    // Not support int or long.
    %CPPSELF.remove(_i, 1);
    PyObject *args = Py_BuildValue("(nO)", _i, _value);
    PyObject *result = Sbk_QByteArrayFunc_insert(self, args);
    Py_DECREF(args);
    Py_XDECREF(result);
    return result != nullptr ? 0: -1;
}

if (PySlice_Check(_key) == 0) {
    PyErr_Format(PyExc_TypeError, "QBytearray indices must be integers or slices, not %.200s",
                 Py_TYPE(_key)->tp_name);
    return -1;
}

Py_ssize_t start, stop, step, slicelength;
if (PySlice_GetIndicesEx(_key, %CPPSELF.size(), &start, &stop, &step, &slicelength) < 0)
    return -1;

// The parameter candidates are: bytes/str, bytearray, QByteArray itself.
// Not supported are iterables containing ints between 0~255
// case 1: value is nullpre, means delete the items within the range
// case 2: step is 1, means shrink or expand
// case 3: step is not 1, then the number of slots have to equal the number of items in _value
Py_ssize_t value_length = 0;
if (_value != nullptr && _value != Py_None) {
    if (!(PyBytes_Check(_value) || PyByteArray_Check(_value)
          || Py_TYPE(_value) == reinterpret_cast<PyTypeObject *>(SbkPySide6_QtCoreTypes[SBK_QBYTEARRAY_IDX]))) {
           PyErr_Format(PyExc_TypeError, "bytes, bytearray or QByteArray is required, not %.200s",
                        Py_TYPE(_value)->tp_name);
           return -1;
    }
    value_length = PyObject_Length(_value);
}

if (step != 1 && value_length != slicelength) {
    PyErr_Format(PyExc_ValueError, "attempt to assign %s of size %d to extended slice of size %d",
                 Py_TYPE(_value)->tp_name, int(value_length), int(slicelength));
    return -1;
}

if (step != 1) {
    Py_ssize_t i = start;
    for (Py_ssize_t j = 0; j < slicelength; ++j) {
        PyObject *item = PyObject_GetItem(_value, PyLong_FromSsize_t(j));
        QByteArray temp;
        if (PyLong_Check(item)) {
            int overflow;
            const long ival = PyLong_AsLongAndOverflow(item, &overflow);
            // Not supposed to be bigger than 255 because only bytes,
            // bytearray, QByteArray were accepted
            temp.append(char(ival));
        } else {
            temp = %CONVERTTOCPP[QByteArray](item);
        }
        %CPPSELF.replace(i, 1, temp);
        i += step;
    }
    return 0;
}

QByteArray ba = %CONVERTTOCPP[QByteArray](_value);
%CPPSELF.replace(start, slicelength, ba);
return 0;
// @snippet qbytearray-msetitem

// @snippet qbytearray-bufferprotocol
extern "C" {
// QByteArray buffer protocol functions
// see: http://www.python.org/dev/peps/pep-3118/

static int SbkQByteArray_getbufferproc(PyObject *obj, Py_buffer *view, int flags)
{
    if (!view || !Shiboken::Object::isValid(obj))
        return -1;

    QByteArray * cppSelf = %CONVERTTOCPP[QByteArray *](obj);
    //XXX      /|\ omitting this space crashes shiboken!
 #ifdef Py_LIMITED_API
    view->obj = obj;
    view->buf = reinterpret_cast<void *>(cppSelf->data());
    view->len = cppSelf->size();
    view->readonly = 0;
    view->itemsize = 1;
    view->format = const_cast<char *>("c");
    view->ndim = 1;
    view->shape = (flags & PyBUF_ND) == PyBUF_ND ? &(view->len) : nullptr;
    view->strides = &view->itemsize;
    view->suboffsets = nullptr;
    view->internal = nullptr;

    Py_XINCREF(obj);
    return 0;
#else // Py_LIMITED_API
    const int result = PyBuffer_FillInfo(view, obj, reinterpret_cast<void *>(cppSelf->data()),
                                         cppSelf->size(), 0, flags);
    if (result == 0)
        Py_XINCREF(obj);
    return result;
#endif
}

static PyBufferProcs SbkQByteArrayBufferProc = {
    /*bf_getbuffer*/  (getbufferproc)SbkQByteArray_getbufferproc,
    /*bf_releasebuffer*/ (releasebufferproc)0,
};

}
// @snippet qbytearray-bufferprotocol

// @snippet qbytearray-operatorplus-1
QByteArray ba = QByteArray(PyBytes_AS_STRING(%PYARG_1), PyBytes_GET_SIZE(%PYARG_1)) + *%CPPSELF;
%PYARG_0 = %CONVERTTOPYTHON[QByteArray](ba);
// @snippet qbytearray-operatorplus-1

// @snippet qbytearray-operatorplus-2
QByteArray ba = QByteArray(PyByteArray_AsString(%PYARG_1), PyByteArray_Size(%PYARG_1)) + *%CPPSELF;
%PYARG_0 = %CONVERTTOPYTHON[QByteArray](ba);
// @snippet qbytearray-operatorplus-2

// @snippet qbytearray-operatorplus-3
QByteArray ba = *%CPPSELF + QByteArray(PyByteArray_AsString(%PYARG_1), PyByteArray_Size(%PYARG_1));
%PYARG_0 = %CONVERTTOPYTHON[QByteArray](ba);
// @snippet qbytearray-operatorplus-3

// @snippet qbytearray-operatorplusequal
*%CPPSELF += QByteArray(PyByteArray_AsString(%PYARG_1), PyByteArray_Size(%PYARG_1));
// @snippet qbytearray-operatorplusequal

// @snippet qbytearray-operatorequalequal
if (PyUnicode_CheckExact(%PYARG_1)) {
    Shiboken::AutoDecRef data(PyUnicode_AsASCIIString(%PYARG_1));
    QByteArray ba = QByteArray(PyBytes_AsString(data.object()), PyBytes_GET_SIZE(data.object()));
    bool cppResult = %CPPSELF == ba;
    %PYARG_0 = %CONVERTTOPYTHON[bool](cppResult);
}
// @snippet qbytearray-operatorequalequal

// @snippet qbytearray-operatornotequal
if (PyUnicode_CheckExact(%PYARG_1)) {
    Shiboken::AutoDecRef data(PyUnicode_AsASCIIString(%PYARG_1));
    QByteArray ba = QByteArray(PyBytes_AsString(data.object()), PyBytes_GET_SIZE(data.object()));
    bool cppResult = %CPPSELF != ba;
    %PYARG_0 = %CONVERTTOPYTHON[bool](cppResult);
}
// @snippet qbytearray-operatornotequal

// @snippet qbytearray-operatorgreater
if (PyUnicode_CheckExact(%PYARG_1)) {
    Shiboken::AutoDecRef data(PyUnicode_AsASCIIString(%PYARG_1));
    QByteArray ba = QByteArray(PyBytes_AsString(data.object()), PyBytes_GET_SIZE(data.object()));
    bool cppResult = %CPPSELF > ba;
    %PYARG_0 = %CONVERTTOPYTHON[bool](cppResult);
}
// @snippet qbytearray-operatorgreater

// @snippet qbytearray-operatorgreaterequal
if (PyUnicode_CheckExact(%PYARG_1)) {
    Shiboken::AutoDecRef data(PyUnicode_AsASCIIString(%PYARG_1));
    QByteArray ba = QByteArray(PyBytes_AsString(data.object()), PyBytes_GET_SIZE(data.object()));
    bool cppResult = %CPPSELF >= ba;
    %PYARG_0 = %CONVERTTOPYTHON[bool](cppResult);
}
// @snippet qbytearray-operatorgreaterequal

// @snippet qbytearray-operatorlower
if (PyUnicode_CheckExact(%PYARG_1)) {
    Shiboken::AutoDecRef data(PyUnicode_AsASCIIString(%PYARG_1));
    QByteArray ba = QByteArray(PyBytes_AsString(data.object()), PyBytes_GET_SIZE(data.object()));
    bool cppResult = %CPPSELF < ba;
    %PYARG_0 = %CONVERTTOPYTHON[bool](cppResult);
}
// @snippet qbytearray-operatorlower

// @snippet qbytearray-operatorlowerequal
if (PyUnicode_CheckExact(%PYARG_1)) {
    Shiboken::AutoDecRef data(PyUnicode_AsASCIIString(%PYARG_1));
    QByteArray ba = QByteArray(PyBytes_AsString(data.object()), PyBytes_GET_SIZE(data.object()));
    bool cppResult = %CPPSELF <= ba;
    %PYARG_0 = %CONVERTTOPYTHON[bool](cppResult);
}
// @snippet qbytearray-operatorlowerequal

// @snippet qbytearray-repr
PyObject *aux = PyBytes_FromStringAndSize(%CPPSELF.constData(), %CPPSELF.size());
if (aux == nullptr) {
    return nullptr;
}
QByteArray b(Py_TYPE(%PYSELF)->tp_name);
%PYARG_0 = PyUnicode_FromFormat("%s(%R)", b.constData(), aux);
Py_DECREF(aux);
// @snippet qbytearray-repr

// @snippet qbytearray-2
%0 = new QByteArray(PyByteArray_AsString(%PYARG_1), PyByteArray_Size(%PYARG_1));
// @snippet qbytearray-2

// @snippet qbytearray-3
%0 = new QByteArray(PyBytes_AS_STRING(%PYARG_1), PyBytes_GET_SIZE(%PYARG_1));
// @snippet qbytearray-3

// @snippet qbytearray-py3
PepType_AS_BUFFER(Shiboken::SbkType<QByteArray>()) = &SbkQByteArrayBufferProc;
// @snippet qbytearray-py3

// @snippet qbytearray-data
%PYARG_0 = PyBytes_FromStringAndSize(%CPPSELF.%FUNCTION_NAME(), %CPPSELF.size());
// @snippet qbytearray-data

// @snippet qbytearray-str
PyObject *aux = PyBytes_FromStringAndSize(%CPPSELF.constData(), %CPPSELF.size());
if (aux == nullptr) {
    return nullptr;
}
%PYARG_0 = PyObject_Repr(aux);
Py_DECREF(aux);
// @snippet qbytearray-str

// @snippet qbytearray-len
return %CPPSELF.size();
// @snippet qbytearray-len

// @snippet qbytearray-getitem
if (_i < 0 || _i >= %CPPSELF.size()) {
    PyErr_SetString(PyExc_IndexError, "index out of bounds");
    return 0;
} else {
    char res[2];
    res[0] = %CPPSELF.at(_i);
    res[1] = 0;
    return PyBytes_FromStringAndSize(res, 1);
}
// @snippet qbytearray-getitem

// @snippet qbytearray-setitem
%CPPSELF.remove(_i, 1);
PyObject *args = Py_BuildValue("(nO)", _i, _value);
PyObject *result = Sbk_QByteArrayFunc_insert(self, args);
Py_DECREF(args);
Py_XDECREF(result);
return !result ? -1 : 0;
// @snippet qbytearray-setitem

// @snippet qfiledevice-unmap
uchar *ptr = reinterpret_cast<uchar *>(Shiboken::Buffer::getPointer(%PYARG_1));
%RETURN_TYPE %0 = %CPPSELF.%FUNCTION_NAME(ptr);
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet qfiledevice-unmap

// @snippet qfiledevice-map
%PYARG_0 = Shiboken::Buffer::newObject(%CPPSELF.%FUNCTION_NAME(%1, %2, %3), %2, Shiboken::Buffer::ReadWrite);
// @snippet qfiledevice-map

// @snippet qiodevice-readdata
QByteArray ba(1 + qsizetype(%2), char(0));
%CPPSELF.%FUNCTION_NAME(ba.data(), qint64(%2));
%PYARG_0 = Shiboken::String::fromCString(ba.constData());
// @snippet qiodevice-readdata

// @snippet qcryptographichash-adddata
%CPPSELF.%FUNCTION_NAME(Shiboken::String::toCString(%PYARG_1), Shiboken::String::len(%PYARG_1));
// @snippet qcryptographichash-adddata

// @snippet qmetaobject-repr
const QByteArray repr = PySide::MetaObjectBuilder::formatMetaObject(%CPPSELF).toUtf8();
%PYARG_0 = PyUnicode_FromString(repr.constData());
// @snippet qmetaobject-repr

// @snippet qsocketdescriptor
#ifdef WIN32
using DescriptorType = Qt::HANDLE;
#else
using DescriptorType = int;
#endif
// @snippet qsocketdescriptor

// @snippet qsocketnotifier
PyObject *socket = %PYARG_1;
if (socket != nullptr) {
    // We use qintptr as PyLong, but we check for int
    // since it is currently an alias to be Python2 compatible.
    // Internally, ints are qlonglongs.
    if (%CHECKTYPE[int](socket)) {
        int cppSocket = %CONVERTTOCPP[int](socket);
        qintptr socket = (qintptr)cppSocket;
        %0 = new %TYPE(socket, %2, %3);
    } else {
        PyErr_SetString(PyExc_TypeError,
            "QSocketNotifier: first argument (socket) must be an int.");
    }
}
// @snippet qsocketnotifier

// @snippet qtranslator-load
Py_ssize_t size;
auto *ptr = reinterpret_cast<uchar *>(Shiboken::Buffer::getPointer(%PYARG_1, &size));
%RETURN_TYPE %0 = %CPPSELF.%FUNCTION_NAME(const_cast<const uchar *>(ptr), size);
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet qtranslator-load

// @snippet qtimer-singleshot-1
// %FUNCTION_NAME() - disable generation of c++ function call
(void) %2; // remove warning about unused variable
Shiboken::AutoDecRef emptyTuple(PyTuple_New(0));
auto *timerType = Shiboken::SbkType<QTimer>();
auto *pyTimer = timerType->tp_new(Shiboken::SbkType<QTimer>(), emptyTuple, nullptr);
timerType->tp_init(pyTimer, emptyTuple, nullptr);

auto timer = %CONVERTTOCPP[QTimer *](pyTimer);
//XXX  /|\ omitting this space crashes shiboken!
Shiboken::AutoDecRef result(
    PyObject_CallMethod(pyTimer, "connect", "OsOs",
                        pyTimer,
                        SIGNAL(timeout()),
                        %PYARG_2,
                        %3)
);
Shiboken::Object::releaseOwnership(reinterpret_cast<SbkObject *>(pyTimer));
Py_XDECREF(pyTimer);
timer->setSingleShot(true);
timer->connect(timer, &QTimer::timeout, timer, &QObject::deleteLater);
timer->start(%1);
// @snippet qtimer-singleshot-1

// @snippet qtimer-singleshot-2
// %FUNCTION_NAME() - disable generation of c++ function call
Shiboken::AutoDecRef emptyTuple(PyTuple_New(0));
auto *timerType = Shiboken::SbkType<QTimer>();
auto *pyTimer = timerType->tp_new(Shiboken::SbkType<QTimer>(), emptyTuple, nullptr);
timerType->tp_init(pyTimer, emptyTuple, nullptr);
QTimer * timer = %CONVERTTOCPP[QTimer *](pyTimer);
timer->setSingleShot(true);

if (PyObject_TypeCheck(%2, PySideSignalInstance_TypeF())) {
    PySideSignalInstance *signalInstance = reinterpret_cast<PySideSignalInstance *>(%2);
    Shiboken::AutoDecRef signalSignature(Shiboken::String::fromFormat("2%s", PySide::Signal::getSignature(signalInstance)));
    Shiboken::AutoDecRef result(
        PyObject_CallMethod(pyTimer, "connect", "OsOO",
                            pyTimer,
                            SIGNAL(timeout()),
                            PySide::Signal::getObject(signalInstance),
                            signalSignature.object())
    );
} else {
    Shiboken::AutoDecRef result(
        PyObject_CallMethod(pyTimer, "connect", "OsO",
                            pyTimer,
                            SIGNAL(timeout()),
                            %PYARG_2)
    );
}

timer->connect(timer, &QTimer::timeout, timer, &QObject::deleteLater, Qt::DirectConnection);
Shiboken::Object::releaseOwnership(reinterpret_cast<SbkObject *>(pyTimer));
Py_XDECREF(pyTimer);
timer->start(%1);
// @snippet qtimer-singleshot-2

// @snippet qprocess-startdetached
qint64 pid;
%RETURN_TYPE retval = %TYPE::%FUNCTION_NAME(%1, %2, %3, &pid);
%PYARG_0 = PyTuple_New(2);
PyTuple_SET_ITEM(%PYARG_0, 0, %CONVERTTOPYTHON[%RETURN_TYPE](retval));
PyTuple_SET_ITEM(%PYARG_0, 1, %CONVERTTOPYTHON[qint64](pid));
// @snippet qprocess-startdetached

// @snippet qcoreapplication-init
static void QCoreApplicationConstructor(PyObject *self, PyObject *pyargv, QCoreApplicationWrapper **cptr)
{
    static int argc;
    static char **argv;
    PyObject *stringlist = PyTuple_GET_ITEM(pyargv, 0);
    if (Shiboken::listToArgcArgv(stringlist, &argc, &argv, "PySideApp")) {
        *cptr = new QCoreApplicationWrapper(argc, argv);
        Shiboken::Object::releaseOwnership(reinterpret_cast<SbkObject *>(self));
        PySide::registerCleanupFunction(&PySide::destroyQCoreApplication);
    }
}
// @snippet qcoreapplication-init

// @snippet qcoreapplication-1
QCoreApplicationConstructor(%PYSELF, args, &%0);
// @snippet qcoreapplication-1

// @snippet qcoreapplication-2
PyObject *empty = PyTuple_New(2);
if (!PyTuple_SetItem(empty, 0, PyList_New(0))) {
    QCoreApplicationConstructor(%PYSELF, empty, &%0);
}
// @snippet qcoreapplication-2

// @snippet qcoreapplication-instance
PyObject *pyApp = Py_None;
if (qApp) {
    pyApp = reinterpret_cast<PyObject *>(
        Shiboken::BindingManager::instance().retrieveWrapper(qApp));
    if (!pyApp)
        pyApp = %CONVERTTOPYTHON[QCoreApplication *](qApp);
        // this will keep app live after python exit (extra ref)
}
// PYSIDE-571: make sure that we return the singleton "None"
if (Py_TYPE(pyApp) == Py_TYPE(Py_None))
    Py_DECREF(MakeQAppWrapper(nullptr));
%PYARG_0 = pyApp;
Py_XINCREF(%PYARG_0);
// @snippet qcoreapplication-instance

// @snippet qdatastream-readrawdata
QByteArray data;
data.resize(%2);
int result = 0;
Py_BEGIN_ALLOW_THREADS
result = %CPPSELF.%FUNCTION_NAME(data.data(), data.size());
Py_END_ALLOW_THREADS
if (result == -1) {
    Py_INCREF(Py_None);
    %PYARG_0 = Py_None;
} else {
    %PYARG_0 = PyBytes_FromStringAndSize(data.constData(), result);
}
// @snippet qdatastream-readrawdata

// @snippet qdatastream-writerawdata
int r = 0;
Py_BEGIN_ALLOW_THREADS
r = %CPPSELF.%FUNCTION_NAME(%1, Shiboken::String::len(%PYARG_1));
Py_END_ALLOW_THREADS
%PYARG_0 = %CONVERTTOPYTHON[int](r);
// @snippet qdatastream-writerawdata

// @snippet releaseownership
Shiboken::Object::releaseOwnership(%PYARG_0);
// @snippet releaseownership

// @snippet qanimationgroup-clear
for (int counter = 0, count = %CPPSELF.animationCount(); counter < count; ++counter ) {
    QAbstractAnimation *animation = %CPPSELF.animationAt(counter);
    PyObject *obj = %CONVERTTOPYTHON[QAbstractAnimation *](animation);
    Shiboken::Object::setParent(nullptr, obj);
    Py_DECREF(obj);
}
%CPPSELF.clear();
// @snippet qanimationgroup-clear

// @snippet qeasingcurve
PySideEasingCurveFunctor::init();
// @snippet qeasingcurve

// @snippet qeasingcurve-setcustomtype
QEasingCurve::EasingFunction func = PySideEasingCurveFunctor::createCustomFuntion(%PYSELF, %PYARG_1);
if (func)
    %CPPSELF.%FUNCTION_NAME(func);
// @snippet qeasingcurve-setcustomtype

// @snippet qeasingcurve-customtype
//%FUNCTION_NAME()
%PYARG_0 = PySideEasingCurveFunctor::callable(%PYSELF);
// @snippet qeasingcurve-customtype

// @snippet qt-signal
%PYARG_0 = Shiboken::String::fromFormat("2%s",QMetaObject::normalizedSignature(%1).constData());
// @snippet qt-signal

// @snippet qt-slot
%PYARG_0 = Shiboken::String::fromFormat("1%s",QMetaObject::normalizedSignature(%1).constData());
// @snippet qt-slot

// @snippet qt-registerresourcedata
QT_BEGIN_NAMESPACE
extern bool
qRegisterResourceData(int,
                      const unsigned char *,
                      const unsigned char *,
                      const unsigned char *);

extern bool
qUnregisterResourceData(int,
                        const unsigned char *,
                        const unsigned char *,
                        const unsigned char *);
QT_END_NAMESPACE
// @snippet qt-registerresourcedata

// @snippet qt-qregisterresourcedata
%RETURN_TYPE %0 = %FUNCTION_NAME(%1, reinterpret_cast<uchar *>(PyBytes_AS_STRING(%PYARG_2)),
                                     reinterpret_cast<uchar *>(PyBytes_AS_STRING(%PYARG_3)),
                                     reinterpret_cast<uchar *>(PyBytes_AS_STRING(%PYARG_4)));
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet qt-qregisterresourcedata

// @snippet qt-qunregisterresourcedata
%RETURN_TYPE %0 = %FUNCTION_NAME(%1, reinterpret_cast<uchar *>(PyBytes_AS_STRING(%PYARG_2)),
                                     reinterpret_cast<uchar *>(PyBytes_AS_STRING(%PYARG_3)),
                                     reinterpret_cast<uchar *>(PyBytes_AS_STRING(%PYARG_4)));
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet qt-qunregisterresourcedata

// @snippet use-stream-for-format-security
// Uses the stream version for security reasons
// see gcc man page at -Wformat-security
Py_BEGIN_ALLOW_THREADS
%FUNCTION_NAME() << %1;
Py_END_ALLOW_THREADS
// @snippet use-stream-for-format-security

// @snippet qresource-registerResource
 auto ptr = reinterpret_cast<uchar *>(Shiboken::Buffer::getPointer(%PYARG_1));
 %RETURN_TYPE %0 = %CPPSELF.%FUNCTION_NAME(const_cast<const uchar *>(ptr), %2);
 %PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet qresource-registerResource

// @snippet qstring-return
%PYARG_0 = %CONVERTTOPYTHON[QString](%1);
// @snippet qstring-return

// @snippet stream-write-method
Py_BEGIN_ALLOW_THREADS
(*%CPPSELF) << %1;
Py_END_ALLOW_THREADS
// @snippet stream-write-method

// @snippet stream-read-method
%RETURN_TYPE _cpp_result;
Py_BEGIN_ALLOW_THREADS
(*%CPPSELF) >> _cpp_result;
Py_END_ALLOW_THREADS
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](_cpp_result);
// @snippet stream-read-method

// @snippet return-qstring-ref
QString &res = *%0;
%PYARG_0 = %CONVERTTOPYTHON[QString](res);
// @snippet return-qstring-ref

// @snippet return-readData
%RETURN_TYPE %0 = 0;
if (PyBytes_Check(%PYARG_0)) {
    %0 = PyBytes_GET_SIZE(%PYARG_0.object());
    memcpy(%1, PyBytes_AS_STRING(%PYARG_0.object()), %0);
} else if (Shiboken::String::check(%PYARG_0.object())) {
    %0 = Shiboken::String::len(%PYARG_0.object());
    memcpy(%1, Shiboken::String::toCString(%PYARG_0.object()), %0);
}
// @snippet return-readData

// @snippet qiodevice-readData
QByteArray ba(1 + qsizetype(%2), char(0));
Py_BEGIN_ALLOW_THREADS
%CPPSELF.%FUNCTION_NAME(ba.data(), qint64(%2));
Py_END_ALLOW_THREADS
%PYARG_0 = Shiboken::String::fromCString(ba.constData());
// @snippet qiodevice-readData

// @snippet qt-module-shutdown
{ // Avoid name clash
    Shiboken::AutoDecRef regFunc(static_cast<PyObject *>(nullptr));
    Shiboken::AutoDecRef atexit(Shiboken::Module::import("atexit"));
    if (atexit.isNull()) {
        qWarning("Module atexit not found for registering __moduleShutdown");
        PyErr_Clear();
    }else{
        regFunc.reset(PyObject_GetAttrString(atexit, "register"));
        if (regFunc.isNull()) {
            qWarning("Function atexit.register not found for registering __moduleShutdown");
            PyErr_Clear();
        }
    }
    if (!atexit.isNull() && !regFunc.isNull()){
        PyObject *shutDownFunc = PyObject_GetAttrString(module, "__moduleShutdown");
        Shiboken::AutoDecRef args(PyTuple_New(1));
        PyTuple_SET_ITEM(args, 0, shutDownFunc);
        Shiboken::AutoDecRef retval(PyObject_Call(regFunc, args, 0));
        Q_ASSERT(!retval.isNull());
    }
}
// @snippet qt-module-shutdown

// @snippet qthread_init_pypy
#ifdef PYPY_VERSION
// PYSIDE-535: PyPy 7.3.8 needs this call, which is actually a no-op in Python 3.9
//             This function should be replaced by a `Py_Initialize` call, but
//             that is still undefined. So we don't rely yet on any PyPy version.
PyEval_InitThreads();
#endif
// @snippet qthread_init_pypy

// @snippet qthread_exec_
if (PyErr_WarnEx(PyExc_DeprecationWarning,
                 "'exec_' will be removed in the future. "
                 "Use 'exec' instead.",
                 1)) {
    return nullptr;
}
%BEGIN_ALLOW_THREADS
#ifndef AVOID_PROTECTED_HACK
int cppResult = %CPPSELF.exec();
#else
int cppResult = static_cast<::QThreadWrapper *>(cppSelf)->QThreadWrapper::exec_protected();
#endif
%END_ALLOW_THREADS
%PYARG_0 = %CONVERTTOPYTHON[int](cppResult);
// @snippet qthread_exec_

// @snippet exec_
if (PyErr_WarnEx(PyExc_DeprecationWarning,
                 "'exec_' will be removed in the future. "
                 "Use 'exec' instead.",
                 1)) {
    return nullptr;
}
%BEGIN_ALLOW_THREADS
int cppResult = %CPPSELF.exec();
%END_ALLOW_THREADS
%PYARG_0 = %CONVERTTOPYTHON[int](cppResult);
// @snippet exec_

// @snippet exec_arg1
if (PyErr_WarnEx(PyExc_DeprecationWarning,
                 "'exec_' will be removed in the future. "
                 "Use 'exec' instead.",
                 1)) {
    return nullptr;
}
%BEGIN_ALLOW_THREADS
int cppResult;
if (numArgs == 1)
    cppResult = %CPPSELF.exec(%1);
else
    cppResult = %CPPSELF.exec();
%END_ALLOW_THREADS
%PYARG_0 = %CONVERTTOPYTHON[int](cppResult);
// @snippet exec_arg1

// @snippet exec_arg1_noreturn
if (PyErr_WarnEx(PyExc_DeprecationWarning,
                 "'exec_' will be removed in the future. "
                 "Use 'exec' instead.",
                 1)) {
    return nullptr;
}
%BEGIN_ALLOW_THREADS
if (numArgs == 1)
    %CPPSELF.exec(%1);
else
    %CPPSELF.exec();
%END_ALLOW_THREADS
// @snippet exec_arg1_noreturn

// @snippet qtextstreammanipulator-exec
if (PyErr_WarnEx(PyExc_DeprecationWarning,
                 "'exec_' will be removed in the future. "
                 "Use 'exec' instead.",
                 1)) {
    return nullptr;
}
%CPPSELF.exec(%1);
// @snippet qtextstreammanipulator-exec

/*********************************************************************
 * CONVERSIONS
 ********************************************************************/

// @snippet conversion-pybool
%out = %OUTTYPE(%in == Py_True);
// @snippet conversion-pybool

// @snippet conversion-pylong-quintptr
#if QT_POINTER_SIZE == 8
%out = %OUTTYPE(PyLong_AsUnsignedLongLong(%in));
#else
%out = %OUTTYPE(PyLong_AsUnsignedLong(%in));
#endif
// @snippet conversion-pylong-quintptr

// @snippet conversion-pyunicode
void *data = _PepUnicode_DATA(%in);
Py_ssize_t len = PyUnicode_GetLength(%in);
switch (_PepUnicode_KIND(%in)) {
    case PepUnicode_1BYTE_KIND:
        %out = QString::fromLatin1(reinterpret_cast<const char *>(data), len);
        break;
    case PepUnicode_2BYTE_KIND:
        %out = QString::fromUtf16(reinterpret_cast<const char16_t *>(data), len);
        break;
    case PepUnicode_4BYTE_KIND:
        %out = QString::fromUcs4(reinterpret_cast<const char32_t *>(data), len);
        break;
}
// @snippet conversion-pyunicode

// @snippet conversion-pynone
%out = %OUTTYPE();
// @snippet conversion-pynone

// @snippet qfile-path-1
auto cppArg0 = PySide::pyPathToQString(%PYARG_1);
// @snippet qfile-path-1

// @snippet qfile-path-2
auto cppArg1 = PySide::pyPathToQString(%PYARG_2);
// @snippet qfile-path-2

// @snippet qitemselection-add
auto res = (*%CPPSELF) + cppArg0;
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](res);
// @snippet qitemselection-add

// @snippet conversion-pystring-char
char c = %CONVERTTOCPP[char](%in);
%out = %OUTTYPE(c);
// @snippet conversion-pystring-char

// @snippet conversion-pyint
int i = %CONVERTTOCPP[int](%in);
%out = %OUTTYPE(i);
// @snippet conversion-pyint

// @snippet conversion-qlonglong
// PYSIDE-1250: For QVariant, if the type fits into an int; use int preferably.
qlonglong in = %CONVERTTOCPP[qlonglong](%in);
constexpr qlonglong intMax = qint64(std::numeric_limits<int>::max());
constexpr qlonglong intMin = qint64(std::numeric_limits<int>::min());
%out = in >= intMin && in <= intMax ? %OUTTYPE(int(in)) : %OUTTYPE(in);
// @snippet conversion-qlonglong

// @snippet conversion-qstring
QString in = %CONVERTTOCPP[QString](%in);
%out = %OUTTYPE(in);
// @snippet conversion-qstring

// @snippet conversion-qbytearray
QByteArray in = %CONVERTTOCPP[QByteArray](%in);
%out = %OUTTYPE(in);
// @snippet conversion-qbytearray

// @snippet conversion-pyfloat
double in = %CONVERTTOCPP[double](%in);
%out = %OUTTYPE(in);
// @snippet conversion-pyfloat

// @snippet conversion-sbkobject
// a class supported by QVariant?
const QMetaType metaType = QVariant_resolveMetaType(Py_TYPE(%in));
if (metaType.isValid()) {
    QVariant var(metaType);
    Shiboken::Conversions::SpecificConverter converter(metaType.name());
    converter.toCpp(pyIn, var.data());
    %out = var;
} else {
    // If the type was not encountered, return a default PyObjectWrapper
    %out = QVariant::fromValue(PySide::PyObjectWrapper(%in));
}
// @snippet conversion-sbkobject

// @snippet conversion-pydict
QVariant ret = QVariant_convertToVariantMap(%in);
%out = ret.isValid() ? ret : QVariant::fromValue(PySide::PyObjectWrapper(%in));
// @snippet conversion-pydict

// @snippet conversion-pylist
QVariant ret = QVariant_convertToVariantList(%in);
%out = ret.isValid() ? ret : QVariant::fromValue(PySide::PyObjectWrapper(%in));
// @snippet conversion-pylist

// @snippet conversion-pyobject
// Is a shiboken type not known by Qt
%out = QVariant::fromValue(PySide::PyObjectWrapper(%in));
// @snippet conversion-pyobject

// @snippet conversion-qjsonobject-pydict
QVariant dict = QVariant_convertToVariantMap(%in);
QJsonValue val = QJsonValue::fromVariant(dict);
%out = val.toObject();
// @snippet conversion-qjsonobject-pydict

// @snippet conversion-qdate-pydate
int day = PyDateTime_GET_DAY(%in);
int month = PyDateTime_GET_MONTH(%in);
int year = PyDateTime_GET_YEAR(%in);
%out = %OUTTYPE(year, month, day);
// @snippet conversion-qdate-pydate

// @snippet conversion-qdatetime-pydatetime
int day = PyDateTime_GET_DAY(%in);
int month = PyDateTime_GET_MONTH(%in);
int year = PyDateTime_GET_YEAR(%in);
int hour = PyDateTime_DATE_GET_HOUR(%in);
int min = PyDateTime_DATE_GET_MINUTE(%in);
int sec = PyDateTime_DATE_GET_SECOND(%in);
int usec = PyDateTime_DATE_GET_MICROSECOND(%in);
%out = %OUTTYPE(QDate(year, month, day), QTime(hour, min, sec, usec/1000));
// @snippet conversion-qdatetime-pydatetime

// @snippet conversion-qtime-pytime
int hour = PyDateTime_TIME_GET_HOUR(%in);
int min = PyDateTime_TIME_GET_MINUTE(%in);
int sec = PyDateTime_TIME_GET_SECOND(%in);
int usec = PyDateTime_TIME_GET_MICROSECOND(%in);
%out = %OUTTYPE(hour, min, sec, usec/1000);
// @snippet conversion-qtime-pytime

// @snippet conversion-qbytearray-pybytes
%out = %OUTTYPE(PyBytes_AS_STRING(%in), PyBytes_GET_SIZE(%in));
// @snippet conversion-qbytearray-pybytes

// @snippet conversion-qbytearray-pybytearray
%out = %OUTTYPE(PyByteArray_AsString(%in), PyByteArray_Size(%in));
// @snippet conversion-qbytearray-pybytearray

// @snippet conversion-qbytearray-pystring
%out = %OUTTYPE(Shiboken::String::toCString(%in), Shiboken::String::len(%in));
// @snippet conversion-qbytearray-pystring

/*********************************************************************
 * NATIVE TO TARGET CONVERSIONS
 ********************************************************************/

// @snippet return-pybool
return PyBool_FromLong((bool)%in);
// @snippet return-pybool

// @snippet return-pybytes
return PyBytes_FromStringAndSize(%in.constData(), %in.size());
// @snippet return-pybytes

// @snippet return-pylong
return PyLong_FromLong(%in);
// @snippet return-pylong

// @snippet return-pylong-quintptr
#if QT_POINTER_SIZE == 8
return PyLong_FromUnsignedLongLong(%in);
#else
return PyLong_FromUnsignedLong(%in);
#endif
// @snippet return-pylong-quintptr

// @snippet return-pyunicode
QByteArray ba = %in.toUtf8();
return PyUnicode_FromStringAndSize(ba.constData(), ba.size());
// @snippet return-pyunicode

// @snippet return-pyunicode-from-qanystringview
QByteArray ba = %in.toString().toUtf8();
return PyUnicode_FromStringAndSize(ba.constData(), ba.size());
// @snippet return-pyunicode-from-qanystringview

// @snippet return-pyunicode-qchar
auto c = wchar_t(%in.unicode());
return PyUnicode_FromWideChar(&c, 1);
// @snippet return-pyunicode-qchar

// @snippet return-qvariant
if (!%in.isValid())
    Py_RETURN_NONE;

switch (%in.typeId()) {
case QMetaType::UnknownType:
case QMetaType::Nullptr:
    Py_RETURN_NONE;
case QMetaType::VoidStar:
    if (%in.constData() == nullptr)
        Py_RETURN_NONE;
    break;

case QMetaType::QVariantList: {
    const auto var = %in.value<QVariantList>();
    return %CONVERTTOPYTHON[QList<QVariant>](var);
}
case QMetaType::QStringList: {
    const auto var = %in.value<QStringList>();
    return %CONVERTTOPYTHON[QList<QString>](var);
}
case QMetaType::QVariantMap: {
    const auto var = %in.value<QVariantMap>();
    return %CONVERTTOPYTHON[QMap<QString, QVariant>](var);
}
default:
    break;
}

Shiboken::Conversions::SpecificConverter converter(cppInRef.typeName());
if (converter) {
   void *ptr = cppInRef.data();
   return converter.toPython(ptr);
}
PyErr_Format(PyExc_RuntimeError, "Can't find converter for '%s'.", %in.typeName());
return 0;
// @snippet return-qvariant

// @snippet return-qjsonobject
// The QVariantMap returned by QJsonObject seems to cause a segfault, so
// using QJsonObject.toVariantMap() won't work.
// Wrapping it in a QJsonValue first allows it to work
QJsonValue val(%in);
QVariant ret = val.toVariant();

return %CONVERTTOPYTHON[QVariant](ret);
// @snippet return-qjsonobject

// @snippet qthread_pthread_cleanup
#ifdef Q_OS_UNIX
#  include <stdio.h>
#  include <pthread.h>
static void qthread_pthread_cleanup(void *arg)
{
    // PYSIDE 1282: When terminating a thread using QThread::terminate()
    // (pthread_cancel()), QThread::run() is aborted and the lock is released,
    // but ~GilState() is still executed for some reason. Prevent it from
    // releasing.
    auto gil = reinterpret_cast<Shiboken::GilState *>(arg);
    gil->abandon();
}
#endif // Q_OS_UNIX
// @snippet qthread_pthread_cleanup

// @snippet qthread_pthread_cleanup_install
#ifdef Q_OS_UNIX
pthread_cleanup_push(qthread_pthread_cleanup, &gil);
#endif
// @snippet qthread_pthread_cleanup_install

// @snippet qthread_pthread_cleanup_uninstall
#ifdef Q_OS_UNIX
pthread_cleanup_pop(0);
#endif
// @snippet qthread_pthread_cleanup_uninstall

// @snippet qlibraryinfo_build
#if defined(Py_LIMITED_API)
auto suffix = PyUnicode_FromString(" [limited API]");
auto oldResult = pyResult;
pyResult = PyUnicode_Concat(pyResult, suffix);
Py_DECREF(oldResult);
Py_DECREF(suffix);
#endif
// @snippet qlibraryinfo_build

// @snippet qsharedmemory_data_readonly
%PYARG_0 = Shiboken::Buffer::newObject(%CPPSELF.%FUNCTION_NAME(), %CPPSELF.size());
// @snippet qsharedmemory_data_readonly

// @snippet qsharedmemory_data_readwrite
// FIXME: There is no way to tell whether QSharedMemory was attached read/write
%PYARG_0 = Shiboken::Buffer::newObject(%CPPSELF.%FUNCTION_NAME(), %CPPSELF.size(),
                                       Shiboken::Buffer::ReadWrite);
// @snippet qsharedmemory_data_readwrite

// @snippet std-function-void-lambda
auto *callable = %PYARG_1;
auto cppCallback = [callable]()
{
    Shiboken::GilState state;
    Shiboken::AutoDecRef arglist(PyTuple_New(0));
    Shiboken::AutoDecRef ret(PyObject_CallObject(callable, arglist));
    Py_DECREF(callable);
};
// @snippet std-function-void-lambda

// @snippet qthreadpool-start
Py_INCREF(callable);
%CPPSELF.%FUNCTION_NAME(cppCallback, %2);
// @snippet qthreadpool-start

// @snippet qthreadpool-trystart
Py_INCREF(callable);
%RETURN_TYPE %0 = %CPPSELF.%FUNCTION_NAME(cppCallback);
%PYARG_0 = %CONVERTTOPYTHON[int](cppResult);
// @snippet qthreadpool-trystart

// @snippet repr-qevent
QString result;
QDebug(&result).nospace() << "<PySide6.QtCore.QEvent(" << %CPPSELF->type() << ")>";
%PYARG_0 = Shiboken::String::fromCString(qPrintable(result));
// @snippet repr-qevent

// @snippet qmetaproperty_write_enum
if (Shiboken::Enum::check(%PYARG_2)) {
    int in = %CONVERTTOCPP[int](%PYARG_2);
    cppArg1 = QVariant(in);
}
// @snippet qmetaproperty_write_enum

// @snippet qdatastream-read-bytes
QByteArray data;
data.resize(%2);
auto dataChar = data.data();
cppSelf->readBytes(dataChar, %2);
const char *constDataChar = dataChar;
if (dataChar == nullptr) {
    Py_INCREF(Py_None);
    %PYARG_0 = Py_None;
} else {
    %PYARG_0 = PyBytes_FromStringAndSize(constDataChar, %2);
}
// @snippet qdatastream-read-bytes

// @snippet qloggingcategory_to_cpp
    QLoggingCategory *category{nullptr};
    Shiboken::Conversions::pythonToCppPointer(SbkPySide6_QtCoreTypes[SBK_QLOGGINGCATEGORY_IDX],
    pyArgs[0], &(category));
// @snippet qloggingcategory_to_cpp
