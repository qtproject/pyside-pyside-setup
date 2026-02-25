// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

// @snippet module-helpers
static bool Check2TupleOfNumbers(PyObject *pyIn)
{
    if (PySequence_Check(pyIn) == 0 || PySequence_Size(pyIn) != 2)
        return false;
    Shiboken::AutoDecRef pyReal(PySequence_GetItem(pyIn, 0));
    Shiboken::AutoDecRef pyImag(PySequence_GetItem(pyIn, 1));
    return PyNumber_Check(pyReal) != 0 && PyNumber_Check(pyImag) != 0;
}

static bool checkPyCapsuleOrPyCObject(PyObject *pyObj)
{
    return PyCapsule_CheckExact(pyObj) != 0;
}

static PyObject* __convertCppValuesToPython(const char **typeNames, void **values, Py_ssize_t size)
{
    PyObject* result = PyTuple_New(size);
    for (Py_ssize_t i = 0; i < size; ++i) {
        Shiboken::Conversions::SpecificConverter converter(typeNames[i]);
        PyTuple_SetItem(result, i, converter.toPython(values[i]));
    }
    return result;
}
// @snippet module-helpers

// @snippet getConversionTypeString
Shiboken::Conversions::SpecificConverter converter(%1);
const char *%0 = nullptr;
switch (converter.conversionType()) {
case Shiboken::Conversions::SpecificConverter::CopyConversion:
    %0 = "Copy conversion";
    break;
case Shiboken::Conversions::SpecificConverter::PointerConversion:
    %0 = "Pointer conversion";
    break;
case Shiboken::Conversions::SpecificConverter::ReferenceConversion:
    %0 = "Reference conversion";
    break;
default:
    %0 = "Invalid conversion";
    break;
}
%PYARG_0 = %CONVERTTOPYTHON[const char*](%0);
// @snippet getConversionTypeString

// @snippet convertValueTypeToCppAndThenToPython
const char *typeNames[] = { "Point", "Point*", "Point&" };
void *values[] = { &%1, &%2, &(%3) };
%PYARG_0 = __convertCppValuesToPython(typeNames, values, 3);
// @snippet convertValueTypeToCppAndThenToPython

// @snippet convertValueTypeToCppAndThenToPython
const char *typeNames[] = { "Point", "Point*", "Point&" };
void *values[] = { &%1, &%2, &%3 };
%PYARG_0 = __convertCppValuesToPython(typeNames, values, 3);
// @snippet convertValueTypeToCppAndThenToPython

// @snippet convertObjectTypeToCppAndThenToPython
const char *typeNames[] = { "ObjectType*", "ObjectType&" };
void *values[] = { &%1, &%2 };
%PYARG_0 = __convertCppValuesToPython(typeNames, values, 2);
// @snippet convertObjectTypeToCppAndThenToPython

// @snippet convertListOfIntegersToCppAndThenToPython
const char *typeNames[] = { "std::list<int>" };
void *values[] = { &%1 };
%PYARG_0 = __convertCppValuesToPython(typeNames, values, 1);
// @snippet convertListOfIntegersToCppAndThenToPython

// @snippet convertIntegersToCppAndThenToPython
const char *typeNames[] = { "int", "int" };
void *values[] = { &%1, &%2 };
%PYARG_0 = __convertCppValuesToPython(typeNames, values, 2);
// @snippet convertIntegersToCppAndThenToPython

// @snippet intwrapper_add_ints
extern "C" {
static PyObject *Sbk_IntWrapper_add_ints(PyObject * /* self */, PyObject *args)
{
    PyObject *result = nullptr;
    if (PyTuple_Check(args) != 0 && PyTuple_Size(args) == 2) {
        PyObject *arg1 = PyTuple_GetItem(args, 0);
        PyObject *arg2 = PyTuple_GetItem(args, 1);
        if (PyLong_Check(arg1) != 0 && PyLong_Check(arg2) != 0)
            result = PyLong_FromLong(PyLong_AsLong(arg1) + PyLong_AsLong(arg2));
    }
    if (result == nullptr)
        PyErr_SetString(PyExc_TypeError, "expecting 2 ints");
    return result;
}
}
// @snippet intwrapper_add_ints

// @snippet stdcomplex_floor
%PYARG_0 = PyFloat_FromDouble(std::floor(%CPPSELF.abs_value()));
// @snippet stdcomplex_floor

// @snippet stdcomplex_ceil
%PYARG_0 = PyFloat_FromDouble(std::ceil(%CPPSELF.abs_value()));
// @snippet stdcomplex_ceil

// @snippet stdcomplex_abs
%PYARG_0 = PyFloat_FromDouble(%CPPSELF.abs_value());
// @snippet stdcomplex_abs

// @snippet stdcomplex_pow
%RETURN_TYPE %0 = %CPPSELF.pow(%1);
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet stdcomplex_pow

// @snippet size_char_ct
// Convert a string "{width}x{height}" specification
{
    double width = -1;
    double height = -1;
    const std::string s = %1;
    const auto pos = s.find('x');
    if (pos != std::string::npos) {
        std::istringstream wstr(s.substr(0, pos));
        wstr >> width;
        std::istringstream hstr(s.substr(pos + 1, s.size() - pos - 1));
        hstr >> height;
    }
    %0 = new %TYPE(width, height);
}
// @snippet size_char_ct

// @snippet nonConversionRuleForArgumentWithDefaultValue
ObjectType *tmpObject = nullptr;
%BEGIN_ALLOW_THREADS
%RETURN_TYPE %0 = %CPPSELF.%FUNCTION_NAME(&tmpObject);
%END_ALLOW_THREADS
%PYARG_0 = PyTuple_New(2);
PyTuple_SetItem(%PYARG_0, 0, %CONVERTTOPYTHON[%RETURN_TYPE](%0));
PyTuple_SetItem(%PYARG_0, 1, %CONVERTTOPYTHON[ObjectType*](tmpObject));
// @snippet nonConversionRuleForArgumentWithDefaultValue

// @snippet reparent-layout-items
static void reparent_layout_items(PyObject *parent, PyObject *layout)
{
    // CHECKTYPE and ISCONVERTIBLE are used here for test purposes, don't change them.
    if (!%CHECKTYPE[ObjectTypeLayout*](layout) && !%ISCONVERTIBLE[ObjectTypeLayout*](layout))
        return;
    /* %CHECKTYPE[ObjectTypeLayout*](layout) */
    /* %ISCONVERTIBLE[ObjectTypeLayout*](layout) */
    ObjectTypeLayout *var;
    var = %CONVERTTOCPP[ObjectTypeLayout*](layout);
    // TODO-CONVERTER: erase this
    // ObjectTypeLayout* var2 = %CONVERTTOCPP[ObjectTypeLayout*](layout);
    const ObjectTypeList &objChildren = var->objects();
    for (auto *child : objChildren) {
        if (child->isLayoutType()) {
            auto *childLayout = reinterpret_cast<ObjectTypeLayout*>(child);
            reparent_layout_items(parent, %CONVERTTOPYTHON[ObjectTypeLayout*](childLayout));
            Shiboken::Object::setParent(layout, %CONVERTTOPYTHON[ObjectTypeLayout*](childLayout));
        } else {
            Shiboken::Object::setParent(parent, %CONVERTTOPYTHON[ObjectType*](child));
        }
    }
}
// @snippet reparent-layout-items

// @snippet fix-margins-parameters
int a0, a1, a2, a3;
%BEGIN_ALLOW_THREADS
%CPPSELF->::%TYPE::%FUNCTION_NAME(&a0, &a1, &a2, &a3);
%END_ALLOW_THREADS
%PYARG_0 = PyTuple_New(4);
PyTuple_SetItem(%PYARG_0, 0, %CONVERTTOPYTHON[int](a0));
PyTuple_SetItem(%PYARG_0, 1, %CONVERTTOPYTHON[int](a1));
PyTuple_SetItem(%PYARG_0, 2, %CONVERTTOPYTHON[int](a2));
PyTuple_SetItem(%PYARG_0, 3, %CONVERTTOPYTHON[int](a3));
// @snippet fix-margins-parameters

// @snippet fix-margins-return
PyObject *obj = %PYARG_0.object();
bool ok = false;
if (PySequence_Check(obj) != 0 && PySequence_Size(obj) == 4) {
    Shiboken::AutoDecRef m0(PySequence_GetItem(obj, 0));
    Shiboken::AutoDecRef m1(PySequence_GetItem(obj, 1));
    Shiboken::AutoDecRef m2(PySequence_GetItem(obj, 2));
    Shiboken::AutoDecRef m3(PySequence_GetItem(obj, 3));
    ok = PyNumber_Check(m0) != 0 && PyNumber_Check(m1) != 0
         && PyNumber_Check(m2) && PyNumber_Check(m3) != 0;
    if (ok) {
        *%1 = %CONVERTTOCPP[int](m0);
        *%2 = %CONVERTTOCPP[int](m1);
        *%3 = %CONVERTTOCPP[int](m2);
        *%4 = %CONVERTTOCPP[int](m3);
    }
}
if (!ok) {
    PyErr_SetString(PyExc_TypeError, "Sequence of 4 numbers expected");
    %1 = %2 = %3 = %4 = 0;
}
// @snippet fix-margins-return

// @snippet sumArrayAndLength
bool ok = false;
if (PySequence_Check(%PYARG_1) != 0) {
    if (int *array = Shiboken::sequenceToIntArray(%PYARG_1, true)) {
        ok = PyErr_Occurred() == nullptr;
        if (ok) {
            %RETURN_TYPE %0 = %CPPSELF.%FUNCTION_NAME(array);
            %PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
        }
        delete [] array;
    }
}
if (!ok)
    PyErr_SetString(PyExc_TypeError, "Should be a sequence of ints");
// @snippet sumArrayAndLength

// @snippet callArrayMethod
const Py_ssize_t numItems = PySequence_Size(%PYARG_1);
Shiboken::ArrayPointer<int> cppItems(numItems);
for (Py_ssize_t i = 0; i < numItems; i++) {
    Shiboken::AutoDecRef _obj(PySequence_GetItem(%PYARG_1, i));
    cppItems[i] = %CONVERTTOCPP[int](_obj);
}
%RETURN_TYPE %0 = %CPPSELF.%FUNCTION_NAME(numItems, cppItems);
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet callArrayMethod

// @snippet applyHomogeneousTransform
bool ok{};
%RETURN_TYPE retval = %FUNCTION_NAME(%1, %2, %3, %4, %5, %6, %7, %8, %9, %10, &ok);
if (ok)
    %PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](retval);
else
    %PYARG_0 = Py_None;
// @snippet applyHomogeneousTransform

// @snippet test-argc-argv
int argc;
char **argv;
if (!Shiboken::listToArgcArgv(%PYARG_1, &argc, &argv)) {
    PyErr_SetString(PyExc_TypeError, "error");
    return 0;
}
%RETURN_TYPE %0 = %CPPSELF.%FUNCTION_NAME(argc, argv);
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
Shiboken::deleteArgv(argc, argv);
// @snippet test-argc-argv

// @snippet sum2d
using Inner = std::list<int>;

int result = 0;
for (const Inner &inner : %1)
    result += std::accumulate(inner.cbegin(), inner.cend(), 0);

%PYARG_0 = %CONVERTTOPYTHON[int](result);
// @snippet sum2d

// @snippet sumproduct
using Pair = std::pair<int, int>;

int result = 0;
for (const Pair &p : %1)
    result += p.first * p.second;
%PYARG_0 = %CONVERTTOPYTHON[int](result);
// @snippet sumproduct

// @snippet time-comparison
static bool compareTime(const Time &t, PyObject *rhs, bool defaultValue)
{
    if (!PyDateTimeAPI)
        PyDateTime_IMPORT;
    if (PyTime_Check(rhs) == 0)
        return defaultValue;
    const int pyH = PyDateTime_TIME_GET_HOUR(rhs);
    const int pyM = PyDateTime_TIME_GET_MINUTE(rhs);
    const int pyS = PyDateTime_TIME_GET_SECOND(rhs);
    return pyH == t.hour() && pyM == t.minute() && pyS == t.second();
}
// @snippet time-comparison

// @snippet point-str
const int x1 = int(%CPPSELF.x());
const int x2 = int((%CPPSELF.x() * 100) - (x1 * 100));
const int y1 = int(%CPPSELF.y());
const int y2 = int((%CPPSELF.y() * 100) - (y1 * 100));
%PYARG_0 = Shiboken::String::fromFormat("%TYPE(%d.%d, %d.%d)", x1, x2, y1, y2);
// @snippet point-str

// @snippet point-repr
const int x1 = int(%CPPSELF.x());
const int x2 = int((%CPPSELF.x() * 10) - (x1 * 10));
const int y1 = int(%CPPSELF.y());
const int y2 = int((%CPPSELF.y() * 10) - (y1 * 10));
%PYARG_0 = Shiboken::String::fromFormat("<%TYPE object at %p: (%d.%d, %d.%d)>",
                                         %CPPSELF, x1, x2, y1, y2);
// @snippet point-repr

// @snippet point-reduce
PyObject *type = PyObject_Type(%PYSELF);
PyObject *args = Py_BuildValue("(dd)", %CPPSELF.x(), %CPPSELF.y());
%PYARG_0 = Py_BuildValue("(OO)", type, args);
// @snippet point-reduce

// @snippet polygon-contains
auto needle = %CONVERTTOCPP[Point](_value);
return %CPPSELF.contains(needle) ? 1 : 0;
// @snippet polygon-contains
