// Copyright (C) 2018 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include "sbkenum.h"
#include "sbkenum_p.h"
#include "sbkstring.h"
#include "sbkstaticstrings.h"
#include "sbkstaticstrings_p.h"
#include "sbkconverter.h"
#include "basewrapper.h"
#include "autodecref.h"
#include "sbkpython.h"
#include "signature.h"

#include <cstring>
#include <vector>
#include <sstream>

#define SbkEnumType_Check(o) (Py_TYPE(Py_TYPE(o)) == SbkEnumType_TypeF())
using enum_func = PyObject *(*)(PyObject *, PyObject *);

using namespace Shiboken;

extern "C"
{

// forward
struct lastEnumCreated;

// forward
static PyTypeObject *recordCurrentEnum(PyObject *scopeOrModule,
                                       const char *name,
                                       PyTypeObject *enumType,
                                       PyTypeObject *flagsType);

struct SbkEnumType
{
    PyTypeObject type;
};

static void cleanupEnumTypes();

struct SbkEnumObject
{
    PyObject_HEAD
    Enum::EnumValueType ob_value;
    PyObject *ob_name;
};

static PyTypeObject *SbkEnum_TypeF();   // forward

static PyObject *SbkEnumObject_repr(PyObject *self)
{
    const SbkEnumObject *enumObj = reinterpret_cast<SbkEnumObject *>(self);
    auto name = Py_TYPE(self)->tp_name;
    if (enumObj->ob_name) {
        return String::fromFormat("%s.%s", name, PyBytes_AS_STRING(enumObj->ob_name));
    }
    return String::fromFormat("%s(%ld)", name, enumObj->ob_value);
}

static PyObject *SbkEnumObject_name(PyObject *self, void *)
{
    auto *enum_self = reinterpret_cast<SbkEnumObject *>(self);

    if (enum_self->ob_name == nullptr)
        Py_RETURN_NONE;

    Py_INCREF(enum_self->ob_name);
    return enum_self->ob_name;
}

static PyObject *SbkEnum_tp_new(PyTypeObject *type, PyObject *args, PyObject *)
{
    long itemValue = 0;
    if (!PyArg_ParseTuple(args, "|l:__new__", &itemValue))
        return nullptr;

    if (type == SbkEnum_TypeF()) {
        PyErr_Format(PyExc_TypeError, "You cannot use %s directly", type->tp_name);
        return nullptr;
    }

    SbkEnumObject *self = PyObject_New(SbkEnumObject, type);
    if (!self)
        return nullptr;
    self->ob_value = itemValue;
    AutoDecRef item(Enum::getEnumItemFromValue(type, itemValue));
    self->ob_name = item.object() ? SbkEnumObject_name(item, nullptr) : nullptr;
    return reinterpret_cast<PyObject *>(self);
}

static const char *SbkEnum_SignatureStrings[] = {
    "Shiboken.Enum(self,itemValue:int=0)",
    nullptr}; // Sentinel

static void enum_object_dealloc(PyObject *ob)
{
    auto *self = reinterpret_cast<SbkEnumObject *>(ob);
    Py_XDECREF(self->ob_name);
    Sbk_object_dealloc(ob);
}

static PyObject *_enum_op(enum_func f, PyObject *a, PyObject *b) {
    PyObject *valA = a;
    PyObject *valB = b;
    PyObject *result = nullptr;
    bool enumA = false;
    bool enumB = false;

    // We are not allowing floats
    if (!PyFloat_Check(valA) && !PyFloat_Check(valB)) {
        // Check if both variables are SbkEnumObject
        if (SbkEnumType_Check(valA)) {
            valA = PyLong_FromLong(reinterpret_cast<SbkEnumObject *>(valA)->ob_value);
            enumA = true;
        }
        if (SbkEnumType_Check(valB)) {
            valB = PyLong_FromLong(reinterpret_cast<SbkEnumObject *>(valB)->ob_value);
            enumB = true;
        }
    }

    // Without an enum we are not supporting the operation
    if (!(enumA || enumB)) {
        Py_INCREF(Py_NotImplemented);
        return Py_NotImplemented;
    }

    result = f(valA, valB);

    // Decreasing the reference of the used variables a and b.
    if (enumA)
        Py_DECREF(valA);
    if (enumB)
        Py_DECREF(valB);
    return result;
}

/* Notes:
 *   On Py3k land we use long type when using integer numbers. However, on older
 *   versions of Python (version 2) we need to convert it to int type,
 *   respectively.
 *
 *   Thus calling PyLong_FromLong() will result in calling PyLong_FromLong in
 *   Py3k.
 */
static PyObject *enum_int(PyObject *v)
{
    return PyLong_FromLong(reinterpret_cast<SbkEnumObject *>(v)->ob_value);
}

static PyObject *enum_and(PyObject *self, PyObject *b)
{
    return _enum_op(PyNumber_And, self, b);
}

static PyObject *enum_or(PyObject *self, PyObject *b)
{
    return _enum_op(PyNumber_Or, self, b);
}

static PyObject *enum_xor(PyObject *self, PyObject *b)
{
    return _enum_op(PyNumber_Xor, self, b);
}

static int enum_bool(PyObject *v)
{
    return (reinterpret_cast<SbkEnumObject *>(v)->ob_value > 0);
}

static PyObject *enum_add(PyObject *self, PyObject *v)
{
    return _enum_op(PyNumber_Add, self, v);
}

static PyObject *enum_subtract(PyObject *self, PyObject *v)
{
    return _enum_op(PyNumber_Subtract, self, v);
}

static PyObject *enum_multiply(PyObject *self, PyObject *v)
{
    return _enum_op(PyNumber_Multiply, self, v);
}

static PyObject *enum_richcompare(PyObject *self, PyObject *other, int op)
{
    PyObject *valA = self;
    PyObject *valB = other;
    PyObject *result = nullptr;
    bool enumA = false;
    bool enumB = false;

    // We are not allowing floats
    if (!PyFloat_Check(valA) && !PyFloat_Check(valB)) {

        // Check if both variables are SbkEnumObject
        if (SbkEnumType_Check(valA)) {
            valA = PyLong_FromLong(reinterpret_cast<SbkEnumObject *>(valA)->ob_value);
            enumA = true;
        }
        if (SbkEnumType_Check(valB)) {
            valB = PyLong_FromLong(reinterpret_cast<SbkEnumObject *>(valB)->ob_value);
            enumB =true;
        }
    }

    // Without an enum we are not supporting the operation
    if (!(enumA || enumB)) {
        Py_INCREF(Py_NotImplemented);
        return Py_NotImplemented;
    }
    result = PyObject_RichCompare(valA, valB, op);

    // Decreasing the reference of the used variables a and b.
    if (enumA)
        Py_DECREF(valA);
    if (enumB)
        Py_DECREF(valB);

    return result;
}

static Py_hash_t enum_hash(PyObject *pyObj)
{
    Py_hash_t val = reinterpret_cast<SbkEnumObject *>(pyObj)->ob_value;
    if (val == -1)
        val = -2;
    return val;
}

static PyGetSetDef SbkEnumGetSetList[] = {
    {const_cast<char *>("name"), SbkEnumObject_name, nullptr, nullptr, nullptr},
    {nullptr, nullptr, nullptr, nullptr, nullptr} // Sentinel
};

static void SbkEnumTypeDealloc(PyObject *pyObj);
static PyTypeObject *SbkEnumTypeTpNew(PyTypeObject *metatype, PyObject *args, PyObject *kwds);

static PyType_Slot SbkEnumType_Type_slots[] = {
    {Py_tp_dealloc, reinterpret_cast<void *>(SbkEnumTypeDealloc)},
    {Py_tp_base, reinterpret_cast<void *>(&PyType_Type)},
    {Py_tp_alloc, reinterpret_cast<void *>(PyType_GenericAlloc)},
    {Py_tp_new, reinterpret_cast<void *>(SbkEnumTypeTpNew)},
    {Py_tp_free, reinterpret_cast<void *>(PyObject_GC_Del)},
    {0, nullptr}
};

// PYSIDE-535: The tp_itemsize field is inherited and does not need to be set.
// In PyPy, it _must_ not be set, because it would have the meaning that a
// `__len__` field must be defined. Not doing so creates a hard-to-find crash.
static PyType_Spec SbkEnumType_Type_spec = {
    "1:Shiboken.EnumMeta",
    0,
    0, // sizeof(PyMemberDef), not for PyPy without a __len__ defined
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE,
    SbkEnumType_Type_slots,
};

PyTypeObject *SbkEnumType_TypeF(void)
{
    static auto *type = SbkType_FromSpec(&SbkEnumType_Type_spec);
    return type;
}

static void SbkEnumTypeDealloc(PyObject *pyObj)
{
    auto *enumType = reinterpret_cast<SbkEnumType *>(pyObj);
    auto *setp = PepType_SETP(enumType);

    PyObject_GC_UnTrack(pyObj);
#ifndef Py_LIMITED_API
#  if PY_VERSION_HEX >= 0x030A0000
    Py_TRASHCAN_BEGIN(pyObj, 1);
#  else
    Py_TRASHCAN_SAFE_BEGIN(pyObj);
#  endif
#endif
    if (setp->converter)
        Conversions::deleteConverter(setp->converter);
    PepType_SETP_delete(enumType);
#ifndef Py_LIMITED_API
#  if PY_VERSION_HEX >= 0x030A0000
    Py_TRASHCAN_END;
#  else
    Py_TRASHCAN_SAFE_END(pyObj);
#  endif
#endif
    if (PepRuntime_38_flag) {
        // PYSIDE-939: Handling references correctly.
        // This was not needed before Python 3.8 (Python issue 35810)
        Py_DECREF(Py_TYPE(pyObj));
    }
}

PyTypeObject *SbkEnumTypeTpNew(PyTypeObject *metatype, PyObject *args, PyObject *kwds)
{
    init_enum();
    return PepType_Type_tp_new(metatype, args, kwds);
}

} // extern "C"

///////////////////////////////////////////////////////////////
//
// PYSIDE-15: Pickling Support for Qt Enum objects
//            This works very well and fixes the issue.
//
extern "C" {

static PyObject *enum_unpickler = nullptr;

// Pickling: reduce the Qt Enum object
static PyObject *enum___reduce__(PyObject *obj)
{
    init_enum();
    return Py_BuildValue("O(Ni)",
                         enum_unpickler,
                         Py_BuildValue("s", Py_TYPE(obj)->tp_name),
                         PyLong_AS_LONG(obj));
}

} // extern "C"

namespace Shiboken { namespace Enum {

// Unpickling: rebuild the Qt Enum object
PyObject *unpickleEnum(PyObject *enum_class_name, PyObject *value)
{
    AutoDecRef parts(PyObject_CallMethod(enum_class_name,
                               "split", "s", "."));
    if (parts.isNull())
        return nullptr;
    PyObject *top_name = PyList_GetItem(parts, 0); // borrowed ref
    if (top_name == nullptr)
        return nullptr;
    PyObject *module = PyImport_GetModule(top_name);
    if (module == nullptr) {
        PyErr_Format(PyExc_ImportError, "could not import module %.200s",
            String::toCString(top_name));
        return nullptr;
    }
    AutoDecRef cur_thing(module);
    int len = PyList_Size(parts);
    for (int idx = 1; idx < len; ++idx) {
        PyObject *name = PyList_GetItem(parts, idx); // borrowed ref
        PyObject *thing = PyObject_GetAttr(cur_thing, name);
        if (thing == nullptr) {
            PyErr_Format(PyExc_ImportError, "could not import Qt Enum type %.200s",
                String::toCString(enum_class_name));
            return nullptr;
        }
        cur_thing.reset(thing);
    }
    PyObject *klass = cur_thing;
    return PyObject_CallFunctionObjArgs(klass, value, nullptr);
}

int enumOption{};

} // namespace Enum
} // namespace Shiboken

extern "C" {

// Initialization
static bool _init_enum()
{
    AutoDecRef shibo(PyImport_ImportModule("shiboken6.Shiboken"));
    auto mod = shibo.object();
    // publish Shiboken.Enum so that the signature gets initialized
    if (PyObject_SetAttrString(mod, "Enum", reinterpret_cast<PyObject *>(SbkEnum_TypeF())) < 0)
        return false;
    if (InitSignatureStrings(SbkEnum_TypeF(), SbkEnum_SignatureStrings) < 0)
        return false;
    enum_unpickler = PyObject_GetAttrString(mod, "_unpickle_enum");
    if (enum_unpickler == nullptr)
        return false;
    return true;
}

static int useOldEnum = -1;

static PyMethodDef SbkEnumObject_Methods[] = {
    {"__reduce__", reinterpret_cast<PyCFunction>(enum___reduce__),
        METH_NOARGS, nullptr},
    {nullptr, nullptr, 0, nullptr} // Sentinel
};

static PyObject *PyEnumModule{};
static PyObject *PyEnumMeta{};
static PyObject *PyEnum{};
static PyObject *PyIntEnum{};
static PyObject *PyFlag{};
static PyObject *PyIntFlag{};
static PyObject *PyFlag_KEEP{};

bool PyEnumMeta_Check(PyObject *ob)
{
    return Py_TYPE(ob) == (useOldEnum ? SbkEnumType_TypeF()
                                      : reinterpret_cast<PyTypeObject *>(PyEnumMeta));
}

PyTypeObject *getPyEnumMeta()
{
    if (PyEnumMeta)
        return reinterpret_cast<PyTypeObject *>(PyEnumMeta);

    static auto *mod = PyImport_ImportModule("enum");
    if (mod) {
        PyEnumModule = mod;
        PyEnumMeta = PyObject_GetAttrString(mod, "EnumMeta");
        if (PyEnumMeta && PyType_Check(PyEnumMeta))
            PyEnum = PyObject_GetAttrString(mod, "Enum");
        if (PyEnum && PyType_Check(PyEnum))
            PyIntEnum = PyObject_GetAttrString(mod, "IntEnum");
        if (PyIntEnum && PyType_Check(PyIntEnum))
            PyFlag = PyObject_GetAttrString(mod, "Flag");
        if (PyFlag && PyType_Check(PyFlag))
            PyIntFlag = PyObject_GetAttrString(mod, "IntFlag");
        if (PyIntFlag && PyType_Check(PyIntFlag)) {
            // KEEP is defined from Python 3.11 on.
            PyFlag_KEEP = PyObject_GetAttrString(mod, "KEEP");
            PyErr_Clear();
            return reinterpret_cast<PyTypeObject *>(PyEnumMeta);
        }
    }
    Py_FatalError("Python module 'enum' not found");
    return nullptr;
}

void init_enum()
{
    static bool isInitialized = false;
    if (isInitialized)
        return;
    if (!(isInitialized || enum_unpickler || _init_enum()))
        Py_FatalError("could not load enum pickling helper function");
    Py_AtExit(cleanupEnumTypes);

    // PYSIDE-1735: Determine whether we should use the old or the new enum implementation.
    static PyObject *option = PySys_GetObject("pyside63_option_python_enum");
    if (!option || !PyLong_Check(option)) {
        PyErr_Clear();
        option = PyLong_FromLong(0);
    }
    int ignoreOver{};
    Enum::enumOption = PyLong_AsLongAndOverflow(option, &ignoreOver);
    useOldEnum = Enum::enumOption == Enum::ENOPT_OLD_ENUM;
    getPyEnumMeta();
    isInitialized = true;
}

// PYSIDE-1735: Helper function supporting QEnum
int enumIsFlag(PyObject *ob_type)
{
    init_enum();

    auto *metatype = Py_TYPE(ob_type);
    if (metatype != reinterpret_cast<PyTypeObject *>(PyEnumMeta))
        return -1;
    auto *mro = reinterpret_cast<PyTypeObject *>(ob_type)->tp_mro;
    Py_ssize_t idx, n = PyTuple_GET_SIZE(mro);
    for (idx = 0; idx < n; idx++) {
        auto *sub_type = reinterpret_cast<PyTypeObject *>(PyTuple_GET_ITEM(mro, idx));
        if (sub_type == reinterpret_cast<PyTypeObject *>(PyFlag))
            return 1;
    }
    return 0;
}

// PYSIDE-1735: Helper function to ask what enum we are using
bool usingNewEnum()
{
    init_enum();
    return !useOldEnum;
}

} // extern "C"

//
///////////////////////////////////////////////////////////////

namespace Shiboken {

class DeclaredEnumTypes
{
public:
    struct EnumEntry
    {
        char *name; // full name as allocated. type->tp_name might be a substring.
        PyTypeObject *type;
    };

    DeclaredEnumTypes(const DeclaredEnumTypes &) = delete;
    DeclaredEnumTypes(DeclaredEnumTypes &&) = delete;
    DeclaredEnumTypes &operator=(const DeclaredEnumTypes &) = delete;
    DeclaredEnumTypes &operator=(DeclaredEnumTypes &&) = delete;

    DeclaredEnumTypes();
    ~DeclaredEnumTypes();
    static DeclaredEnumTypes &instance();
    void addEnumType(const EnumEntry &e) { m_enumTypes.push_back(e); }

    void cleanup();

private:
    std::vector<EnumEntry> m_enumTypes;
};

namespace Enum {

// forward
static PyObject *newItemOld(PyTypeObject *enumType, EnumValueType itemValue,
                            const char *itemName);

// forward
static PyTypeObject * newTypeWithNameOld(const char *name,
                                         const char *cppName,
                                         PyTypeObject *numbers_fromFlag);

bool check(PyObject *pyObj)
{
    init_enum();

    // PYSIDE-1735: Decide dynamically if new or old enums will be used.
    if (useOldEnum)
        return Py_TYPE(Py_TYPE(pyObj)) == SbkEnumType_TypeF();

    static PyTypeObject *meta = getPyEnumMeta();
    return Py_TYPE(Py_TYPE(pyObj)) == reinterpret_cast<PyTypeObject *>(meta);
}

static PyObject *getEnumItemFromValueOld(PyTypeObject *enumType,
                                         EnumValueType itemValue)
{
    PyObject *key, *value;
    Py_ssize_t pos = 0;
    PyObject *values = PyDict_GetItem(enumType->tp_dict, PyName::values());
    if (values == nullptr)
        return nullptr;

    while (PyDict_Next(values, &pos, &key, &value)) {
        auto *obj = reinterpret_cast<SbkEnumObject *>(value);
        if (obj->ob_value == itemValue) {
            Py_INCREF(value);
            return value;
        }
    }
    return nullptr;
}

PyObject *getEnumItemFromValue(PyTypeObject *enumType, EnumValueType itemValue)
{
    init_enum();
    // PYSIDE-1735: Decide dynamically if new or old enums will be used.
    if (useOldEnum)
        return getEnumItemFromValueOld(enumType, itemValue);

    auto *obEnumType = reinterpret_cast<PyObject *>(enumType);
    AutoDecRef val2members(PyObject_GetAttrString(obEnumType, "_value2member_map_"));
    if (val2members.isNull()) {
        PyErr_Clear();
        return nullptr;
    }
    AutoDecRef ob_value(PyLong_FromLongLong(itemValue));
    auto *result = PyDict_GetItem(val2members, ob_value);
    Py_XINCREF(result);
    return result;
}

static PyTypeObject *createEnum(const char *fullName, const char *cppName,
                                PyTypeObject *flagsType)
{
    init_enum();
    PyTypeObject *enumType = newTypeWithNameOld(fullName, cppName, flagsType);
    if (PyType_Ready(enumType) < 0) {
        Py_XDECREF(enumType);
        return nullptr;
    }
    return enumType;
}

PyTypeObject *createGlobalEnum(PyObject *module, const char *name, const char *fullName,
                               const char *cppName, PyTypeObject *flagsType)
{
    PyTypeObject *enumType = createEnum(fullName, cppName, flagsType);
    if (enumType && PyModule_AddObject(module, name, reinterpret_cast<PyObject *>(enumType)) < 0) {
        Py_DECREF(enumType);
        return nullptr;
    }
    flagsType = recordCurrentEnum(module, name, enumType, flagsType);
    if (flagsType && PyModule_AddObject(module, PepType_GetNameStr(flagsType),
            reinterpret_cast<PyObject *>(flagsType)) < 0) {
        Py_DECREF(enumType);
        return nullptr;
    }
    return enumType;
}

PyTypeObject *createScopedEnum(PyTypeObject *scope, const char *name, const char *fullName,
                               const char *cppName, PyTypeObject *flagsType)
{
    PyTypeObject *enumType = createEnum(fullName, cppName, flagsType);
    if (enumType && PyDict_SetItemString(scope->tp_dict, name,
            reinterpret_cast<PyObject *>(enumType)) < 0) {
        Py_DECREF(enumType);
        return nullptr;
    }
    auto *obScope = reinterpret_cast<PyObject *>(scope);
    flagsType = recordCurrentEnum(obScope, name, enumType, flagsType);
    if (flagsType && PyDict_SetItemString(scope->tp_dict,
            PepType_GetNameStr(flagsType),
            reinterpret_cast<PyObject *>(flagsType)) < 0) {
        Py_DECREF(enumType);
        return nullptr;
    }
    return enumType;
}

static PyObject *createEnumItem(PyTypeObject *enumType, const char *itemName,
                                EnumValueType itemValue)
{
    init_enum();
    PyObject *enumItem = newItemOld(enumType, itemValue, itemName);
    if (PyDict_SetItemString(enumType->tp_dict, itemName, enumItem) < 0) {
        Py_DECREF(enumItem);
        return nullptr;
    }
    return enumItem;
}

bool createGlobalEnumItem(PyTypeObject *enumType, PyObject *module,
                          const char *itemName, EnumValueType itemValue)
{
    PyObject *enumItem = createEnumItem(enumType, itemName, itemValue);
    if (!enumItem)
        return false;
    int ok = useOldEnum ? PyModule_AddObject(module, itemName, enumItem) : true;
    Py_DECREF(enumItem);
    return ok >= 0;
}

bool createScopedEnumItem(PyTypeObject *enumType, PyTypeObject *scope,
                          const char *itemName, EnumValueType itemValue)
{
    PyObject *enumItem = createEnumItem(enumType, itemName, itemValue);
    if (!enumItem)
        return false;
    int ok = useOldEnum ? PyDict_SetItemString(scope->tp_dict, itemName, enumItem) : true;
    Py_DECREF(enumItem);
    return ok >= 0;
}

// This exists temporary as the old way to create an enum item.
// For the public interface, we use a new function
static PyObject *newItemOld(PyTypeObject *enumType,
                            EnumValueType itemValue, const char *itemName)
{
    bool newValue = true;
    SbkEnumObject *enumObj;
    if (!itemName) {
        enumObj = reinterpret_cast<SbkEnumObject *>(
                      getEnumItemFromValue(enumType, itemValue));
        if (enumObj)
            return reinterpret_cast<PyObject *>(enumObj);

        newValue = false;
    }

    enumObj = PyObject_New(SbkEnumObject, enumType);
    if (!enumObj)
        return nullptr;

    enumObj->ob_name = itemName ? PyBytes_FromString(itemName) : nullptr;
    enumObj->ob_value = itemValue;

    if (newValue) {
        auto dict = enumType->tp_dict;  // Note: 'values' is borrowed
        PyObject *values = PyDict_GetItemWithError(dict, PyName::values());
        if (values == nullptr) {
            if (PyErr_Occurred())
                return nullptr;
            AutoDecRef new_values(values = PyDict_New());
            if (values == nullptr)
                return nullptr;
            if (PyDict_SetItem(dict, PyName::values(), values) < 0)
                return nullptr;
        }
        PyDict_SetItemString(values, itemName, reinterpret_cast<PyObject *>(enumObj));
    }

    return reinterpret_cast<PyObject *>(enumObj);
}

PyObject *newItem(PyTypeObject *enumType, EnumValueType itemValue,
                  const char *itemName)
{
    init_enum();
    // PYSIDE-1735: Decide dynamically if new or old enums will be used.
    if (useOldEnum)
        return newItemOld(enumType, itemValue, itemName);

    auto *obEnumType = reinterpret_cast<PyObject *>(enumType);
    if (!itemName)
        return PyObject_CallFunction(obEnumType, "L", itemValue);

    static PyObject *const _member_map_ = String::createStaticString("_member_map_");
    auto *member_map = PyDict_GetItem(enumType->tp_dict, _member_map_);
    if (!(member_map && PyDict_Check(member_map)))
        return nullptr;
    auto *result = PyDict_GetItemString(member_map, itemName);
    Py_XINCREF(result);
    return result;
}

} // namespace Shiboken
} // namespace Enum

static PyType_Slot SbkNewEnum_slots[] = {
    {Py_tp_repr, reinterpret_cast<void *>(SbkEnumObject_repr)},
    {Py_tp_str, reinterpret_cast<void *>(SbkEnumObject_repr)},
    {Py_tp_getset, reinterpret_cast<void *>(SbkEnumGetSetList)},
    {Py_tp_methods, reinterpret_cast<void *>(SbkEnumObject_Methods)},
    {Py_tp_new, reinterpret_cast<void *>(SbkEnum_tp_new)},
    {Py_nb_add, reinterpret_cast<void *>(enum_add)},
    {Py_nb_subtract, reinterpret_cast<void *>(enum_subtract)},
    {Py_nb_multiply, reinterpret_cast<void *>(enum_multiply)},
    {Py_nb_positive, reinterpret_cast<void *>(enum_int)},
    {Py_nb_bool, reinterpret_cast<void *>(enum_bool)},
    {Py_nb_and, reinterpret_cast<void *>(enum_and)},
    {Py_nb_xor, reinterpret_cast<void *>(enum_xor)},
    {Py_nb_or, reinterpret_cast<void *>(enum_or)},
    {Py_nb_int, reinterpret_cast<void *>(enum_int)},
    {Py_nb_index, reinterpret_cast<void *>(enum_int)},
    {Py_tp_richcompare, reinterpret_cast<void *>(enum_richcompare)},
    {Py_tp_hash, reinterpret_cast<void *>(enum_hash)},
    {Py_tp_dealloc, reinterpret_cast<void *>(enum_object_dealloc)},
    {0, nullptr}
};
static PyType_Spec SbkNewEnum_spec = {
    "1:Shiboken.Enum",
    sizeof(SbkEnumObject),
    0,
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE,
    SbkNewEnum_slots,
};

static PyTypeObject *SbkEnum_TypeF()
{
    static auto type = SbkType_FromSpecWithMeta(&SbkNewEnum_spec, SbkEnumType_TypeF());
    return type;
}

namespace Shiboken { namespace Enum {

static void
copyNumberMethods(PyTypeObject *flagsType,
                  PyType_Slot number_slots[],
                  int *pidx)
{
    int idx = *pidx;
#define PUT_SLOT(name) \
    number_slots[idx].slot = (name);                                \
    number_slots[idx].pfunc = PyType_GetSlot(flagsType, (name));    \
    ++idx;

    PUT_SLOT(Py_nb_absolute);
    PUT_SLOT(Py_nb_add);
    PUT_SLOT(Py_nb_and);
    PUT_SLOT(Py_nb_bool);
    PUT_SLOT(Py_nb_divmod);
    PUT_SLOT(Py_nb_float);
    PUT_SLOT(Py_nb_floor_divide);
    PUT_SLOT(Py_nb_index);
    PUT_SLOT(Py_nb_inplace_add);
    PUT_SLOT(Py_nb_inplace_and);
    PUT_SLOT(Py_nb_inplace_floor_divide);
    PUT_SLOT(Py_nb_inplace_lshift);
    PUT_SLOT(Py_nb_inplace_multiply);
    PUT_SLOT(Py_nb_inplace_or);
    PUT_SLOT(Py_nb_inplace_power);
    PUT_SLOT(Py_nb_inplace_remainder);
    PUT_SLOT(Py_nb_inplace_rshift);
    PUT_SLOT(Py_nb_inplace_subtract);
    PUT_SLOT(Py_nb_inplace_true_divide);
    PUT_SLOT(Py_nb_inplace_xor);
    PUT_SLOT(Py_nb_int);
    PUT_SLOT(Py_nb_invert);
    PUT_SLOT(Py_nb_lshift);
    PUT_SLOT(Py_nb_multiply);
    PUT_SLOT(Py_nb_negative);
    PUT_SLOT(Py_nb_or);
    PUT_SLOT(Py_nb_positive);
    PUT_SLOT(Py_nb_power);
    PUT_SLOT(Py_nb_remainder);
    PUT_SLOT(Py_nb_rshift);
    PUT_SLOT(Py_nb_subtract);
    PUT_SLOT(Py_nb_true_divide);
    PUT_SLOT(Py_nb_xor);
#undef PUT_SLOT
    *pidx = idx;
}

static PyTypeObject * newTypeWithNameOld(const char *name,
                                         const char *cppName,
                                         PyTypeObject *numbers_fromFlag)
{
    // Careful: SbkType_FromSpec does not allocate the string.
    PyType_Slot newslots[99] = {};  // enough but not too big for the stack
    PyType_Spec newspec;
    DeclaredEnumTypes::EnumEntry entry{strdup(name), nullptr};
    newspec.name = entry.name; // Note that SbkType_FromSpec might use a substring.
    newspec.basicsize = SbkNewEnum_spec.basicsize;
    newspec.itemsize = SbkNewEnum_spec.itemsize;
    newspec.flags = SbkNewEnum_spec.flags;
    // we must append all the number methods, so rebuild everything:
    int idx = 0;
    while (SbkNewEnum_slots[idx].slot) {
        newslots[idx].slot = SbkNewEnum_slots[idx].slot;
        newslots[idx].pfunc = SbkNewEnum_slots[idx].pfunc;
        ++idx;
    }
    if (numbers_fromFlag)
        copyNumberMethods(numbers_fromFlag, newslots, &idx);
    newspec.slots = newslots;
    AutoDecRef bases(PyTuple_New(1));
    static auto basetype = reinterpret_cast<PyObject *>(SbkEnum_TypeF());
    Py_INCREF(basetype);
    PyTuple_SetItem(bases, 0, basetype);
    auto *type = SbkType_FromSpecBasesMeta(&newspec, bases, SbkEnumType_TypeF());
    entry.type = type;

    auto *enumType = reinterpret_cast<SbkEnumType *>(type);
    auto *setp = PepType_SETP(enumType);
    setp->cppName = cppName;
    DeclaredEnumTypes::instance().addEnumType(entry);
    return entry.type;
}

// PySIDE-1735: This function is in the API and should be removed in 6.4 .
//              Python enums are created differently.
PyTypeObject *newTypeWithName(const char *name,
                              const char *cppName,
                              PyTypeObject *numbers_fromFlag)
{
    if (!useOldEnum)
        PyErr_Format(PyExc_RuntimeError, "function `%s` can no longer be used when the Python "
            "Enum's have been selected", __FUNCTION__);
    return newTypeWithNameOld(name, cppName, numbers_fromFlag);
}

const char *getCppName(PyTypeObject *enumType)
{
    assert(Py_TYPE(enumType) == SbkEnumType_TypeF());
    auto *type = reinterpret_cast<SbkEnumType *>(enumType);
    auto *setp = PepType_SETP(type);
    return setp->cppName;
}

EnumValueType getValue(PyObject *enumItem)
{
    init_enum();

    assert(Enum::check(enumItem));

    // PYSIDE-1735: Decide dynamically if new or old enums will be used.
    if (useOldEnum)
        return reinterpret_cast<SbkEnumObject *>(enumItem)->ob_value;

    AutoDecRef pyValue(PyObject_GetAttrString(enumItem, "value"));
    return PyLong_AsLongLong(pyValue);
}

void setTypeConverter(PyTypeObject *type, SbkConverter *converter, bool isFlag)
{
    if (isFlag) {
        auto *flagsType = reinterpret_cast<PySideQFlagsType *>(type);
        PepType_PFTP(flagsType)->converter = converter;
    }
    else {
        auto *enumType = reinterpret_cast<SbkEnumType *>(type);
        PepType_SETP(enumType)->converter = converter;
    }
}

} // namespace Enum

DeclaredEnumTypes &DeclaredEnumTypes::instance()
{
    static DeclaredEnumTypes me;
    return me;
}

DeclaredEnumTypes::DeclaredEnumTypes() = default;

DeclaredEnumTypes::~DeclaredEnumTypes()
{
   cleanup();
}

void DeclaredEnumTypes::cleanup()
{
    static bool was_called = false;
    if (was_called)
        return;

    for (const auto &e : m_enumTypes) {
        std::free(e.name);
    }
    m_enumTypes.clear();
    was_called = true;
}

} // namespace Shiboken

static void cleanupEnumTypes()
{
    DeclaredEnumTypes::instance().cleanup();
}

///////////////////////////////////////////////////////////////////////
//
// PYSIDE-1735: Re-implementation of Enums using Python
// ====================================================
//
// This is a very simple, first implementation of a replacement
// for the Qt-like Enums using the Python Enum module.
//
// The basic idea:
// ---------------
// * We create the Enums as always
// * After creation of each enum, a special function is called that
//   * grabs the last generated enum
//   * reads all Enum items
//   * generates a class statement for the Python Enum
//   * creates a new Python Enum class
//   * replaces the already inserted Enum with the new one.
//
// There are lots of ways to optimize that. Will be added later.
//
extern "C" {

struct lastEnumCreated {
    PyObject *scopeOrModule;
    const char *name;
    PyTypeObject *enumType;
    PyTypeObject *flagsType;
};

static lastEnumCreated lec{};

static PyTypeObject *recordCurrentEnum(PyObject *scopeOrModule,
                                       const char *name,
                                       PyTypeObject *enumType,
                                       PyTypeObject *flagsType)
{
    lec.scopeOrModule = scopeOrModule;
    lec.name = name;
    lec.enumType = enumType;
    lec.flagsType = flagsType;

    // PYSIDE-1735: Decide dynamically if new or old enums will be used.
    if (useOldEnum)
        return flagsType;

    // We return nullptr as flagsType to disable flag creation.
    return nullptr;
}

static bool is_old_version()
{
    auto *version = PySys_GetObject("version_info");
    auto *major = PyTuple_GetItem(version, 0);
    auto *minor = PyTuple_GetItem(version, 1);
    auto number = PyLong_AsLong(major) * 1000 + PyLong_AsLong(minor);
    return number <= 3008;
}

///////////////////////////////////////////////////////////////////////
//
// Support for Missing Values
// ==========================
//
// Qt enums sometimes use undefined values in enums.
// The enum module handles this by the option "KEEP" for Flag and
// IntFlag. The handling of missing enum values is still strict.
//
// We changed that (also for compatibility with some competitor)
// and provide a `_missing_` function that creates the missing value.
//
// The idea:
// ---------
// We cannot modify the already created class.
// But we can create a one-element class with the new value and
// pretend that this is the already existing class.
//
// We create each constant only once and keep the result in a dict
// "_sbk_missing_". This is similar to a competitor's "_sip_missing_".
//
static PyObject *missing_func(PyObject * /* self */ , PyObject *args)
{
    // In order to relax matters to be more compatible with C++, we need
    // to create a pseudo-member with that value.
    static auto *const _sbk_missing = Shiboken::String::createStaticString("_sbk_missing_");
    static auto *const _name = Shiboken::String::createStaticString("__name__");
    static auto *const _mro = Shiboken::String::createStaticString("__mro__");
    static auto *const _class = Shiboken::String::createStaticString("__class__");

    PyObject *klass{}, *value{};
    if (!PyArg_UnpackTuple(args, "missing", 2, 2, &klass, &value))
        Py_RETURN_NONE;
    if (!PyLong_Check(value))
        Py_RETURN_NONE;
    auto *type = reinterpret_cast<PyTypeObject *>(klass);
    auto *sbk_missing = PyDict_GetItem(type->tp_dict, _sbk_missing);
    if (!sbk_missing) {
        sbk_missing = PyDict_New();
        PyDict_SetItem(type->tp_dict, _sbk_missing, sbk_missing);
    }
    // See if the value is already in the dict.
    AutoDecRef val_str(PyObject_CallMethod(value, "__str__", nullptr));
    auto *ret = PyDict_GetItem(sbk_missing, val_str);
    if (ret) {
        Py_INCREF(ret);
        return ret;
    }
    // No, we must create a new object and insert it into the dict.
    AutoDecRef cls_name(PyObject_GetAttr(klass, _name));
    AutoDecRef mro(PyObject_GetAttr(klass, _mro));
    auto *baseClass(PyTuple_GetItem(mro, 1));
    AutoDecRef param(PyDict_New());
    PyDict_SetItem(param, val_str, value);
    AutoDecRef fake(PyObject_CallFunctionObjArgs(baseClass, cls_name.object(), param.object(),
                                                 nullptr));
    ret = PyObject_GetAttr(fake, val_str);
    PyDict_SetItem(sbk_missing, val_str, ret);
    // Now the real fake: Pretend that the type is our original type!
    PyObject_SetAttr(ret, _class, klass);
    return ret;
}

static struct PyMethodDef dummy_methods[] = {
    {"_missing_", reinterpret_cast<PyCFunction>(missing_func), METH_VARARGS|METH_STATIC, nullptr},
    {nullptr, nullptr, 0, nullptr}
};

static PyType_Slot dummy_slots[] = {
    {Py_tp_base, reinterpret_cast<void *>(&PyType_Type)},
    {Py_tp_methods, reinterpret_cast<void *>(dummy_methods)},
    {0, nullptr}
};

static PyType_Spec dummy_spec = {
    "1:builtins.EnumType",
    0,
    0,
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE,
    dummy_slots,
};

static PyObject *create_missing_func(PyObject *klass)
{
    // When creating the class, memorize it in the missing function by
    // a partial function argument.
    static auto *const type = SbkType_FromSpec(&dummy_spec);
    static auto *const obType = reinterpret_cast<PyObject *>(type);
    static auto *const _missing = Shiboken::String::createStaticString("_missing_");
    static auto *const func = PyObject_GetAttr(obType, _missing);
    static auto *const partial = Pep_GetPartialFunction();
    return PyObject_CallFunctionObjArgs(partial, func, klass, nullptr);
}
//
////////////////////////////////////////////////////////////////////////

PyTypeObject *morphLastEnumToPython()
{
    /// The Python Enum internal structure is way too complicated.
    /// It is much easier to generate Python code and execute it.

    // Pick up the last generated Enum and convert it into a PyEnum
    auto *enumType = lec.enumType;
    // This is temporary; SbkEnumType will be removed, soon.

    auto *scopeOrModule = lec.scopeOrModule;
    static PyObject *enumName = String::createStaticString("IntEnum");
    if (PyType_Check(scopeOrModule)) {
        // For global objects, we have no good solution, yet where to put the int info.
        auto type = reinterpret_cast<PyTypeObject *>(scopeOrModule);
        auto *sotp = PepType_SOTP(type);
        if (!sotp->enumFlagsDict)
            initEnumFlagsDict(type);
        enumName = PyDict_GetItem(sotp->enumTypeDict, String::fromCString(lec.name));
    }

    PyObject *key, *value;
    Py_ssize_t pos = 0;
    PyObject *values = PyDict_GetItem(enumType->tp_dict, PyName::values());
    if (!values)
        return nullptr;

    AutoDecRef PyEnumType(PyObject_GetAttr(PyEnumModule, enumName));
    assert(PyEnumType.object());
    bool isFlag = PyObject_IsSubclass(PyEnumType, PyFlag);

    // See if we should use the Int versions of the types, again
    bool useIntInheritance = Enum::enumOption & Enum::ENOPT_INHERIT_INT;
    if (useIntInheritance) {
        auto *surrogate = PyObject_IsSubclass(PyEnumType, PyFlag) ? PyIntFlag : PyIntEnum;
        Py_INCREF(surrogate);
        PyEnumType.reset(surrogate);
    }

    // Walk the values dict and create a Python enum type.
    AutoDecRef name(PyUnicode_FromString(lec.name));
    AutoDecRef args(PyList_New(0));
    auto *pyName = name.object();
    auto *pyArgs = args.object();
    while (PyDict_Next(values, &pos, &key, &value)) {
        auto *key_value = PyTuple_New(2);
        PyTuple_SET_ITEM(key_value, 0, key);
        Py_INCREF(key);
        auto *obj = reinterpret_cast<SbkEnumObject *>(value);
        auto *num = PyLong_FromLongLong(obj->ob_value);
        PyTuple_SET_ITEM(key_value, 1, num);
        PyList_Append(pyArgs, key_value);
    }
    // We now create the new type. Since Python 3.11, we need to pass in
    // `boundary=KEEP` because the default STRICT crashes on us.
    // See  QDir.Filter.Drives | QDir.Filter.Files
    AutoDecRef callArgs(Py_BuildValue("(OO)", pyName, pyArgs));
    AutoDecRef callDict(PyDict_New());
    static PyObject *boundary = String::createStaticString("boundary");
    if (PyFlag_KEEP)
        PyDict_SetItem(callDict, boundary, PyFlag_KEEP);
    auto *obNewType = PyObject_Call(PyEnumType, callArgs, callDict);
    if (!obNewType || PyObject_SetAttr(scopeOrModule, pyName, obNewType) < 0)
        return nullptr;

    // For compatibility with Qt enums, provide a permissive missing method for (Int)?Enum.
    if (!isFlag) {
        bool supportMissing = !(Enum::enumOption & Enum::ENOPT_NO_MISSING);
        if (supportMissing) {
            AutoDecRef enum_missing(create_missing_func(obNewType));
            PyObject_SetAttrString(obNewType, "_missing_", enum_missing);
        }
    }

    auto *newType = reinterpret_cast<PyTypeObject *>(obNewType);
    auto *obEnumType = reinterpret_cast<PyObject *>(enumType);
    AutoDecRef qual_name(PyObject_GetAttr(obEnumType, PyMagicName::qualname()));
    PyObject_SetAttr(obNewType, PyMagicName::qualname(), qual_name);
    AutoDecRef module(PyObject_GetAttr(obEnumType, PyMagicName::module()));
    PyObject_SetAttr(obNewType, PyMagicName::module(), module);

    // See if we should re-introduce shortcuts in the enclosing object.
    const bool useGlobalShortcut = (Enum::enumOption & Enum::ENOPT_GLOBAL_SHORTCUT) != 0;
    const bool useScopedShortcut = (Enum::enumOption & Enum::ENOPT_SCOPED_SHORTCUT) != 0;
    if (useGlobalShortcut || useScopedShortcut) {
        bool isModule = PyModule_Check(scopeOrModule);
        pos = 0;
        while (PyDict_Next(values, &pos, &key, &value)) {
            AutoDecRef entry(PyObject_GetAttr(obNewType, key));
            if ((useGlobalShortcut && isModule) || (useScopedShortcut && !isModule))
                if (PyObject_SetAttr(scopeOrModule, key, entry) < 0)
                    return nullptr;
        }
    }

    // PYSIDE-1735: Old Python versions can't stand the early enum deallocation.
    static bool old_python_version = is_old_version();
    if (old_python_version)
        Py_INCREF(obEnumType);
    return newType;
}

PyTypeObject *mapFlagsToSameEnum(PyTypeObject *FType, PyTypeObject *EType)
{
    // this will be switchable...
    return useOldEnum ? FType : EType;
}

} // extern "C"
