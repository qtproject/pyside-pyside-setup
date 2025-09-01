// Copyright (C) 2025 Ford Motor Company
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

// Workaround to access protected functions. PySide builds with this, but
// since this is now a separate library, we need to add it too.

#include "pysidedynamiccommon_p.h"
#include "pysidedynamicclass_p.h"
#include "pysidecapsulemethod_p.h"
#include "pysiderephandler_p.h"

#include <basewrapper.h>
#include <sbkconverter.h>
#include <sbkstring.h>

#include <pyside_p.h>
#include <pysideproperty.h>
#include <pysideqobject.h>
#include <pysidesignal.h>
#include <pysideutils.h>

#include <QtCore/qmetaobject.h>
#include <QtCore/qvariantlist.h>

#include <QtRemoteObjects/qremoteobjectpendingcall.h>
#include <QtRemoteObjects/qremoteobjectreplica.h>

#include <cstring>
#include <cctype>

using namespace Shiboken;

class FriendlyReplica : public QRemoteObjectReplica
{
public:
    using QRemoteObjectReplica::send;
    using QRemoteObjectReplica::setProperties;
    using QRemoteObjectReplica::propAsVariant;
    using QRemoteObjectReplica::sendWithReply;
};

extern "C"
{

PyObject *propertiesAttr()
{
    static PyObject *const s = Shiboken::String::createStaticString("__PROPERTIES__");
    return s;
}

struct SourceDefs
{
    static PyTypeObject *getSbkType()
    {
        static PyTypeObject *sbkType =
            Shiboken::Conversions::getPythonTypeObject("QObject");
        return sbkType;
    }

    static PyObject *getBases()
    {
        static PyObject *bases = PyTuple_Pack(1, getSbkType());
        return bases;
    }

    static const char *getTypePrefix()
    {
        return "2:PySide6.QtRemoteObjects.DynamicSource.";
    }

    static int tp_init(PyObject *self, PyObject *args, PyObject *kwds)
    {
        static initproc initFunc = reinterpret_cast<initproc>(PepType_GetSlot(getSbkType(), Py_tp_init));
        int res = initFunc(self, args, kwds);
        if (res < 0) {
            PyErr_Print();
            return res;
        }

        // Get the properties from the type
        PyTypeObject *type = Py_TYPE(self);
        auto *pyProperties = PyObject_GetAttr(reinterpret_cast<PyObject *>(type), propertiesAttr());
        if (!pyProperties) {
            PyErr_SetString(PyExc_RuntimeError, "Failed to get properties from type");
            return -1;
        }
        // Add a copy of the properties to the object
        auto *propPtr = reinterpret_cast<QVariantList *>(PyCapsule_GetPointer(pyProperties, nullptr));
        auto *propertiesCopy = new QVariantList(*propPtr);
        PyObject *capsule = PyCapsule_New(propertiesCopy, nullptr, [](PyObject *capsule) {
                delete reinterpret_cast<QVariantList *>(PyCapsule_GetPointer(capsule, nullptr));
            });
        PyObject_SetAttr(self, propertiesAttr(), capsule);
        Py_DECREF(capsule);
        return res;
    }

    static PyObject *capsule_method_handler(PyObject *payload, PyObject *args)
    {
        auto *methodData = reinterpret_cast<CapsuleDescriptorData *>(PyCapsule_GetPointer(payload,
                                                                                          "Payload"));
        if (!methodData) {
            PyErr_SetString(PyExc_RuntimeError, "Invalid call to dynamic method.  Missing payload.");
            return nullptr;
        }
        PyObject *self = methodData->self;
        if (PyCapsule_IsValid(methodData->payload, "PropertyCapsule")) {
            // Handle property getter/setter against our hidden properties attribute
            auto *capsule = PyCapsule_GetPointer(methodData->payload, "PropertyCapsule");
            if (capsule) {
                auto *ob_dict = SbkObject_GetDict_NoRef(self);
                auto *propPtr = PyCapsule_GetPointer(PyDict_GetItem(ob_dict, propertiesAttr()),
                                                     nullptr);
                auto *currentProperties = reinterpret_cast<QVariantList *>(propPtr);
                auto *callData = reinterpret_cast<PropertyCapsule *>(capsule);
                if (callData->indexInObject < 0
                    || callData->indexInObject >= currentProperties->size()) {
                    PyErr_Format(PyExc_RuntimeError, "Unknown property method: %s",
                                 callData->name.constData());
                    return nullptr;
                }
                const QVariant &currentVariant = currentProperties->at(callData->indexInObject);

                // Handle getter
                if (PyTuple_Size(args) == 0)
                    return toPython(currentVariant);

                // Handle setter
                if (PyTuple_Size(args) != 1) {
                    PyErr_SetString(PyExc_TypeError, "Property setter takes exactly one argument");
                    return nullptr;
                }
                Conversions::SpecificConverter converter(currentVariant.metaType().name());
                QVariant variant{currentVariant.metaType()};
                auto metaType = currentVariant.metaType();
                if (metaType.flags().testFlag(QMetaType::IsEnumeration)) {
                    converter.toCpp(PyTuple_GetItem(args, 0), variant.data());
                    variant.convert(metaType);
                } else {
                    converter.toCpp(PyTuple_GetItem(args, 0), variant.data());
                }
                if (PyErr_Occurred()) // POD conversion can produce an error
                    return nullptr;
                if (variant == currentVariant)
                    Py_RETURN_NONE;

                currentProperties->replace(callData->indexInObject, variant);
                // Get the QMetaObject and emit the property changed signal if there is one
                const auto *metaObject = PySide::retrieveMetaObject(self);
                auto metaProperty = metaObject->property(callData->propertyIndex);
                if (metaProperty.hasNotifySignal()) {
                    // We know our custom types don't have multiple cpp objects
                    void *cptr = reinterpret_cast<SbkObject *>(self)->d->cptr[0];
                    auto *qObject = reinterpret_cast<QObject *>(cptr);
                    void *_args[] = {nullptr, variant.data()};
                    QMetaObject::activate(qObject, metaProperty.notifySignalIndex(), _args);
                }
                Py_RETURN_NONE;
            }
        }
        if (PyCapsule_IsValid(methodData->payload, "MethodCapsule")) {
            auto *capsule = PyCapsule_GetPointer(methodData->payload, "MethodCapsule");
            auto *callData = reinterpret_cast<MethodCapsule *>(capsule);
            if (callData->name.startsWith("push") && callData->name.size() > 4) {
                const auto *metaObject = PySide::retrieveMetaObject(self);
                // The convention for QtRO is if a property is named "something" and uses
                // push, the name of the push method will be "pushSomething". But it is
                // possible the name would be "Something", so we need to check upper
                // and lower case.
                auto name = callData->name.sliced(4);
                auto index = metaObject->indexOfProperty(name.constData());
                if (index < 0) {
                    name[0] = std::tolower(name[0]);  // Try lower case
                    index = metaObject->indexOfProperty(name.constData());
                }
                // It is possible a .rep names a Slot "push" or "pushSomething" that
                // isn't generated for a property. Let that fall through to regular
                // method handling.
                if (index >= 0) {
                    // Call the custom descriptor's set method
                    auto result = PyObject_SetAttrString(self, name.constData(),
                                                         PyTuple_GetItem(args, 0));
                    if (result < 0) {
                        PyErr_Print();
                        return nullptr;
                    }
                    Py_RETURN_NONE;
                }
            }
            // TODO: This doesn't do much, as it is "eaten" by a PyError_Print in
            // SignalManager::handleMetaCallError()
            // Is there a better way to address slots that need to be implemented?
            PyErr_Format(PyExc_NotImplementedError, "** The method %s is not implemented",
                         callData->name.constData());
            return nullptr;
        }

        PyErr_SetString(PyExc_RuntimeError, "Unknown capsule type");
        return nullptr;
    }
};

struct ReplicaDefs
{
    static PyTypeObject *getSbkType()
    {
        static PyTypeObject *sbkType =
            Shiboken::Conversions::getPythonTypeObject("QRemoteObjectReplica");
        return sbkType;
    }

    static PyObject *getBases()
    {
        static PyObject *bases = PyTuple_Pack(1, getSbkType());
        return bases;
    }

    static const char *getTypePrefix()
    {
        return "2:PySide6.QtRemoteObjects.DynamicReplica.";
    }

    static int tp_init(PyObject *self, PyObject *args, PyObject *kwds)
    {
        static initproc initFunc = reinterpret_cast<initproc>(PepType_GetSlot(getSbkType(),
                                                                              Py_tp_init));
        QRemoteObjectReplica *replica = nullptr;
        if (PyTuple_Size(args) == 0) {
            if (initFunc(self, args, kwds) < 0)
                return -1;
            Shiboken::Conversions::pythonToCppPointer(getSbkType(), self, &replica);
        } else {  // Process replica with arguments passed from the added node.acquire method
            PyObject *node = nullptr;
            PyObject *constructorType = nullptr;
            PyObject *name = nullptr;
            static PyTypeObject *nodeType = Shiboken::Conversions::getPythonTypeObject("QRemoteObjectNode");
            if (!PyArg_UnpackTuple(args, "Replica.__init__", 2, 3, &node, &constructorType, &name) ||
                !PySide::inherits(Py_TYPE(node), nodeType->tp_name)) {
                PyErr_SetString(PyExc_TypeError,
                                "Replicas can be initialized with no arguments or by node.acquire only");
                return -1;
            }
            static auto *constructorArgs = PyTuple_Pack(1, constructorType);
            if (initFunc(self, constructorArgs, kwds) < 0)
                return -1;
            if (name)
                PyObject_CallMethod(self, "initializeNode", "OO", node, name);
            else
                PyObject_CallMethod(self, "initializeNode", "O", node);
            Shiboken::Conversions::pythonToCppPointer(getSbkType(), self, &replica);
        }
        if (!replica) {
            PyErr_SetString(PyExc_RuntimeError, "Failed to initialize replica");
            return -1;
        }
        // Get the properties from the type
        PyTypeObject *type = Py_TYPE(self);
        auto *pyProperties = PyObject_GetAttr(reinterpret_cast<PyObject *>(type), propertiesAttr());
        if (!pyProperties) {
            PyErr_SetString(PyExc_RuntimeError, "Failed to get properties from type");
            return -1;
        }
        // Make a copy of the properties and set them on the replica
        auto *propPtr = reinterpret_cast<QVariantList *>(PyCapsule_GetPointer(pyProperties, nullptr));
        auto propertiesCopy = QVariantList(*propPtr);
        static_cast<FriendlyReplica *>(replica)->setProperties(std::move(propertiesCopy));
        return 0;
    }

    static PyObject *capsule_method_handler(PyObject *payload, PyObject *args)
    {
        auto *methodData = reinterpret_cast<CapsuleDescriptorData *>(PyCapsule_GetPointer(payload,
                                                                                          "Payload"));
        if (!methodData) {
            PyErr_SetString(PyExc_RuntimeError, "Invalid call to dynamic method.  Missing payload.");
            return nullptr;
        }
        PyObject *self = methodData->self;
        QRemoteObjectReplica *replica = nullptr;
        Shiboken::Conversions::pythonToCppPointer(getSbkType(), self, &replica);
        if (PyCapsule_IsValid(methodData->payload, "PropertyCapsule")) {
            auto *capsule = PyCapsule_GetPointer(methodData->payload, "PropertyCapsule");
            if (capsule) {
                auto *callData = reinterpret_cast<PropertyCapsule *>(capsule);
                QVariant currentVariant = static_cast<FriendlyReplica *>(replica)->propAsVariant(callData->indexInObject);

                // Handle getter
                if (PyTuple_Size(args) == 0) // Getter
                    return toPython(currentVariant);

                // Handle setter - currentVariant is a copy, so we can modify it
                if (PyTuple_Size(args) != 1) {
                    PyErr_SetString(PyExc_TypeError,
                                    "Property setter takes exactly one argument");
                    return nullptr;
                }
                Conversions::SpecificConverter converter(currentVariant.metaType().name());
                auto metaType = currentVariant.metaType();
                if (metaType.flags().testFlag(QMetaType::IsEnumeration)) {
                    converter.toCpp(PyTuple_GetItem(args, 0), currentVariant.data());
                    currentVariant.convert(metaType);
                } else {
                    converter.toCpp(PyTuple_GetItem(args, 0), currentVariant.data());
                }
                if (PyErr_Occurred()) // POD conversion can produce an error
                    return nullptr;
                QVariantList _args{currentVariant};
                static_cast<FriendlyReplica *>(replica)->send(QMetaObject::WriteProperty, callData->propertyIndex, _args);
                Py_RETURN_NONE;
            }
        }
        if (PyCapsule_IsValid(methodData->payload, "MethodCapsule")) {
            auto *capsule = PyCapsule_GetPointer(methodData->payload, "MethodCapsule");
            if (capsule) {
                auto *callData = reinterpret_cast<MethodCapsule *>(capsule);
                if (PyTuple_Size(args) != callData->argumentTypes.size()) {
                    PyErr_SetString(PyExc_TypeError,
                                    "Method called with incorrect number of arguments");
                    return nullptr;
                }
                QVariantList _args;
                static Conversions::SpecificConverter argsConverter("QVariantList");
                argsConverter.toCpp(args, &_args);
                if (PyErr_Occurred()) // POD conversion can produce an error
                    return nullptr;
                if (!callData->returnType.isValid() ||
                    (callData->returnType.isValid() && callData->returnType.id() == QMetaType::Void)) {
                    static_cast<FriendlyReplica *>(replica)->send(QMetaObject::InvokeMetaMethod, callData->methodIndex, _args);
                    Py_RETURN_NONE;
                }
                QRemoteObjectPendingCall *cppResult = new QRemoteObjectPendingCall;
                *cppResult = static_cast<FriendlyReplica *>(replica)->sendWithReply(QMetaObject::InvokeMetaMethod,
                                                    callData->methodIndex, _args);
                static PyTypeObject *baseType =
                    Shiboken::Conversions::getPythonTypeObject("QRemoteObjectPendingCall");
                Q_ASSERT(baseType);
                auto *pyResult = Shiboken::Object::newObject(baseType, cppResult, true, true);
                return pyResult;
            }
        }

        PyErr_SetString(PyExc_RuntimeError, "Unknown capsule type");
        return nullptr;
    }
};

static int DynamicType_traverse(PyObject *self, visitproc visit, void *arg)
{
    auto traverseProc = reinterpret_cast<traverseproc>(PepType_GetSlot(SbkObject_TypeF(),
                                                                       Py_tp_traverse));
    return traverseProc(self, visit, arg);
}

static int DynamicType_clear(PyObject *self)
{
    auto clearProc = reinterpret_cast<inquiry>(PepType_GetSlot(SbkObject_TypeF(), Py_tp_clear));
    return clearProc(self);
}

static PyMethodDef DynamicClass_methods[] = {
    {"get_enum", reinterpret_cast<PyCFunction>(DynamicType_get_enum), METH_O | METH_CLASS,
     "Get enum type by name"},
    {nullptr, nullptr, 0, nullptr}
};

static PyType_Slot DynamicClass_slots[] = {
    {Py_tp_base,        nullptr}, // inserted by introduceWrapperType
    {Py_tp_init,        nullptr}, // inserted by createDynamicType
    {Py_tp_traverse,    reinterpret_cast<void *>(DynamicType_traverse)},
    {Py_tp_clear,       reinterpret_cast<void *>(DynamicType_clear)},
    {Py_tp_methods,     reinterpret_cast<void *>(DynamicClass_methods)},
    {0, nullptr}
};

} // extern "C"

template <typename T, typename BaseType>
PyTypeObject *createDynamicClassImpl(QMetaObject *meta)
{
    DynamicClass_slots[1].pfunc = reinterpret_cast<void*>(T::tp_init);

    auto fullTypeName = QByteArray{T::getTypePrefix()} + meta->className();
    PyType_Spec spec = {
        fullTypeName.constData(),
        0,
        0,
        Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
        DynamicClass_slots
    };

    auto type = Shiboken::ObjectType::introduceWrapperType(
        reinterpret_cast<PyObject *>(PySideRepFile_TypeF()),
        meta->className(),
        meta->className(),
        &spec,
        &Shiboken::callCppDestructor<BaseType>,
        T::getBases(),
        Shiboken::ObjectType::WrapperFlags::InternalWrapper);

    auto *self = reinterpret_cast<PyObject *>(type);
    if (create_managed_py_enums(self, meta) < 0)
        return nullptr;

    PySide::Signal::registerSignals(type, meta);
    Shiboken::ObjectType::setSubTypeInitHook(type, &PySide::initQObjectSubType);
    PySide::initDynamicMetaObject(type, meta, 0);  // Size 0?

    PyMethodDef method = {
        nullptr,
        reinterpret_cast<PyCFunction>(T::capsule_method_handler),
        METH_VARARGS,
        nullptr
    };
    for (int i = meta->propertyOffset(); i < meta->propertyCount(); ++i) {
        // Create a PropertyCapsule for each property to store the info needed for
        // the handler. Assign the __get__ and (if needed) __set__ attributes to a
        // PySideProperty which becomes the attribute set on the new type.
        auto metaProperty = meta->property(i);
        PyObject *kwds = PyDict_New();
        auto metaType = metaProperty.metaType();
        auto *pyPropertyType = PyUnicode_FromString(metaType.name());
        PyDict_SetItemString(kwds, "type", pyPropertyType);
        Py_DECREF(pyPropertyType);

        method.ml_name = metaProperty.name();
        auto *pc = new PropertyCapsule{metaProperty.name(), i, i - meta->propertyOffset()};
        auto capsule = PyCapsule_New(pc, "PropertyCapsule", [](PyObject *capsule) {
            delete static_cast<PropertyCapsule *>(PyCapsule_GetPointer(capsule, "PropertyCapsule"));
        });
        auto capsulePropObject = make_capsule_property(&method, capsule,
                                                       metaProperty.isWritable());
        PyObject *fget = PyObject_GetAttrString(capsulePropObject, "__get__");
        PyDict_SetItemString(kwds, "fget", fget);
        if (metaProperty.isWritable()) {
            PyObject *fset = PyObject_GetAttrString(capsulePropObject, "__set__");
            PyDict_SetItemString(kwds, "fset", fset);
            if (metaProperty.hasNotifySignal()) {
                auto nameString = metaProperty.notifySignal().name();
                auto *notify = PyObject_GetAttrString(reinterpret_cast<PyObject *>(type),
                                                      nameString.constData());
                PyDict_SetItemString(kwds, "notify", notify);
            }
        }
        PyObject *pyProperty = PyObject_Call(reinterpret_cast<PyObject *>(PySideProperty_TypeF()),
                                             PyTuple_New(0), kwds);
        if (PyObject_SetAttrString(reinterpret_cast<PyObject *>(type),
                                   metaProperty.name(), pyProperty) < 0) {
            return nullptr;
        }
        Py_DECREF(pyProperty);
    }
    for (int i = meta->methodOffset(); i < meta->methodCount(); ++i) {
        // Create a CapsuleMethod for each Slot method to store the info needed
        // for the handler.
        auto metaMethod = meta->method(i);
        // Note: We are creating our custom metatype ourselves, which makes our added
        // (non-signal), methods return QMetaMethod::MethodType::Method, not
        // MethodType::Slot. This is fine, we just need to create a CapsuleMethod
        // for those methods.
        if (metaMethod.methodType() == QMetaMethod::MethodType::Signal)
            continue;
        auto name = metaMethod.name();
        method.ml_name = name.constData();
        QList<QMetaType> argumentTypes;
        for (int j = 0; j < metaMethod.parameterCount(); ++j)
            argumentTypes << metaMethod.parameterMetaType(j);
        MethodCapsule *capsuleData = new MethodCapsule{metaMethod.name(),
                                                       metaMethod.methodIndex(),
                                                       std::move(argumentTypes),
                                                       metaMethod.returnMetaType()};
        add_capsule_method_to_type(type, &method,
                                   PyCapsule_New(capsuleData, "MethodCapsule",
                                                 [](PyObject *capsule) {
            delete reinterpret_cast<MethodCapsule *>(PyCapsule_GetPointer(capsule, "MethodCapsule"));
        }));
    }

    return type;
}

PyTypeObject *createDynamicClass(QMetaObject *meta, PyObject *properties_capsule)
{
    bool isSource;
    if (std::strncmp(meta->superClass()->className(), "QObject", 7) == 0) {
        isSource = true;
    } else if (std::strncmp(meta->superClass()->className(), "QRemoteObjectReplica", 20) == 0) {
        isSource = false;
    } else {
        PyErr_SetString(PyExc_RuntimeError,
                        "Dynamic type must be a subclass of QObject or QRemoteObjectReplica");
        return nullptr;
    }

    PyTypeObject *newType = nullptr;

    if (isSource)
        newType = createDynamicClassImpl<SourceDefs, QObject>(meta);
    else
        newType = createDynamicClassImpl<ReplicaDefs, QRemoteObjectReplica>(meta);

    // Add the properties to the new type as an attribute
    if (PyObject_SetAttr(reinterpret_cast<PyObject *>(newType), propertiesAttr(),
                         properties_capsule) < 0) {
        Py_DECREF(newType);
        return nullptr;
    }

    return newType;
}
