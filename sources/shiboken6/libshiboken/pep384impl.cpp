// Copyright (C) 2018 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include "sbkpython.h"
#include "autodecref.h"
#include "sbkstaticstrings.h"
#include "sbkstaticstrings_p.h"
#include "basewrapper.h"
#include "basewrapper_p.h"
#include "sbkenum.h"
#include "sbkenum_p.h"
#include "sbkconverter.h"
#include "voidptr.h"

#include <cstdlib>
#include <cstring>

extern "C"
{

/*
 * The documentation is located in `sources/pyside6/doc/developer/limited_api.rst`.

 * Here is the verification code for PyTypeObject.
 * We create a type object and check if its fields
 * appear at the right offsets.
 */
#ifdef Py_LIMITED_API

#define make_dummy_int(x)   (x * sizeof(void *))
#define make_dummy(x)       (reinterpret_cast<void *>(make_dummy_int(x)))

static PyObject *
dummy_func(PyObject * /* self */, PyObject * /* args */)
{
    Py_RETURN_NONE;
}

static struct PyMethodDef probe_methoddef[] = {
    {"dummy", dummy_func, METH_NOARGS, nullptr},
    {nullptr, nullptr, 0, nullptr}
};

static PyGetSetDef probe_getseters[] = {
    {nullptr, nullptr, nullptr, nullptr, nullptr}  /* Sentinel */
};

static PyMemberDef probe_members[] = {
    {nullptr, 0, 0, 0, nullptr}  /* Sentinel */
};

#define probe_tp_dealloc    make_dummy(1)
#define probe_tp_repr       make_dummy(2)
#define probe_tp_call       make_dummy(3)
#define probe_tp_getattro   make_dummy(16)
#define probe_tp_setattro   make_dummy(17)
#define probe_tp_str        make_dummy(4)
#define probe_tp_traverse   make_dummy(5)
#define probe_tp_clear      make_dummy(6)
#define probe_tp_iternext   make_dummy(7)
#define probe_tp_methods    probe_methoddef
#define probe_tp_members    probe_members
#define probe_tp_getset     probe_getseters
#define probe_tp_descr_get  make_dummy(10)
#define probe_tp_descr_set  make_dummy(18)
#define probe_tp_init       make_dummy(11)
#define probe_tp_alloc      make_dummy(12)
#define probe_tp_new        make_dummy(13)
#define probe_tp_free       make_dummy(14)
#define probe_tp_is_gc      make_dummy(15)

#define probe_tp_name       "type.probe"
#define probe_tp_basicsize  make_dummy_int(42)

static PyType_Slot typeprobe_slots[] = {
    {Py_tp_dealloc,     probe_tp_dealloc},
    {Py_tp_repr,        probe_tp_repr},
    {Py_tp_call,        probe_tp_call},
    {Py_tp_getattro,    probe_tp_getattro},
    {Py_tp_setattro,    probe_tp_setattro},
    {Py_tp_str,         probe_tp_str},
    {Py_tp_traverse,    probe_tp_traverse},
    {Py_tp_clear,       probe_tp_clear},
    {Py_tp_iternext,    probe_tp_iternext},
    {Py_tp_methods,     probe_tp_methods},
    {Py_tp_members,     probe_tp_members},
    {Py_tp_getset,      probe_tp_getset},
    {Py_tp_descr_get,   probe_tp_descr_get},
    {Py_tp_descr_set,   probe_tp_descr_set},
    {Py_tp_init,        probe_tp_init},
    {Py_tp_alloc,       probe_tp_alloc},
    {Py_tp_new,         probe_tp_new},
    {Py_tp_free,        probe_tp_free},
    {Py_tp_is_gc,       probe_tp_is_gc},
    {0, nullptr}
};
static PyType_Spec typeprobe_spec = {
    probe_tp_name,
    probe_tp_basicsize,
    0,
    Py_TPFLAGS_DEFAULT,
    typeprobe_slots,
};

static void
check_PyTypeObject_valid()
{
    auto *obtype = reinterpret_cast<PyObject *>(&PyType_Type);
    auto *probe_tp_base = reinterpret_cast<PyTypeObject *>(
        PyObject_GetAttr(obtype, Shiboken::PyMagicName::base()));
    auto *probe_tp_bases = PyObject_GetAttr(obtype, Shiboken::PyMagicName::bases());
    auto *check = reinterpret_cast<PyTypeObject *>(
        PyType_FromSpecWithBases(&typeprobe_spec, probe_tp_bases));
    auto *typetype = reinterpret_cast<PyTypeObject *>(obtype);
    PyObject *w = PyObject_GetAttr(obtype, Shiboken::PyMagicName::weakrefoffset());
    long probe_tp_weakrefoffset = PyLong_AsLong(w);
    PyObject *d = PyObject_GetAttr(obtype, Shiboken::PyMagicName::dictoffset());
    long probe_tp_dictoffset = PyLong_AsLong(d);
    PyObject *probe_tp_mro = PyObject_GetAttr(obtype, Shiboken::PyMagicName::mro());
    if (false
        || strcmp(probe_tp_name, check->tp_name) != 0
        || probe_tp_basicsize       != check->tp_basicsize
        || probe_tp_dealloc         != check->tp_dealloc
        || probe_tp_repr            != check->tp_repr
        || probe_tp_call            != check->tp_call
        || probe_tp_getattro        != check->tp_getattro
        || probe_tp_setattro        != check->tp_setattro
        || probe_tp_str             != check->tp_str
        || probe_tp_traverse        != check->tp_traverse
        || probe_tp_clear           != check->tp_clear
        || probe_tp_weakrefoffset   != typetype->tp_weaklistoffset
        || probe_tp_iternext        != check->tp_iternext
        || probe_tp_methods         != check->tp_methods
        || probe_tp_getset          != check->tp_getset
        || probe_tp_base            != typetype->tp_base
        || !PyDict_Check(check->tp_dict)
        || !PyDict_GetItemString(check->tp_dict, "dummy")
        || probe_tp_descr_get       != check->tp_descr_get
        || probe_tp_descr_set       != check->tp_descr_set
        || probe_tp_dictoffset      != typetype->tp_dictoffset
        || probe_tp_init            != check->tp_init
        || probe_tp_alloc           != check->tp_alloc
        || probe_tp_new             != check->tp_new
        || probe_tp_free            != check->tp_free
        || probe_tp_is_gc           != check->tp_is_gc
        || probe_tp_bases           != typetype->tp_bases
        || probe_tp_mro             != typetype->tp_mro
        || Py_TPFLAGS_DEFAULT       != (check->tp_flags & Py_TPFLAGS_DEFAULT))
        Py_FatalError("The structure of type objects has changed!");
    Py_DECREF(check);
    Py_DECREF(probe_tp_base);
    Py_DECREF(w);
    Py_DECREF(d);
    Py_DECREF(probe_tp_bases);
    Py_DECREF(probe_tp_mro);
}

// PYSIDE-1797: This must be a runtime decision.
#include "pep384_issue33738.cpp"

#endif // Py_LIMITED_API

/*****************************************************************************
 *
 * Additional for object.h / class properties
 *
 */
#ifdef Py_LIMITED_API
/*
 * This implementation of `_PyType_Lookup` works for lookup in our classes.
 * The implementation ignores all caching and versioning and is also
 * less optimized. This is reduced from the Python implementation.
 */

/* Internal API to look for a name through the MRO, bypassing the method cache.
   This returns a borrowed reference, and might set an exception.
   'error' is set to: -1: error with exception; 1: error without exception; 0: ok */
static PyObject *
find_name_in_mro(PyTypeObject *type, PyObject *name, int *error)
{
    Py_ssize_t i, n;
    PyObject *mro, *res, *base, *dict;

    /* Look in tp_dict of types in MRO */
    mro = type->tp_mro;

    res = nullptr;
    /* Keep a strong reference to mro because type->tp_mro can be replaced
       during dict lookup, e.g. when comparing to non-string keys. */
    Py_INCREF(mro);
    assert(PyTuple_Check(mro));
    n = PyTuple_GET_SIZE(mro);
    for (i = 0; i < n; i++) {
        base = PyTuple_GET_ITEM(mro, i);
        assert(PyType_Check(base));
        dict = ((PyTypeObject *)base)->tp_dict;
        assert(dict && PyDict_Check(dict));
        res = PyDict_GetItem(dict, name);
        if (res != nullptr)
            break;
        if (PyErr_Occurred()) {
            *error = -1;
            goto done;
        }
    }
    *error = 0;
done:
    Py_DECREF(mro);
    return res;
}

/* Internal API to look for a name through the MRO.
   This returns a borrowed reference, and doesn't set an exception! */
PyObject *
_PepType_Lookup(PyTypeObject *type, PyObject *name)
{
    PyObject *res;
    int error;

    /* We may end up clearing live exceptions below, so make sure it's ours. */
    assert(!PyErr_Occurred());

    res = find_name_in_mro(type, name, &error);
    /* Only put NULL results into cache if there was no error. */
    if (error) {
        /* It's not ideal to clear the error condition,
           but this function is documented as not setting
           an exception, and I don't want to change that.
           E.g., when PyType_Ready() can't proceed, it won't
           set the "ready" flag, so future attempts to ready
           the same type will call it again -- hopefully
           in a context that propagates the exception out.
        */
        if (error == -1) {
            PyErr_Clear();
        }
        return nullptr;
    }
    return res;
}

#endif // Py_LIMITED_API

/*****************************************************************************
 *
 * Support for unicodeobject.h
 *
 */
#ifdef Py_LIMITED_API

// structs and macros modelled after their equivalents in
// cpython/Include/cpython/unicodeobject.h

struct PepASCIIObject
{
    PyObject_HEAD
    Py_ssize_t length;          /* Number of code points in the string */
    Py_hash_t hash;             /* Hash value; -1 if not set */
    struct {
        unsigned int interned:2;
        unsigned int kind:3;
        unsigned int compact:1;
        unsigned int ascii:1;
        unsigned int ready:1;
        unsigned int :24;
    } state;
    wchar_t *wstr;              /* wchar_t representation (null-terminated) */
};

struct PepCompactUnicodeObject
{
    PepASCIIObject _base;
    Py_ssize_t utf8_length;
    char *utf8;                 /* UTF-8 representation (null-terminated) */
    Py_ssize_t wstr_length;     /* Number of code points in wstr */
};

struct PepUnicodeObject
{
    PepCompactUnicodeObject _base;
    union {
        void *any;
        Py_UCS1 *latin1;
        Py_UCS2 *ucs2;
        Py_UCS4 *ucs4;
    } data;                     /* Canonical, smallest-form Unicode buffer */
};

int _PepUnicode_KIND(PyObject *str)
{
    return reinterpret_cast<PepASCIIObject *>(str)->state.kind;
}

int _PepUnicode_IS_ASCII(PyObject *str)
{
    auto *asciiObj = reinterpret_cast<PepASCIIObject *>(str);
    return asciiObj->state.ascii;
}

int _PepUnicode_IS_COMPACT(PyObject *str)
{
    auto *asciiObj = reinterpret_cast<PepASCIIObject *>(str);
    return asciiObj->state.compact;
}

static void *_PepUnicode_COMPACT_DATA(PyObject *str)
{
    auto *asciiObj = reinterpret_cast<PepASCIIObject *>(str);
    if (asciiObj->state.ascii)
        return asciiObj + 1;
    auto *compactObj = reinterpret_cast<PepCompactUnicodeObject *>(str);
    return compactObj + 1;
}

static void *_PepUnicode_NONCOMPACT_DATA(PyObject *str)
{
    return reinterpret_cast<PepUnicodeObject *>(str)->data.any;
}

void *_PepUnicode_DATA(PyObject *str)
{
    return _PepUnicode_IS_COMPACT(str)
           ? _PepUnicode_COMPACT_DATA(str) : _PepUnicode_NONCOMPACT_DATA(str);
}

// Fast path accessing UTF8 data without doing a conversion similar
// to _PyUnicode_AsUTF8String
static const char *utf8FastPath(PyObject *str)
{
    if (PyUnicode_GetLength(str) == 0)
        return "";
    auto *asciiObj = reinterpret_cast<PepASCIIObject *>(str);
    if (asciiObj->state.kind != PepUnicode_1BYTE_KIND || asciiObj->state.compact == 0)
        return nullptr; // Empirical: PyCompactUnicodeObject.utf8 is only valid for 1 byte
    if (asciiObj->state.ascii) {
        auto *data = asciiObj + 1;
        return reinterpret_cast<const char *>(data);
    }
    auto *compactObj = reinterpret_cast<PepCompactUnicodeObject *>(str);
    if (compactObj->utf8_length)
        return compactObj->utf8;
    return nullptr;
}

const char *_PepUnicode_AsString(PyObject *str)
{
    /*
     * This function is the surrogate for PyUnicode_AsUTF8, which keeps the data
     * in the unicode object as long as that object exists.
     *
     * The function does too much if not optimized by utf8, because it keeps the
     * string alive, unconditionally.
     * We should not rely on this behavior and think of PyUnicode_AsUTF8, only.
     */
#define STRINGIFY(x) #x
#define TOSTRING(x) STRINGIFY(x)
#define AT __FILE__ ":" TOSTRING(__LINE__)

    if (const auto *utf8 = utf8FastPath(str))
        return utf8;

    static PyObject *cstring_dict = nullptr;
    if (cstring_dict == nullptr) {
        cstring_dict = PyDict_New();
        if (cstring_dict == nullptr)
            Py_FatalError("Error in " AT);
    }
    PyObject *bytesStr = PyUnicode_AsEncodedString(str, "utf8", nullptr);
    PyObject *entry = PyDict_GetItemWithError(cstring_dict, bytesStr);
    if (entry == nullptr) {
        int e = PyDict_SetItem(cstring_dict, bytesStr, bytesStr);
        if (e != 0)
            Py_FatalError("Error in " AT);
        entry = bytesStr;
    }
    else
        Py_DECREF(bytesStr);
    return PyBytes_AsString(entry);
}
#endif // Py_LIMITED_API

/*****************************************************************************
 *
 * Support for pydebug.h
 *
 */
#ifdef Py_LIMITED_API

static PyObject *sys_flags = nullptr;

int
Pep_GetFlag(const char *name)
{
    static int initialized = 0;
    int ret = -1;

    if (!initialized) {
        sys_flags = PySys_GetObject("flags");
        // func gives no error if nullptr is returned and does not incref.
        Py_XINCREF(sys_flags);
        initialized = 1;
    }
    if (sys_flags != nullptr) {
        PyObject *ob_ret = PyObject_GetAttrString(sys_flags, name);
        if (ob_ret != nullptr) {
            long long_ret = PyLong_AsLong(ob_ret);
            Py_DECREF(ob_ret);
            ret = (int) long_ret;
        }
    }
    return ret;
}

int
Pep_GetVerboseFlag()
{
    static int initialized = 0;
    static int verbose_flag = -1;

    if (!initialized) {
        verbose_flag = Pep_GetFlag("verbose");
        if (verbose_flag != -1)
            initialized = 1;
    }
    return verbose_flag;
}
#endif // Py_LIMITED_API

/*****************************************************************************
 *
 * Support for code.h
 *
 */
#ifdef Py_LIMITED_API

int
PepCode_Get(PepCodeObject *co, const char *name)
{
    PyObject *ob = reinterpret_cast<PyObject *>(co);
    PyObject *ob_ret;
    int ret = -1;

    ob_ret = PyObject_GetAttrString(ob, name);
    if (ob_ret != nullptr) {
        long long_ret = PyLong_AsLong(ob_ret);
        Py_DECREF(ob_ret);
        ret = (int) long_ret;
    }
    return ret;
}
#endif // Py_LIMITED_API

/*****************************************************************************
 *
 * Support for datetime.h
 *
 */
#ifdef Py_LIMITED_API

datetime_struc *PyDateTimeAPI = nullptr;

static PyTypeObject *dt_getCheck(const char *name)
{
    PyObject *op = PyObject_GetAttrString(PyDateTimeAPI->module, name);
    if (op == nullptr) {
        fprintf(stderr, "datetime.%s not found\n", name);
        Py_FatalError("aborting");
    }
    return reinterpret_cast<PyTypeObject *>(op);
}

// init_DateTime is called earlier than our module init.
// We use the provided PyDateTime_IMPORT machinery.
datetime_struc *
init_DateTime(void)
{
    static int initialized = 0;
    if (!initialized) {
        PyDateTimeAPI = (datetime_struc *)malloc(sizeof(datetime_struc));
        if (PyDateTimeAPI == nullptr)
            Py_FatalError("PyDateTimeAPI malloc error, aborting");
        PyDateTimeAPI->module = PyImport_ImportModule("datetime");
        if (PyDateTimeAPI->module == nullptr)
            Py_FatalError("datetime module not found, aborting");
        PyDateTimeAPI->DateType     = dt_getCheck("date");
        PyDateTimeAPI->DateTimeType = dt_getCheck("datetime");
        PyDateTimeAPI->TimeType     = dt_getCheck("time");
        PyDateTimeAPI->DeltaType    = dt_getCheck("timedelta");
        PyDateTimeAPI->TZInfoType   = dt_getCheck("tzinfo");
        initialized = 1;
    }
    return PyDateTimeAPI;
}

int
PyDateTime_Get(PyObject *ob, const char *name)
{
    PyObject *ob_ret;
    int ret = -1;

    ob_ret = PyObject_GetAttrString(ob, name);
    if (ob_ret != nullptr) {
        long long_ret = PyLong_AsLong(ob_ret);
        Py_DECREF(ob_ret);
        ret = (int) long_ret;
    }
    return ret;
}

PyObject *
PyDate_FromDate(int year, int month, int day)
{
    return PyObject_CallFunction((PyObject *)PyDateTimeAPI->DateType,
                                 (char *)"(iii)", year, month, day);
}

PyObject *
PyDateTime_FromDateAndTime(int year, int month, int day,
                           int hour, int min, int sec, int usec)
{
    return PyObject_CallFunction((PyObject *)PyDateTimeAPI->DateTimeType,
                                 (char *)"(iiiiiii)", year, month, day,
                                  hour, min, sec, usec);
}

PyObject *
PyTime_FromTime(int hour, int min, int sec, int usec)
{
    return PyObject_CallFunction((PyObject *)PyDateTimeAPI->TimeType,
                                 (char *)"(iiii)", hour, min, sec, usec);
}
#endif // Py_LIMITED_API

/*****************************************************************************
 *
 * Support for pythonrun.h
 *
 */
#ifdef Py_LIMITED_API

// Flags are ignored in these simple helpers.
PyObject *
PyRun_String(const char *str, int start, PyObject *globals, PyObject *locals)
{
    PyObject *code = Py_CompileString(str, "pyscript", start);
    PyObject *ret = nullptr;

    if (code != nullptr) {
        ret = PyEval_EvalCode(code, globals, locals);
    }
    Py_XDECREF(code);
    return ret;
}

#endif // Py_LIMITED_API

/*****************************************************************************
 *
 * Support for classobject.h
 *
 */
#ifdef Py_LIMITED_API

PyTypeObject *PepMethod_TypePtr = nullptr;

static PyTypeObject *getMethodType(void)
{
    static const char prog[] =
        "class _C:\n"
        "    def _m(self): pass\n"
        "result = type(_C()._m)\n";
    return reinterpret_cast<PyTypeObject *>(PepRun_GetResult(prog));
}

// We have no access to PyMethod_New and must call types.MethodType, instead.
PyObject *
PyMethod_New(PyObject *func, PyObject *self)
{
    return PyObject_CallFunction((PyObject *)PepMethod_TypePtr,
                                 (char *)"(OO)", func, self);
}

PyObject *
PyMethod_Function(PyObject *im)
{
    PyObject *ret = PyObject_GetAttr(im, Shiboken::PyMagicName::func());

    // We have to return a borrowed reference.
    Py_DECREF(ret);
    return ret;
}

PyObject *
PyMethod_Self(PyObject *im)
{
    PyObject *ret = PyObject_GetAttr(im, Shiboken::PyMagicName::self());

    // We have to return a borrowed reference.
    // If we don't obey that here, then we get a test error!
    Py_DECREF(ret);
    return ret;
}
#endif // Py_LIMITED_API

/*****************************************************************************
 *
 * Support for funcobject.h
 *
 */
#ifdef Py_LIMITED_API

PyObject *
PepFunction_Get(PyObject *ob, const char *name)
{
    PyObject *ret;

    // We have to return a borrowed reference.
    ret = PyObject_GetAttrString(ob, name);
    Py_XDECREF(ret);
    return ret;
}

// This became necessary after Windows was activated.

PyTypeObject *PepFunction_TypePtr = nullptr;

static PyTypeObject *getFunctionType(void)
{
    static const char prog[] =
        "from types import FunctionType as result\n";
    return reinterpret_cast<PyTypeObject *>(PepRun_GetResult(prog));
}
#endif // Py_LIMITED_API || Python 2

/*****************************************************************************
 *
 * Support for dictobject.h
 *
 */

/*****************************************************************************
 *
 * Extra support for signature.cpp
 *
 */
#ifdef Py_LIMITED_API

PyTypeObject *PepStaticMethod_TypePtr = nullptr;

static PyTypeObject *
getStaticMethodType(void)
{
    // this works for Python 3, only
    //    "StaticMethodType = type(str.__dict__['maketrans'])\n";
    static const char prog[] =
        "from xxsubtype import spamlist\n"
        "result = type(spamlist.__dict__['staticmeth'])\n";
    return reinterpret_cast<PyTypeObject *>(PepRun_GetResult(prog));
}

typedef struct {
    PyObject_HEAD
    PyObject *sm_callable;
    PyObject *sm_dict;
} staticmethod;

PyObject *
PyStaticMethod_New(PyObject *callable)
{
    staticmethod *sm = (staticmethod *)
        PyType_GenericAlloc(PepStaticMethod_TypePtr, 0);
    if (sm != nullptr) {
        Py_INCREF(callable);
        sm->sm_callable = callable;
    }
    return reinterpret_cast<PyObject *>(sm);
}
#endif // Py_LIMITED_API

#ifdef PYPY_VERSION
PyTypeObject *PepBuiltinMethod_TypePtr = nullptr;

static PyTypeObject *
getBuiltinMethodType(void)
{
    // PYSIDE-535: PyPy has a special builtin method that acts almost like PyCFunction.
    //
    // There is no public declaration for the "builtin method" type.
    // We also cannot grep it with a Python script since the import is too early.
    // Pick a demo "builtin method" by using the VoidPtr type.
    // Create the equivalent of
    // "from shiboken6.Shiboken import VoidPtr\n"
    // "result = type(VoidPtr(0).toBytes)\n";
    auto *pyVoidP = reinterpret_cast<PyObject *>(SbkVoidPtr_TypeF());
    Shiboken::AutoDecRef arg(Py_BuildValue("i", 0));
    Shiboken::AutoDecRef inst(PyObject_CallFunctionObjArgs(pyVoidP, arg.object(), nullptr));
    Shiboken::AutoDecRef meth(PyObject_GetAttrString(inst, "toBytes"));
    auto *result = reinterpret_cast<PyTypeObject *>(PyObject_Type(meth));
    return result;
}
#endif

/*****************************************************************************
 *
 * Common newly needed functions
 *
 */

// The introduction of heaptypes converted many type names to the
// dotted form, since PyType_FromSpec uses it to compute the module
// name. This function reverts this effect.
const char *
PepType_GetNameStr(PyTypeObject *type)
{
    const char *ret = type->tp_name;
    const char *nodots = std::strrchr(ret, '.');
    if (nodots)
        ret = nodots + 1;
    return ret;
}

// PYSIDE-2264: Find the _functools or functools module and retrieve the
//              partial function. This can be tampered with, check carefully.
PyObject *
Pep_GetPartialFunction(void)
{
    static bool initialized = false;
    static PyObject *result{};
    if (initialized) {
        Py_INCREF(result);
        return result;
    }
    auto *functools = PyImport_ImportModule("_functools");
    if (!functools) {
        PyErr_Clear();
        functools = PyImport_ImportModule("functools");
    }
    if (!functools)
        Py_FatalError("functools cannot be found");
    result = PyObject_GetAttrString(functools, "partial");
    if (!result || !PyCallable_Check(result))
        Py_FatalError("partial not found or not a function");
    initialized = true;
    return result;
}

/*****************************************************************************
 *
 * Newly introduced convenience functions
 *
 */
#if PY_VERSION_HEX < 0x03070000 || defined(Py_LIMITED_API)

PyObject *
PyImport_GetModule(PyObject *name)
{
    PyObject *m;
    PyObject *modules = PyImport_GetModuleDict();
    if (modules == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "unable to get sys.modules");
        return NULL;
    }
    Py_INCREF(modules);
    if (PyDict_CheckExact(modules)) {
        m = PyDict_GetItemWithError(modules, name);  /* borrowed */
        Py_XINCREF(m);
    }
    else {
        m = PyObject_GetItem(modules, name);
        if (m == NULL && PyErr_ExceptionMatches(PyExc_KeyError)) {
            PyErr_Clear();
        }
    }
    Py_DECREF(modules);
    return m;
}

#endif // PY_VERSION_HEX < 0x03070000 || defined(Py_LIMITED_API)

// 2020-06-16: For simplicity of creating arbitrary things, this function
// is now made public.

PyObject *
PepRun_GetResult(const char *command)
{
    /*
     * Evaluate a string and return the variable `result`
     */
    PyObject *d, *v, *res;

    d = PyDict_New();
    if (d == nullptr
        || PyDict_SetItem(d, Shiboken::PyMagicName::builtins(), PyEval_GetBuiltins()) < 0) {
        return nullptr;
    }
    v = PyRun_String(command, Py_file_input, d, d);
    res = v ? PyDict_GetItem(d, Shiboken::PyName::result()) : nullptr;
    Py_XDECREF(v);
    Py_DECREF(d);
    return res;
}

PyTypeObject *PepType_Type_tp_new(PyTypeObject *metatype, PyObject *args, PyObject *kwds)
{
    auto ret = PyType_Type.tp_new(metatype, args, kwds);
    return reinterpret_cast<PyTypeObject *>(ret);
}

/*****************************************************************************
 *
 * Extra support for name mangling
 *
 */

#ifdef Py_LIMITED_API
// We keep these definitions local, because they don't work in Python 2.
# define PyUnicode_GET_LENGTH(op)    PyUnicode_GetLength((PyObject *)(op))
# define PyUnicode_READ_CHAR(u, i)   PyUnicode_ReadChar((PyObject *)(u), (i))
#endif // Py_LIMITED_API

PyObject *
_Pep_PrivateMangle(PyObject *self, PyObject *name)
{
    /*
     * Name mangling: __private becomes _classname__private.
     * This function is modelled after _Py_Mangle, but is optimized
     * a little for our purpose.
     */
    if (PyUnicode_READ_CHAR(name, 0) != '_' ||
        PyUnicode_READ_CHAR(name, 1) != '_') {
        Py_INCREF(name);
        return name;
    }
    size_t nlen = PyUnicode_GET_LENGTH(name);
    /* Don't mangle __id__ or names with dots. */
    if ((PyUnicode_READ_CHAR(name, nlen-1) == '_' &&
         PyUnicode_READ_CHAR(name, nlen-2) == '_') ||
        PyUnicode_FindChar(name, '.', 0, nlen, 1) != -1) {
        Py_INCREF(name);
        return name;
    }
    Shiboken::AutoDecRef privateobj(PyObject_GetAttr(
        reinterpret_cast<PyObject *>(Py_TYPE(self)), Shiboken::PyMagicName::name()));

    // PYSIDE-1436: _Py_Mangle is no longer exposed; implement it always.
    // The rest of this function is our own implementation of _Py_Mangle.
    // Please compare the original function in compile.c .
    size_t plen = PyUnicode_GET_LENGTH(privateobj.object());
    /* Strip leading underscores from class name */
    size_t ipriv = 0;
    while (PyUnicode_READ_CHAR(privateobj.object(), ipriv) == '_')
        ipriv++;
    if (ipriv == plen) {
        Py_INCREF(name);
        return name; /* Don't mangle if class is just underscores */
    }
    plen -= ipriv;

    if (plen + nlen >= PY_SSIZE_T_MAX - 1) {
        PyErr_SetString(PyExc_OverflowError,
                        "private identifier too large to be mangled");
        return nullptr;
    }
    size_t const amount = ipriv + 1 + plen + nlen;
    size_t const big_stack = 1000;
    wchar_t bigbuf[big_stack];
    wchar_t *resbuf = amount <= big_stack ? bigbuf : (wchar_t *)malloc(sizeof(wchar_t) * amount);
    if (!resbuf)
        return 0;
    /* ident = "_" + priv[ipriv:] + ident # i.e. 1+plen+nlen bytes */
    resbuf[0] = '_';
    if (PyUnicode_AsWideChar(privateobj, resbuf + 1, ipriv + plen) < 0)
        return 0;
    if (PyUnicode_AsWideChar(name, resbuf + ipriv + plen + 1, nlen) < 0)
        return 0;
    PyObject *result = PyUnicode_FromWideChar(resbuf + ipriv, 1 + plen + nlen);
    if (amount > big_stack)
        free(resbuf);
    return result;
}

/*****************************************************************************
 *
 * Runtime support for Python 3.8 incompatibilities
 *
 */

int PepRuntime_38_flag = 0;

static void
init_PepRuntime()
{
    // We expect a string of the form "\d\.\d+\."
    const char *version = Py_GetVersion();
    if (version[0] < '3')
        return;
    if (std::atoi(version + 2) >= 8)
        PepRuntime_38_flag = 1;
}

long _PepRuntimeVersion()
{
    static auto *version = PySys_GetObject("version_info");
    static auto major = PyLong_AsLong(PyTuple_GetItem(version, 0));
    static auto minor = PyLong_AsLong(PyTuple_GetItem(version, 1));
    static auto micro = PyLong_AsLong(PyTuple_GetItem(version, 2));
    static auto number = major << 16 | minor << 8 | micro;
    return number;
}

/*****************************************************************************
 *
 * PYSIDE-535: Support for PyPy
 *
 * This has the nice side effect of a more clean implementation,
 * and we don't keep the old macro version.
 *
 */

/*
 * PyTypeObject extender
 */
static std::unordered_map<PyTypeObject *, SbkObjectTypePrivate > SOTP_extender{};
static thread_local PyTypeObject *SOTP_key{};
static thread_local SbkObjectTypePrivate *SOTP_value{};

SbkObjectTypePrivate *PepType_SOTP(PyTypeObject *sbkType)
{
    if (sbkType == SOTP_key)
        return SOTP_value;
    auto it = SOTP_extender.find(sbkType);
    if (it == SOTP_extender.end()) {
        it = SOTP_extender.insert({sbkType, {}}).first;
        memset(&it->second, 0, sizeof(SbkObjectTypePrivate));
    }
    SOTP_key = sbkType;
    SOTP_value = &it->second;
    return SOTP_value;
}

void PepType_SOTP_delete(PyTypeObject *sbkType)
{
    SOTP_extender.erase(sbkType);
    SOTP_key = nullptr;
}

/*
 * SbkEnumType extender
 */
static std::unordered_map<SbkEnumType *, SbkEnumTypePrivate> SETP_extender{};
static thread_local SbkEnumType *SETP_key{};
static thread_local SbkEnumTypePrivate *SETP_value{};

SbkEnumTypePrivate *PepType_SETP(SbkEnumType *enumType)
{
    if (enumType == SETP_key)
        return SETP_value;
    auto it = SETP_extender.find(enumType);
    if (it == SETP_extender.end()) {
        it = SETP_extender.insert({enumType, {}}).first;
        memset(&it->second, 0, sizeof(SbkEnumTypePrivate));
    }
    SETP_key = enumType;
    SETP_value = &it->second;
    return SETP_value;
}

void PepType_SETP_delete(SbkEnumType *enumType)
{
    SETP_extender.erase(enumType);
    SETP_key = nullptr;
}

/*
 * PySideQFlagsType extender
 */
static std::unordered_map<PySideQFlagsType *, SbkQFlagsTypePrivate> PFTP_extender{};
static thread_local PySideQFlagsType *PFTP_key{};
static thread_local SbkQFlagsTypePrivate *PFTP_value{};

SbkQFlagsTypePrivate *PepType_PFTP(PySideQFlagsType *flagsType)
{
    static PyTypeObject *enumMeta = getPyEnumMeta();
    auto *mappedType = reinterpret_cast<PyTypeObject *>(flagsType);
    auto *metaType = Py_TYPE(mappedType);
    if (metaType == enumMeta) {
        return reinterpret_cast<SbkQFlagsTypePrivate *>(
            PepType_SETP(reinterpret_cast<SbkEnumType *>(flagsType)));
    }
    if (flagsType == PFTP_key)
        return PFTP_value;
    auto it = PFTP_extender.find(flagsType);
    if (it == PFTP_extender.end()) {
        it = PFTP_extender.insert({flagsType, {}}).first;
        memset(&it->second, 0, sizeof(SbkQFlagsTypePrivate));
    }
    PFTP_key = flagsType;
    PFTP_value = &it->second;
    return PFTP_value;
}

void PepType_PFTP_delete(PySideQFlagsType *flagsType)
{
    PFTP_extender.erase(flagsType);
    PFTP_key = nullptr;
}

/***************************************************************************
 *
 * PYSIDE-535: The enum/flag error
 * -------------------------------
 *
 * This is a fragment of the code which was used to find the enum/flag
 * alias error. See the change to `setTypeConverter` in sbkenum.cpp .
 *

Usage:

python3 -c "from PySide6 import QtCore" 2>&1 | python3 tools/debug_renamer.py | uniq -c | head -10

   5 PepType_ExTP:940 x_A SOTP s=96
   4 PepType_ExTP:940 x_B SETP s=24
   2 PepType_ExTP:940 x_C PFTP s=16
   4 PepType_ExTP:940 x_D SETP s=24
   1 PepType_ExTP:940 x_C SETP s=24
   2 PepType_ExTP:940 x_E PFTP s=16
   4 PepType_ExTP:940 x_F SETP s=24
   1 PepType_ExTP:940 x_E SETP s=24
   4 PepType_ExTP:940 x_G SETP s=24
   4 PepType_ExTP:940 x_H SETP s=24

static inline void *PepType_ExTP(PyTypeObject *type, size_t size)
{
    static const char *env_p = std::getenv("PFTP");
    if (env_p) {
        static PyTypeObject *alias{};
        const char *kind = size == sizeof(SbkObjectTypePrivate) ? "SOTP" :
                           size == sizeof(SbkEnumTypePrivate) ? "SETP" :
                           size == sizeof(SbkQFlagsTypePrivate) ? "PFTP" :
                           "unk.";
        fprintf(stderr, "%s:%d %p x %s s=%ld\n", __func__, __LINE__, type, kind, size);
        PyObject *kill{};
        if (strlen(env_p) > 0) {
            if (size == sizeof(SbkQFlagsTypePrivate)) {
                if (alias == nullptr)
                    alias = type;
            }
            if (size != sizeof(SbkQFlagsTypePrivate)) {
                if (type == alias)
                    Py_INCREF(kill);
            }
        }
    }
    const auto ikey = reinterpret_cast<std::uintptr_t>(type);
    if (ikey == cached_key)
        return cached_value;
    auto it = SOTP_extender.find(ikey);
    if (it == SOTP_extender.end()) {
        PepType_ExTP_init(type, size);
        return PepType_ExTP(type, size);
    }
    cached_key = ikey;
    cached_value = reinterpret_cast<void *>(it->second);
    return cached_value;
}
*/

/*****************************************************************************
 *
 * Module Initialization
 *
 */

void
Pep384_Init()
{
    init_PepRuntime();
#ifdef Py_LIMITED_API
    check_PyTypeObject_valid();
    Pep_GetVerboseFlag();
    PepMethod_TypePtr = getMethodType();
    PepFunction_TypePtr = getFunctionType();
    PepStaticMethod_TypePtr = getStaticMethodType();
#endif // Py_LIMITED_API
#ifdef PYPY_VERSION
    PepBuiltinMethod_TypePtr = getBuiltinMethodType();
#endif
}

} // extern "C"
