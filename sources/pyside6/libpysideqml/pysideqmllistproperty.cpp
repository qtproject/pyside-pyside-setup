// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include "pysideqmllistproperty_p.h"
#include "pysideqmlregistertype_p.h"

#include <shiboken.h>
#include <signature.h>

#include <pysideproperty.h>
#include <pysideproperty_p.h>

#include <QtCore/QObject>
#include <QtQml/QQmlListProperty>

// This is the user data we store in the property.
class QmlListPropertyPrivate : public PySidePropertyPrivate
{
public:
    void metaCall(PyObject *source, QMetaObject::Call call, void **args) override;

    PyTypeObject *type = nullptr;
    PyObject *append = nullptr;
    PyObject *count = nullptr;
    PyObject *at = nullptr;
    PyObject *clear = nullptr;
    PyObject *replace = nullptr;
    PyObject *removeLast = nullptr;
};

extern "C"
{

static PyObject *propList_tp_new(PyTypeObject *subtype, PyObject * /* args */, PyObject * /* kwds */)
{
    PySideProperty *me = reinterpret_cast<PySideProperty *>(subtype->tp_alloc(subtype, 0));
    me->d = new QmlListPropertyPrivate;
    return reinterpret_cast<PyObject *>(me);
}

static int propListTpInit(PyObject *self, PyObject *args, PyObject *kwds)
{
    static const char *kwlist[] = {"type", "append", "count", "at", "clear",
                                   "replace", "removeLast",
                                   "doc", "notify", // PySideProperty
                                   "designable", "scriptable", "stored",
                                   "user", "constant", "final",
                                   nullptr};
    PySideProperty *pySelf = reinterpret_cast<PySideProperty *>(self);

    auto *data = static_cast<QmlListPropertyPrivate *>(pySelf->d);

    char *doc{};

    if (!PyArg_ParseTupleAndKeywords(args, kwds,
                                     "O|OOOOOOsObbbbbb:QtQml.ListProperty",
                                     const_cast<char **>(kwlist),
                                     &data->type,
                                     &data->append,
                                     &data->count,
                                     &data->at,
                                     &data->clear,
                                     &data->replace,
                                     &data->removeLast,
                                     /*s*/   &doc,
                                     /*O*/   &(data->notify), // PySideProperty
                                     /*bbb*/ &(data->designable),
                                             &(data->scriptable),
                                             &(data->stored),
                                     /*bbb*/ &(data->user),
                                             &(data->constant),
                                             &(data->final))) {
        return -1;
    }

    if (doc)
        data->doc = doc;
    else
        data->doc.clear();

    PyTypeObject *qobjectType = qObjectType();

    if (!PySequence_Contains(data->type->tp_mro, reinterpret_cast<PyObject *>(qobjectType))) {
        PyErr_Format(PyExc_TypeError, "A type inherited from %s expected, got %s.",
                     qobjectType->tp_name, data->type->tp_name);
        return -1;
    }

    if ((data->append && data->append != Py_None && !PyCallable_Check(data->append)) ||
        (data->count && data->count != Py_None && !PyCallable_Check(data->count)) ||
        (data->at && data->at != Py_None && !PyCallable_Check(data->at)) ||
        (data->clear && data->clear != Py_None && !PyCallable_Check(data->clear)) ||
        (data->replace && data->replace != Py_None && !PyCallable_Check(data->replace)) ||
        (data->removeLast && data->removeLast != Py_None && !PyCallable_Check(data->removeLast))) {
        PyErr_Format(PyExc_TypeError, "Non-callable parameter given");
        return -1;
    }

    data->typeName = QByteArrayLiteral("QQmlListProperty<QObject>");

    return 0;
}

static PyType_Slot PropertyListType_slots[] = {
    {Py_tp_new, reinterpret_cast<void *>(propList_tp_new)},
    {Py_tp_init, reinterpret_cast<void *>(propListTpInit)},
    {0, nullptr}
};
static PyType_Spec PropertyListType_spec = {
    "2:PySide6.QtQml.ListProperty",
    sizeof(PySideProperty),
    0,
    Py_TPFLAGS_DEFAULT,
    PropertyListType_slots,
};


PyTypeObject *PropertyList_TypeF(void)
{
    static Shiboken::AutoDecRef bases(Py_BuildValue("(O)", PySideProperty_TypeF()));
    static auto *type = SbkType_FromSpecWithBases(&PropertyListType_spec, bases);
    return type;
}

} // extern "C"

// Implementation of QQmlListProperty<T>::AppendFunction callback
void propListAppender(QQmlListProperty<QObject> *propList, QObject *item)
{
    Shiboken::GilState state;

    Shiboken::AutoDecRef args(PyTuple_New(2));
    PyTypeObject *qobjectType = qObjectType();
    PyTuple_SET_ITEM(args, 0,
                     Shiboken::Conversions::pointerToPython(qobjectType, propList->object));
    PyTuple_SET_ITEM(args, 1,
                     Shiboken::Conversions::pointerToPython(qobjectType, item));

    auto *data = reinterpret_cast<QmlListPropertyPrivate *>(propList->data);
    Shiboken::AutoDecRef retVal(PyObject_CallObject(data->append, args));

    if (PyErr_Occurred())
        PyErr_Print();
}

// Implementation of QQmlListProperty<T>::CountFunction callback
qsizetype propListCount(QQmlListProperty<QObject> *propList)
{
    Shiboken::GilState state;

    Shiboken::AutoDecRef args(PyTuple_New(1));
    PyTuple_SET_ITEM(args, 0,
                     Shiboken::Conversions::pointerToPython(qObjectType(), propList->object));

    auto *data = reinterpret_cast<QmlListPropertyPrivate *>(propList->data);
    Shiboken::AutoDecRef retVal(PyObject_CallObject(data->count, args));

    // Check return type
    if (PyErr_Occurred()) {
        PyErr_Print();
        return 0;
    }

    int cppResult = 0;
    auto *converter = Shiboken::Conversions::PrimitiveTypeConverter<qsizetype>();
    if (auto *pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(converter, retVal))
        pythonToCpp(retVal, &cppResult);
    return cppResult;
}

// Implementation of QQmlListProperty<T>::AtFunction callback
QObject *propListAt(QQmlListProperty<QObject> *propList, qsizetype index)
{
    Shiboken::GilState state;

    Shiboken::AutoDecRef args(PyTuple_New(2));
    PyTypeObject *qobjectType = qObjectType();
    PyTuple_SET_ITEM(args, 0,
                     Shiboken::Conversions::pointerToPython(qobjectType, propList->object));
    auto *converter = Shiboken::Conversions::PrimitiveTypeConverter<qsizetype>();
    PyTuple_SET_ITEM(args, 1,
                     Shiboken::Conversions::copyToPython(converter, &index));

    auto *data = reinterpret_cast<QmlListPropertyPrivate *>(propList->data);
    Shiboken::AutoDecRef retVal(PyObject_CallObject(data->at, args));

    QObject *result = 0;
    if (PyErr_Occurred())
        PyErr_Print();
    else if (PyType_IsSubtype(Py_TYPE(retVal), data->type))
        Shiboken::Conversions::pythonToCppPointer(qobjectType, retVal, &result);
    return result;
}

// Implementation of QQmlListProperty<T>::ClearFunction callback
void propListClear(QQmlListProperty<QObject> * propList)
{
    Shiboken::GilState state;

    Shiboken::AutoDecRef args(PyTuple_New(1));
    PyTypeObject *qobjectType = qObjectType();
    PyTuple_SET_ITEM(args, 0,
                     Shiboken::Conversions::pointerToPython(qobjectType, propList->object));

    auto *data = reinterpret_cast<QmlListPropertyPrivate *>(propList->data);
    Shiboken::AutoDecRef retVal(PyObject_CallObject(data->clear, args));

    if (PyErr_Occurred())
        PyErr_Print();
}

// Implementation of QQmlListProperty<T>::ReplaceFunction callback
void propListReplace(QQmlListProperty<QObject> *propList, qsizetype index, QObject *value)
{
    Shiboken::GilState state;

    Shiboken::AutoDecRef args(PyTuple_New(3));
    PyTypeObject *qobjectType = qObjectType();
    PyTuple_SET_ITEM(args, 0,
                     Shiboken::Conversions::pointerToPython(qobjectType, propList->object));
    auto *converter = Shiboken::Conversions::PrimitiveTypeConverter<qsizetype>();
    PyTuple_SET_ITEM(args, 1,
                     Shiboken::Conversions::copyToPython(converter, &index));
    PyTuple_SET_ITEM(args, 2,
                     Shiboken::Conversions::pointerToPython(qobjectType, value));

    auto *data = reinterpret_cast<QmlListPropertyPrivate *>(propList->data);
    Shiboken::AutoDecRef retVal(PyObject_CallObject(data->replace, args));

    if (PyErr_Occurred())
        PyErr_Print();
}

// Implementation of QQmlListProperty<T>::RemoveLastFunction callback
void propListRemoveLast(QQmlListProperty<QObject> *propList)
{
    Shiboken::GilState state;

    Shiboken::AutoDecRef args(PyTuple_New(1));
    PyTypeObject *qobjectType = qObjectType();
    PyTuple_SET_ITEM(args, 0,
                     Shiboken::Conversions::pointerToPython(qobjectType, propList->object));

    auto *data = reinterpret_cast<QmlListPropertyPrivate *>(propList->data);
    Shiboken::AutoDecRef retVal(PyObject_CallObject(data->removeLast, args));

    if (PyErr_Occurred())
        PyErr_Print();
}

// qt_metacall specialization for ListProperties
void QmlListPropertyPrivate::metaCall(PyObject *source, QMetaObject::Call call, void **args)
{
    if (call != QMetaObject::ReadProperty)
        return;

    QObject *qobj;
    PyTypeObject *qobjectType = qObjectType();
    Shiboken::Conversions::pythonToCppPointer(qobjectType, source, &qobj);
    QQmlListProperty<QObject> declProp(
        qobj, this,
        append && append != Py_None ? &propListAppender : nullptr,
        count && count != Py_None ? &propListCount : nullptr,
        at && at != Py_None ? &propListAt : nullptr,
        clear && clear != Py_None ? &propListClear : nullptr,
        replace && replace != Py_None ? &propListReplace : nullptr,
        removeLast && removeLast != Py_None ? &propListRemoveLast : nullptr);

    // Copy the data to the memory location requested by the meta call
    void *v = args[0];
    *reinterpret_cast<QQmlListProperty<QObject> *>(v) = declProp;
}

static const char *PropertyList_SignatureStrings[] = {
    "PySide6.QtQml.ListProperty(self,type:type,append:typing.Callable,"
        "at:typing.Callable=None,clear:typing.Callable=None,count:typing.Callable=None)",
    nullptr // Sentinel
};

namespace PySide::Qml {

void initQtQmlListProperty(PyObject *module)
{
    // Export QmlListProperty type
    if (InitSignatureStrings(PropertyList_TypeF(), PropertyList_SignatureStrings) < 0) {
        PyErr_Print();
        qWarning() << "Error initializing PropertyList type.";
        return;
    }

    // Register QQmlListProperty metatype for use in QML
    qRegisterMetaType<QQmlListProperty<QObject>>();

    Py_INCREF(reinterpret_cast<PyObject *>(PropertyList_TypeF()));
    PyModule_AddObject(module, PepType_GetNameStr(PropertyList_TypeF()),
                       reinterpret_cast<PyObject *>(PropertyList_TypeF()));
}

} // namespace PySide::Qml
