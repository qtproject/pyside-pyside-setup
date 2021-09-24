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

#define SbkEnumType_Check(o) (Py_TYPE(Py_TYPE(o)) == SbkEnumType_TypeF())
using enum_func = PyObject *(*)(PyObject *, PyObject *);

static void cleanupEnumTypes();

extern "C"
{

struct SbkEnumType
{
    PyTypeObject type;
};

struct SbkEnumObject
{
    PyObject_HEAD
    long ob_value;
    PyObject *ob_name;
};

static PyTypeObject *SbkEnum_TypeF();   // forward

static PyObject *SbkEnumObject_repr(PyObject *self)
{
    const SbkEnumObject *enumObj = reinterpret_cast<SbkEnumObject *>(self);
    auto name = Py_TYPE(self)->tp_name;
    if (enumObj->ob_name) {
        return Shiboken::String::fromFormat("%s.%s", name,
                                            PyBytes_AS_STRING(enumObj->ob_name));
    }
    return Shiboken::String::fromFormat("%s(%ld)", name, enumObj->ob_value);
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
    Shiboken::AutoDecRef item(Shiboken::Enum::getEnumItemFromValue(type, itemValue));
    self->ob_name = item.object() ? SbkEnumObject_name(item, nullptr) : nullptr;
    return reinterpret_cast<PyObject *>(self);
}

static const char *SbkEnum_SignatureStrings[] = {
    "Shiboken.Enum(self,itemValue:int=0)",
    nullptr}; // Sentinel

void enum_object_dealloc(PyObject *ob)
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
static PyType_Spec SbkEnumType_Type_spec = {
    "1:Shiboken.EnumMeta",
    0,
    sizeof(PyMemberDef),
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE,
    SbkEnumType_Type_slots,
};

PyTypeObject *SbkEnumType_TypeF(void)
{
    static auto *type = SbkType_FromSpec(&SbkEnumType_Type_spec);
    return type;
}

void SbkEnumTypeDealloc(PyObject *pyObj)
{
    auto *enumType = reinterpret_cast<SbkEnumType *>(pyObj);
    auto *setp = PepType_SETP(enumType);

    PyObject_GC_UnTrack(pyObj);
#ifndef Py_LIMITED_API
    Py_TRASHCAN_SAFE_BEGIN(pyObj);
#endif
    if (setp->converter)
        Shiboken::Conversions::deleteConverter(setp->converter);
    PepType_SETP_delete(enumType);
#ifndef Py_LIMITED_API
    Py_TRASHCAN_SAFE_END(pyObj);
#endif
    if (PepRuntime_38_flag) {
        // PYSIDE-939: Handling references correctly.
        // This was not needed before Python 3.8 (Python issue 35810)
        Py_DECREF(Py_TYPE(pyObj));
    }
}

PyTypeObject *SbkEnumTypeTpNew(PyTypeObject *metatype, PyObject *args, PyObject *kwds)
{
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
    Shiboken::AutoDecRef parts(PyObject_CallMethod(enum_class_name,
                               "split", "s", "."));
    if (parts.isNull())
        return nullptr;
    PyObject *top_name = PyList_GetItem(parts, 0); // borrowed ref
    if (top_name == nullptr)
        return nullptr;
    PyObject *module = PyImport_GetModule(top_name);
    if (module == nullptr) {
        PyErr_Format(PyExc_ImportError, "could not import module %.200s",
            Shiboken::String::toCString(top_name));
        return nullptr;
    }
    Shiboken::AutoDecRef cur_thing(module);
    int len = PyList_Size(parts);
    for (int idx = 1; idx < len; ++idx) {
        PyObject *name = PyList_GetItem(parts, idx); // borrowed ref
        PyObject *thing = PyObject_GetAttr(cur_thing, name);
        if (thing == nullptr) {
            PyErr_Format(PyExc_ImportError, "could not import Qt Enum type %.200s",
                Shiboken::String::toCString(enum_class_name));
            return nullptr;
        }
        cur_thing.reset(thing);
    }
    PyObject *klass = cur_thing;
    return PyObject_CallFunctionObjArgs(klass, value, nullptr);
}

} // namespace Enum
} // namespace Shiboken

extern "C" {

// Initialization
static bool _init_enum()
{
    Shiboken::AutoDecRef shibo(PyImport_ImportModule("shiboken6.Shiboken"));
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

void init_enum()
{
    static bool is_initialized = false;
    if (!(is_initialized || enum_unpickler || _init_enum()))
        Py_FatalError("could not load enum pickling helper function");
    Py_AtExit(cleanupEnumTypes);
    is_initialized = true;
}

static PyMethodDef SbkEnumObject_Methods[] = {
    {"__reduce__", reinterpret_cast<PyCFunction>(enum___reduce__),
        METH_NOARGS, nullptr},
    {nullptr, nullptr, 0, nullptr} // Sentinel
};

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

bool check(PyObject *pyObj)
{
    return Py_TYPE(Py_TYPE(pyObj)) == SbkEnumType_TypeF();
}

PyObject *getEnumItemFromValue(PyTypeObject *enumType, long itemValue)
{
    PyObject *key, *value;
    Py_ssize_t pos = 0;
    PyObject *values = PyDict_GetItem(enumType->tp_dict, Shiboken::PyName::values());

    while (PyDict_Next(values, &pos, &key, &value)) {
        auto *obj = reinterpret_cast<SbkEnumObject *>(value);
        if (obj->ob_value == itemValue) {
            Py_INCREF(value);
            return value;
        }
    }
    return nullptr;
}

static PyTypeObject *createEnum(const char *fullName, const char *cppName,
                                PyTypeObject *flagsType)
{
    PyTypeObject *enumType = newTypeWithName(fullName, cppName, flagsType);
    if (PyType_Ready(enumType) < 0) {
        Py_XDECREF(enumType);
        return nullptr;
    }
    return enumType;
}

PyTypeObject *createGlobalEnum(PyObject *module, const char *name, const char *fullName, const char *cppName, PyTypeObject *flagsType)
{
    PyTypeObject *enumType = createEnum(fullName, cppName, flagsType);
    if (enumType && PyModule_AddObject(module, name, reinterpret_cast<PyObject *>(enumType)) < 0) {
        Py_DECREF(enumType);
        return nullptr;
    }
    if (flagsType && PyModule_AddObject(module, PepType_GetNameStr(flagsType),
            reinterpret_cast<PyObject *>(flagsType)) < 0) {
        Py_DECREF(enumType);
        return nullptr;
    }
    return enumType;
}

PyTypeObject *createScopedEnum(PyTypeObject *scope, const char *name, const char *fullName, const char *cppName, PyTypeObject *flagsType)
{
    PyTypeObject *enumType = createEnum(fullName, cppName, flagsType);
    if (enumType && PyDict_SetItemString(scope->tp_dict, name,
            reinterpret_cast<PyObject *>(enumType)) < 0) {
        Py_DECREF(enumType);
        return nullptr;
    }
    if (flagsType && PyDict_SetItemString(scope->tp_dict,
            PepType_GetNameStr(flagsType),
            reinterpret_cast<PyObject *>(flagsType)) < 0) {
        Py_DECREF(enumType);
        return nullptr;
    }
    return enumType;
}

static PyObject *createEnumItem(PyTypeObject *enumType, const char *itemName, long itemValue)
{
    PyObject *enumItem = newItem(enumType, itemValue, itemName);
    if (PyDict_SetItemString(enumType->tp_dict, itemName, enumItem) < 0) {
        Py_DECREF(enumItem);
        return nullptr;
    }
    return enumItem;
}

bool createGlobalEnumItem(PyTypeObject *enumType, PyObject *module, const char *itemName, long itemValue)
{
    PyObject *enumItem = createEnumItem(enumType, itemName, itemValue);
    if (!enumItem)
        return false;
    int ok = PyModule_AddObject(module, itemName, enumItem);
    Py_DECREF(enumItem);
    return ok >= 0;
}

bool createScopedEnumItem(PyTypeObject *enumType, PyTypeObject *scope,
                          const char *itemName, long itemValue)
{
    PyObject *enumItem = createEnumItem(enumType, itemName, itemValue);
    if (!enumItem)
        return false;
    int ok = PyDict_SetItemString(scope->tp_dict, itemName, enumItem);
    Py_DECREF(enumItem);
    return ok >= 0;
}

PyObject *
newItem(PyTypeObject *enumType, long itemValue, const char *itemName)
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
        PyObject *values = PyDict_GetItemWithError(dict, Shiboken::PyName::values());
        if (values == nullptr) {
            if (PyErr_Occurred())
                return nullptr;
            Shiboken::AutoDecRef new_values(values = PyDict_New());
            if (values == nullptr)
                return nullptr;
            if (PyDict_SetItem(dict, Shiboken::PyName::values(), values) < 0)
                return nullptr;
        }
        PyDict_SetItemString(values, itemName, reinterpret_cast<PyObject *>(enumObj));
    }

    return reinterpret_cast<PyObject *>(enumObj);
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
    static auto type = SbkType_FromSpec(&SbkNewEnum_spec);
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

PyTypeObject *
newTypeWithName(const char *name,
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
    Shiboken::AutoDecRef bases(PyTuple_New(1));
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

const char *getCppName(PyTypeObject *enumType)
{
    assert(Py_TYPE(enumType) == SbkEnumType_TypeF());
    auto *type = reinterpret_cast<SbkEnumType *>(enumType);
    auto *setp = PepType_SETP(type);
    return setp->cppName;
}

long int getValue(PyObject *enumItem)
{
    assert(Shiboken::Enum::check(enumItem));
    return reinterpret_cast<SbkEnumObject *>(enumItem)->ob_value;
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
    for (const auto &e : m_enumTypes) {
        std::free(e.name);
        Py_DECREF(e.type);
    }
    m_enumTypes.clear();
}

} // namespace Shiboken

static void cleanupEnumTypes()
{
    Shiboken::DeclaredEnumTypes::instance().cleanup();
}

