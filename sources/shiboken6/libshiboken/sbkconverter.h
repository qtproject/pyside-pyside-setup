// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef SBK_CONVERTER_H
#define SBK_CONVERTER_H

#include "sbkpython.h"
#include "sbkmodule.h"
#include "shibokenmacros.h"

#include <cstdint>
#include <string>

namespace Shiboken::Module
{
struct TypeInitStruct;
}

struct SbkObject;

/*!
    This is a convenience function identical to Python's PyObject_TypeCheck(),
    checking whether \a ob is of type \a tp, except that the arguments have
    swapped places, for the great convenience of the generator.
*/
LIBSHIBOKEN_API  bool SbkObject_TypeCheck(PyTypeObject *tp, PyObject *ob);

extern "C"
{

/*!
    SbkConverter is used to perform type conversions from C++
    to Python and vice-versa; and it is also used for type checking.
    SbkConverter is a private structure that must be accessed
    using the functions provided by the converter API.
*/
struct SbkConverter;
struct SbkArrayConverter;

/*!
    Given a void pointer to a C++ object, this function must return
    the proper Python object. It may be either an existing wrapper
    for the C++ object, or a newly created one. Or even the Python
    equivalent of the C++ value passed in the argument.

    C++ -> Python
*/
using CppToPythonFunc = PyObject *(*)(const void *);

/*!
    Same as CppToPythonFunc, but additionally receives the \c{PyTypeObject *}.
    This is handy for some converters, namely enumeration converters or
    dynamic user-defined converters that invoke the type object.
*/
using CppToPythonWithTypeFunc = PyObject *(*)(PyTypeObject *, const void *);

/*!
    This function converts a Python object to a C++ value, it may be
    a pointer, value, class, container or primitive type, passed via
    a void pointer, that will be cast properly inside the function.
    This function is usually returned by an IsConvertibleToCppFunc
    function, or obtained knowing the type of the Python object input,
    thus it will not check the Python object type, and will expect
    the void pointer to be pointing to a proper variable.

    Python -> C++
*/
using PythonToCppFunc = void (*)(PyObject *,void *);

/*!
    Checks if the Python object passed in the argument is convertible to a
    C++ type defined inside the function, it returns the converter function
    that will transform a Python argument into a C++ value.
    It returns nullptr if the Python object is not convertible to the C++ type
    that the function represents.

    Python -> C++ ?
*/
using IsConvertibleToCppFunc = PythonToCppFunc (*)(PyObject *);

} // extern "C"

namespace Shiboken {
namespace Conversions {


class LIBSHIBOKEN_API SpecificConverter
{
public:
    enum Type : uint8_t
    {
        InvalidConversion,
        CopyConversion,
        PointerConversion,
        ReferenceConversion
    };

    explicit SpecificConverter(const char *typeName);

    SbkConverter *converter() const { return m_converter; }
    operator SbkConverter *() const { return m_converter; }

    bool isValid() const { return m_type != InvalidConversion; }
    operator bool() const { return m_type != InvalidConversion; }

    Type conversionType() const { return m_type; }

    PyObject *toPython(const void *cppIn) const;
    void toCpp(PyObject *pyIn, void *cppOut) const;
private:
    SbkConverter *m_converter;
    Type m_type;
};


LIBSHIBOKEN_API SbkConverter *createConverter(PyTypeObject *type,
                                              PythonToCppFunc toCppPointerConvFunc,
                                              IsConvertibleToCppFunc toCppPointerCheckFunc,
                                              CppToPythonFunc pointerToPythonFunc,
                                              CppToPythonFunc copyToPythonFunc = nullptr);

/*!
    Creates a converter for a non wrapper type (primitive or container type)
    represented by the Python type \a type using the function \a toPythonFunc
    to convert a C++ object to a Python \a type.

    Returns the new type converter.
*/
LIBSHIBOKEN_API SbkConverter *createConverter(PyTypeObject *type, CppToPythonFunc toPythonFunc);

/*!
    \overload

    Creates a converter for a non wrapper type represented by the Python type
    \a type using the function \a toPythonFunc which additionally receives the
    type object.
*/
LIBSHIBOKEN_API SbkConverter *createConverter(PyTypeObject *type, CppToPythonWithTypeFunc toPythonFunc);

/*!
    Deletes the \a converter.
*/
LIBSHIBOKEN_API void deleteConverter(SbkConverter *converter);

/*!
    Sets the C++ pointer to Python object conversion function of
    \a converter to \a pointerToPythonFunc.
*/
LIBSHIBOKEN_API void setCppPointerToPythonFunction(SbkConverter *converter, CppToPythonFunc pointerToPythonFunc);

/*!
    Sets the Python object to C++ pointer conversion functions of \a converter
    to \a toCppPointerConvFunc and the check function \a toCppPointerCheckFunc.
*/
LIBSHIBOKEN_API void setPythonToCppPointerFunctions(SbkConverter *converter,
                                                    PythonToCppFunc toCppPointerConvFunc,
                                                    IsConvertibleToCppFunc toCppPointerCheckFunc);

/*!
    Adds a new conversion of a Python object to a C++ value to \a converter
    consisting of the conversion function \a pythonToCppFunc and the check
    function \a isConvertibleToCppFunc.
    This is used in copy and implicit conversions.
*/
LIBSHIBOKEN_API void addPythonToCppValueConversion(SbkConverter *converter,
                                                   PythonToCppFunc pythonToCppFunc,
                                                   IsConvertibleToCppFunc isConvertibleToCppFunc);
LIBSHIBOKEN_API void prependPythonToCppValueConversion(SbkConverter *converter,
                                                       PythonToCppFunc pythonToCppFunc,
                                                       IsConvertibleToCppFunc isConvertibleToCppFunc);

LIBSHIBOKEN_API void addPythonToCppValueConversion(PyTypeObject *type,
                                                   PythonToCppFunc pythonToCppFunc,
                                                   IsConvertibleToCppFunc isConvertibleToCppFunc);
LIBSHIBOKEN_API void addPythonToCppValueConversion(Shiboken::Module::TypeInitStruct typeStruct,
                                                   PythonToCppFunc pythonToCppFunc,
                                                   IsConvertibleToCppFunc isConvertibleToCppFunc);

// C++ -> Python ---------------------------------------------------------------------------

/*!
    Retrieves the Python wrapper object of \a type for the given \a cppIn
    C++ pointer object.
    This function is used only for Value and Object Types.
    Example usage:

    \code
        TYPE *var;
        PyObject *pyVar = pointerToPython(SBKTYPE, &var);
    \endcode
*/
LIBSHIBOKEN_API PyObject *pointerToPython(PyTypeObject *type, const void *cppIn);

/*!
    \overload

    Retrieves the Python wrapper object for the given \a cppIn
    C++ pointer object using \a converter.
*/
LIBSHIBOKEN_API PyObject *pointerToPython(const SbkConverter *converter, const void *cppIn);

/*!
    For the given \a cppIn C++ reference it returns the Python wrapper object
    of \a type, always for Object Types, and when they already exist for
    reference types; for when the latter doesn't have an existing wrapper type,
    the C++ object is copied to Python.
    Example usage:

    \code
        TYPE &var = SOMETHING;
        PyObject *pyVar = referenceToPython(SBKTYPE, &var);
    \endcode
*/
LIBSHIBOKEN_API PyObject *referenceToPython(PyTypeObject *type, const void *cppIn);

/*!
    \overload

    Returns the Python wrapper object for the given \a cppIn C++ reference
    using \a converter.
*/
LIBSHIBOKEN_API PyObject *referenceToPython(const SbkConverter *converter, const void *cppIn);

/*!
    Retrieves the Python wrapper object of \a type for the given C++ value
    pointed to by \a cppIn.
    This function is used only for Value Types.
    Example usage:

    \code
        TYPE var;
        PyObject *pyVar = copyToPython(SBKTYPE, &var);
    \endcode
*/
LIBSHIBOKEN_API PyObject *copyToPython(PyTypeObject *type, const void *cppIn);

/*!
    \overload

    Retrieves the Python wrapper object for the given C++ value
    pointed to by \a cppIn using \a converter.
*/
LIBSHIBOKEN_API PyObject *copyToPython(const SbkConverter *converter, const void *cppIn);

// Python -> C++ ---------------------------------------------------------------------------

struct PythonToCppConversion
{
    enum Type : uint8_t {Invalid, Pointer, Value};

    operator bool() const { return type != Invalid; }

    void operator()(PyObject *po,void *cpp) const { function(po, cpp); }

    bool isValue() const { return type == Value; }

    PythonToCppFunc function = nullptr;
    Type type = Invalid;
};

/*!
    Returns a Python to C++ conversion function if the Python object \a pyIn
    is convertible to a C++ pointer.
    It returns nullptr if the Python object is not convertible to \a type.
*/
LIBSHIBOKEN_API PythonToCppFunc isPythonToCppPointerConvertible(PyTypeObject *type, PyObject *pyIn);
LIBSHIBOKEN_API PythonToCppConversion pythonToCppPointerConversion(PyTypeObject *type, PyObject *pyIn);
LIBSHIBOKEN_API PythonToCppConversion pythonToCppPointerConversion(Module::TypeInitStruct typeStruct, PyObject *pyIn);

/*!
    Returns a Python to C++ conversion function if the Python object \a pyIn
    is convertible to a C++ value.
    The resulting converter function will create a copy of the Python object
    in C++, or implicitly convert the object to the expected \a type.
    It returns nullptr if the Python object is not convertible to \a type.
*/
LIBSHIBOKEN_API PythonToCppFunc isPythonToCppValueConvertible(PyTypeObject *type, PyObject *pyIn);
LIBSHIBOKEN_API PythonToCppConversion pythonToCppValueConversion(PyTypeObject *type, PyObject *pyIn);

/*!
    Returns a Python to C++ conversion function if the Python object \a pyIn
    is convertible to a C++ reference.
    The resulting converter function will return the underlying C++ object
    held by the Python wrapper, or a new C++ value if it must be an implicit
    conversion.
    It returns nullptr if the Python object is not convertible to \a type.
*/
LIBSHIBOKEN_API PythonToCppFunc isPythonToCppReferenceConvertible(PyTypeObject *type, PyObject *pyIn);
LIBSHIBOKEN_API PythonToCppConversion pythonToCppReferenceConversion(PyTypeObject *type, PyObject *pyIn);

/*!
    This is the same as the isPythonToCppValueConvertible() function,
    checking \a pyIn using \a converter.
*/
LIBSHIBOKEN_API PythonToCppFunc isPythonToCppConvertible(const SbkConverter *converter, PyObject *pyIn);
LIBSHIBOKEN_API PythonToCppConversion pythonToCppReferenceConversion(const SbkConverter *converter, PyObject *pyIn);

LIBSHIBOKEN_API PythonToCppConversion pythonToCppConversion(const SbkConverter *converter, PyObject *pyIn);
LIBSHIBOKEN_API PythonToCppFunc isPythonToCppConvertible(const SbkArrayConverter *converter,
                                                         int dim1, int dim2, PyObject *pyIn);
LIBSHIBOKEN_API PythonToCppConversion pythonToCppConversion(const SbkArrayConverter *converter,
                                                                int dim1, int dim2, PyObject *pyIn);

/*!
    Returns the C++ pointer for the \a pyIn object cast to the type passed via
    \a desiredType.
    It differs from Shiboken::Object::cppPointer() because it casts the pointer
    to a proper memory offset depending on the desired type.
*/
LIBSHIBOKEN_API void *cppPointer(PyTypeObject *desiredType, SbkObject *pyIn);

/*!
    Converts a Python object \a pyIn of \a type to C++ and stores the result
    in the C++ pointer passed in \a cppOut.
*/
LIBSHIBOKEN_API void pythonToCppPointer(PyTypeObject *type, PyObject *pyIn, void *cppOut);

/*!
    \overload

    Converts a Python object \a pyIn to C++ using \a converter and stores
    the result in the C++ pointer passed in \a cppOut.
*/
LIBSHIBOKEN_API void pythonToCppPointer(const SbkConverter *converter, PyObject *pyIn, void *cppOut);

/*!
    Converts a Python object \a pyIn of \a type to C++, and copies the result
    to the C++ variable passed in \a cppOut.
*/
LIBSHIBOKEN_API void pythonToCppCopy(PyTypeObject *type, PyObject *pyIn, void *cppOut);

/*!
    \overload

    Converts a Python object \a pyIn to C++ using \a converter, and copies
    the result to the C++ variable passed in \a cppOut.
*/
LIBSHIBOKEN_API void pythonToCppCopy(const SbkConverter *converter, PyObject *pyIn, void *cppOut);

/*!
    Helper function returned by generated convertible checking functions
    that sets \a cppOut to a C++ nullptr when the input Python object is None.
*/
LIBSHIBOKEN_API void nonePythonToCppNullPtr(PyObject *, void *cppOut);

/*!
    Returns true if the \a toCpp function passed is an implicit conversion of
    Python \a type.
    It is used when C++ expects a reference argument, so it may be the same
    object received from Python, or another created through implicit conversion.
*/
[[deprecated]] LIBSHIBOKEN_API bool isImplicitConversion(PyTypeObject *type, PythonToCppFunc toCpp);

/*!
    Registers a \a converter with a type name \a typeName that may be used to
    retrieve the converter.
    Use for fully qualified names (main type). This will overwrite existing
    converters of the same name.
*/
LIBSHIBOKEN_API void registerConverterName(SbkConverter *converter, const char *typeName);

/*!
    Registers a \a converter with a type name \a typeName that may be used to
    retrieve the converter unless there is already a converter for the name.
    Use for partially qualified names.
*/
LIBSHIBOKEN_API void registerConverterAlias(SbkConverter *converter, const char *typeName);

/*!
    Returns the converter for a given \a typeName, or nullptr if it wasn't
    registered before.
*/
LIBSHIBOKEN_API SbkConverter *getConverter(const char *typeName);

/*!
    Returns the converter for a primitive type identified by \a index.
*/
LIBSHIBOKEN_API SbkConverter *primitiveTypeConverter(int index);

/*!
    Returns true if a Python sequence \a pyIn is comprised of objects of the
    given \a type.
*/
LIBSHIBOKEN_API bool checkSequenceTypes(PyTypeObject *type, PyObject *pyIn);

/*!
    Returns true if a Python object \a pyIn is iterable and comprised of
    objects of the given \a type.
*/
LIBSHIBOKEN_API bool checkIterableTypes(PyTypeObject *type, PyObject *pyIn);

/*!
    Returns true if a Python sequence \a pyIn is comprised of objects of a type
    convertible to the one represented by the given \a converter.
*/
LIBSHIBOKEN_API bool convertibleSequenceTypes(const SbkConverter *converter, PyObject *pyIn);

/*!
    Returns true if a Python sequence \a pyIn is comprised of objects of a type
    convertible to \a type.
*/
LIBSHIBOKEN_API bool convertibleSequenceTypes(PyTypeObject *type, PyObject *pyIn);

/*!
    Returns true if a Python object \a pyIn is iterable and comprised of
    objects of a type convertible to the one represented by the given
    \a converter.
*/
LIBSHIBOKEN_API bool convertibleIterableTypes(const SbkConverter *converter, PyObject *pyIn);

/*!
    Returns true if a Python object \a pyIn is iterable and comprised of
    objects of a type convertible to \a type.
*/
LIBSHIBOKEN_API bool convertibleIterableTypes(PyTypeObject *type, PyObject *pyIn);

/*!
    Returns true if a Python sequence \a pyIn can be converted to a C++ pair
    of \a firstType and \a secondType.
*/
LIBSHIBOKEN_API bool checkPairTypes(PyTypeObject *firstType, PyTypeObject *secondType, PyObject *pyIn);

/*!
    Returns true if a Python sequence \a pyIn can be converted to a C++ pair
    using \a firstConverter and \a secondConverter. \a firstCheckExact and
    \a secondCheckExact indicate whether an exact type check is to be
    performed.
*/
LIBSHIBOKEN_API bool convertiblePairTypes(const SbkConverter *firstConverter, bool firstCheckExact,
                                          const SbkConverter *secondConverter, bool secondCheckExact,
                                          PyObject *pyIn);

/*!
    Returns true if a Python dictionary \a pyIn can be converted to a C++ hash
    or map of \a keyType and \a valueType.
*/
LIBSHIBOKEN_API bool checkDictTypes(PyTypeObject *keyType, PyTypeObject *valueType, PyObject *pyIn);

/*!
    Returns true if a Python dictionary \a pyIn can be converted to a C++
    multi hash/map of \a keyType and \a valueType.
    The Python dictionary is expected to contain lists of values.
*/
bool checkMultiDictTypes(PyTypeObject *keyType, PyTypeObject *valueType,
                         PyObject *pyIn);

/*!
    Returns true if a Python dictionary \a pyIn can be converted to a C++ hash
    or map using \a keyConverter and \a valueConverter. \a keyCheckExact and
    \a valueCheckExact indicate whether an exact type check is to be performed.
*/
LIBSHIBOKEN_API bool convertibleDictTypes(const SbkConverter *keyConverter, bool keyCheckExact,
                                          const SbkConverter *valueConverter, bool valueCheckExact,
                                          PyObject *pyIn);

/*!
    Returns true if a Python dictionary \a pyIn can be converted to a C++
    multi hash/map using \a keyConverter and \a valueConverter.
    \a keyCheckExact and \a valueCheckExact indicate whether an exact type
    check is to be performed.
    The Python dictionary is expected to contain lists of values.
*/
LIBSHIBOKEN_API bool convertibleMultiDictTypes(const SbkConverter *keyConverter,
                                               bool keyCheckExact,
                                               const SbkConverter *valueConverter,
                                               bool valueCheckExact,
                                               PyObject *pyIn);

/*!
    Returns the Python type object associated with the given \a converter.
*/
LIBSHIBOKEN_API PyTypeObject *getPythonTypeObject(const SbkConverter *converter);

/*!
    Returns the Python type object for the given \a typeName.
*/
LIBSHIBOKEN_API PyTypeObject *getPythonTypeObject(const char *typeName);

/*!
    Returns true if the Python type associated with the \a converter is a
    value type.
*/
LIBSHIBOKEN_API bool pythonTypeIsValueType(const SbkConverter *converter);

/*!
    Returns true if the Python type associated with the \a converter is an
    object type.
*/
LIBSHIBOKEN_API bool pythonTypeIsObjectType(const SbkConverter *converter);

/*!
    Returns true if the Python type associated with the \a converter is a
    wrapper type.
*/
LIBSHIBOKEN_API bool pythonTypeIsWrapperType(const SbkConverter *converter);

enum  : int {
SBK_PY_LONG_LONG_IDX =             0,
// Qt5: name collision in QtCore after QBool is replaced by bool
SBK_BOOL_IDX_1 =                   1,
SBK_CHAR_IDX =                     2,
SBK_CONSTCHARPTR_IDX =             3,
SBK_DOUBLE_IDX =                   4,
SBK_FLOAT_IDX =                    5,
SBK_INT_IDX =                      6,
SBK_SIGNEDINT_IDX =                6,
SBK_LONG_IDX =                     7,
SBK_SHORT_IDX =                    8,
SBK_SIGNEDCHAR_IDX =               9,
SBK_STD_STRING_IDX =              10,
SBK_STD_WSTRING_IDX =             11,
SBK_UNSIGNEDPY_LONG_LONG_IDX =    12,
SBK_UNSIGNEDCHAR_IDX =            13,
SBK_UNSIGNEDINT_IDX =             14,
SBK_UNSIGNEDLONG_IDX =            15,
SBK_UNSIGNEDSHORT_IDX =           16,
SBK_VOIDPTR_IDX =                 17,
SBK_NULLPTR_T_IDX =               18
};

template<typename T> SbkConverter *PrimitiveTypeConverter() { return nullptr; }
template<> inline SbkConverter *PrimitiveTypeConverter<PY_LONG_LONG>() { return primitiveTypeConverter(SBK_PY_LONG_LONG_IDX); }
template<> inline SbkConverter *PrimitiveTypeConverter<bool>() { return primitiveTypeConverter(SBK_BOOL_IDX_1); }
template<> inline SbkConverter *PrimitiveTypeConverter<char>() { return primitiveTypeConverter(SBK_CHAR_IDX); }
template<> inline SbkConverter *PrimitiveTypeConverter<const char *>() { return primitiveTypeConverter(SBK_CONSTCHARPTR_IDX); }
template<> inline SbkConverter *PrimitiveTypeConverter<double>() { return primitiveTypeConverter(SBK_DOUBLE_IDX); }
template<> inline SbkConverter *PrimitiveTypeConverter<float>() { return primitiveTypeConverter(SBK_FLOAT_IDX); }
template<> inline SbkConverter *PrimitiveTypeConverter<int>() { return primitiveTypeConverter(SBK_INT_IDX); }
template<> inline SbkConverter *PrimitiveTypeConverter<long>() { return primitiveTypeConverter(SBK_LONG_IDX); }
template<> inline SbkConverter *PrimitiveTypeConverter<short>() { return primitiveTypeConverter(SBK_SHORT_IDX); }
template<> inline SbkConverter *PrimitiveTypeConverter<signed char>() { return primitiveTypeConverter(SBK_SIGNEDCHAR_IDX); }
template<> inline SbkConverter *PrimitiveTypeConverter<std::string>() { return primitiveTypeConverter(SBK_STD_STRING_IDX); }
template<> inline SbkConverter *PrimitiveTypeConverter<std::wstring>() { return primitiveTypeConverter(SBK_STD_WSTRING_IDX); }
template<> inline SbkConverter *PrimitiveTypeConverter<unsigned PY_LONG_LONG>() { return primitiveTypeConverter(SBK_UNSIGNEDPY_LONG_LONG_IDX); }
template<> inline SbkConverter *PrimitiveTypeConverter<unsigned char>() { return primitiveTypeConverter(SBK_UNSIGNEDCHAR_IDX); }
template<> inline SbkConverter *PrimitiveTypeConverter<unsigned int>() { return primitiveTypeConverter(SBK_UNSIGNEDINT_IDX); }
template<> inline SbkConverter *PrimitiveTypeConverter<unsigned long>() { return primitiveTypeConverter(SBK_UNSIGNEDLONG_IDX); }
template<> inline SbkConverter *PrimitiveTypeConverter<unsigned short>() { return primitiveTypeConverter(SBK_UNSIGNEDSHORT_IDX); }
template<> inline SbkConverter *PrimitiveTypeConverter<void *>() { return primitiveTypeConverter(SBK_VOIDPTR_IDX); }
template<> inline SbkConverter *PrimitiveTypeConverter<std::nullptr_t>() { return primitiveTypeConverter(SBK_NULLPTR_T_IDX); }

} // namespace Shiboken::Conversions

/*!
    This function template is used to get the PyTypeObject of a C++ type \c T.
    All implementations should be provided by template specializations
    generated by the generator when \c T isn't a C++ primitive type.
*/
template<typename T> PyTypeObject *SbkType() { return nullptr; }

// Below are the template specializations for C++ primitive types.
template<> inline PyTypeObject *SbkType<PY_LONG_LONG>() { return &PyLong_Type; }
template<> inline PyTypeObject *SbkType<bool>() { return &PyBool_Type; }
template<> inline PyTypeObject *SbkType<char>() { return &PyLong_Type; }
template<> inline PyTypeObject *SbkType<double>() { return &PyFloat_Type; }
template<> inline PyTypeObject *SbkType<float>() { return &PyFloat_Type; }
template<> inline PyTypeObject *SbkType<int>() { return &PyLong_Type; }
template<> inline PyTypeObject *SbkType<long>() { return &PyLong_Type; }
template<> inline PyTypeObject *SbkType<short>() { return &PyLong_Type; }
template<> inline PyTypeObject *SbkType<signed char>() { return &PyLong_Type; }
template<> inline PyTypeObject *SbkType<unsigned PY_LONG_LONG>() { return &PyLong_Type; }
template<> inline PyTypeObject *SbkType<unsigned char>() { return &PyLong_Type; }
template<> inline PyTypeObject *SbkType<unsigned int>() { return &PyLong_Type; }
template<> inline PyTypeObject *SbkType<unsigned long>() { return &PyLong_Type; }
template<> inline PyTypeObject *SbkType<unsigned short>() { return &PyLong_Type; }
template<> inline PyTypeObject *SbkType<std::nullptr_t>() { return Py_TYPE(&_Py_NoneStruct); }

} // namespace Shiboken

LIBSHIBOKEN_API bool SbkChar_Check(PyObject *X);

#endif // SBK_CONVERTER_H
