/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:GPL-EXCEPT$
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** GNU General Public License Usage
** Alternatively, this file may be used under the terms of the GNU
** General Public License version 3 as published by the Free Software
** Foundation with exceptions as appearing in the file LICENSE.GPL3-EXCEPT
** included in the packaging of this file. Please review the following
** information to ensure the GNU General Public License requirements will
** be met: https://www.gnu.org/licenses/gpl-3.0.html.
**
** $QT_END_LICENSE$
**
****************************************************************************/

#include "predefined_templates.h"

static QString pySequenceToCppContainer(const QString &insertFunc,
                                        bool reserve)
{
    QString result;
    if (reserve) {
        result += uR"(if (PyList_Check(%in)) {
    const Py_ssize_t size = PySequence_Size(%in);
    if (size > 10)
        (%out).reserve(size);
}

)"_qs;
    }

    result += uR"(Shiboken::AutoDecRef it(PyObject_GetIter(%in));
while (true) {
    Shiboken::AutoDecRef pyItem(PyIter_Next(it.object()));
    if (pyItem.isNull()) {
        if (PyErr_Occurred() && PyErr_ExceptionMatches(PyExc_StopIteration))
            PyErr_Clear();
        break;
    }
    %OUTTYPE_0 cppItem = %CONVERTTOCPP[%OUTTYPE_0](pyItem);
    (%out).)"_qs;

    result += insertFunc;
    result += uR"((cppItem);
}
)"_qs;
    return result;
}

static const char stlMapKeyAccessor[] = "->first";
static const char stlMapValueAccessor[] = "->second";
static const char qtMapKeyAccessor[] = ".key()";
static const char qtMapValueAccessor[] = ".value()";

static QString cppMapToPyDict(bool isQMap)
{
    return uR"(PyObject *%out = PyDict_New();
for (auto it = %in.cbegin(), end = %in.cend(); it != end; ++it) {
    const auto &key = it)"_qs
        + QLatin1String(isQMap ? qtMapKeyAccessor : stlMapKeyAccessor)
        + uR"(;
    const auto &value = it)"_qs
        + QLatin1String(isQMap ? qtMapValueAccessor : stlMapValueAccessor)
        + uR"(;
    PyObject *pyKey = %CONVERTTOPYTHON[%INTYPE_0](key);
    PyObject *pyValue = %CONVERTTOPYTHON[%INTYPE_1](value);
    PyDict_SetItem(%out, pyKey, pyValue);
    Py_DECREF(pyKey);
    Py_DECREF(pyValue);
}
return %out;
)"_qs;
}

static QString pyDictToCppMap(bool isQMap)
{
    return uR"(PyObject *key;
PyObject *value;
Py_ssize_t pos = 0;
while (PyDict_Next(%in, &pos, &key, &value)) {
    %OUTTYPE_0 cppKey = %CONVERTTOCPP[%OUTTYPE_0](key);
    %OUTTYPE_1 cppValue = %CONVERTTOCPP[%OUTTYPE_1](value);
    %out.insert()"_qs
    // STL needs a pair
    + (isQMap ? u"cppKey, cppValue"_qs : u"{cppKey, cppValue}"_qs) + uR"();
}
)"_qs;
}

// Convert a STL or Qt multi map to Dict of Lists using upperBound()
static QString cppMultiMapToPyDict(bool isQMultiMap)
{
    return uR"(PyObject *%out = PyDict_New();
    for (auto it = %in.cbegin(), end = %in.cend(); it != end; ++it) {
        const auto &key = it)"_qs
        +  QLatin1String(isQMultiMap ? qtMapKeyAccessor : stlMapKeyAccessor)
        + uR"(;
        PyObject *pyKey = %CONVERTTOPYTHON[%INTYPE_0](key);
        auto upper = %in.)"_qs
       + (isQMultiMap ? u"upperBound"_qs : u"upper_bound"_qs)
       + uR"((key);
        const auto count = Py_ssize_t(std::distance(it, upper));
        PyObject *pyValues = PyList_New(count);
        Py_ssize_t idx = 0;
        for (; it != upper; ++it, ++idx) {
            const auto &cppItem = it.value();
            PyList_SET_ITEM(pyValues, idx, %CONVERTTOPYTHON[%INTYPE_1](cppItem));
        }
        PyDict_SetItem(%out, pyKey, pyValues);
        Py_DECREF(pyKey);
    }
    return %out;
)"_qs;
}

// Convert a STL or Qt multi hash to Dict of Lists using equalRange()
static QString cppMultiHashToPyDict(bool isQMultiHash)
{
    return uR"(PyObject *%out = PyDict_New();
    for (auto it = %in.cbegin(), end = %in.cend(); it != end; ++it) {
        const auto &key = it)"_qs
           +  QLatin1String(isQMultiHash ? qtMapKeyAccessor : stlMapKeyAccessor)
           + uR"(;
        PyObject *pyKey = %CONVERTTOPYTHON[%INTYPE_0](key);
        auto range = %in.equal_range(key);
        const auto count = Py_ssize_t(std::distance(range.first, range.second));
        PyObject *pyValues = PyList_New(count);
        Py_ssize_t idx = 0;
        for (; it != range.second; ++it, ++idx) {
            const auto &cppItem = it.value();
            PyList_SET_ITEM(pyValues, idx, %CONVERTTOPYTHON[%INTYPE_1](cppItem));
        }
        PyDict_SetItem(%out, pyKey, pyValues);
        Py_DECREF(pyKey);
    }
    return %out;
)"_qs;
}

// Convert Dict of Lists to a STL or Qt multi hash/map
static QString pyDictToCppMultiHash(bool isQMultiHash)
{
    return uR"(PyObject *key;
    PyObject *values;
    Py_ssize_t pos = 0;
    while (PyDict_Next(%in, &pos, &key, &values)) {
        %OUTTYPE_0 cppKey = %CONVERTTOCPP[%OUTTYPE_0](key);
        const Py_ssize_t size = PySequence_Size(values);
        for (Py_ssize_t i = 0; i < size; ++i) {
            Shiboken::AutoDecRef value(PySequence_GetItem(values, i));
            %OUTTYPE_1 cppValue = %CONVERTTOCPP[%OUTTYPE_1](value);
            %out.insert()"_qs
        + (isQMultiHash ? u"cppKey, cppValue"_qs : u"{cppKey, cppValue}"_qs)
        + uR"();
        }
    }
)"_qs;
}

const PredefinedTemplates &predefinedTemplates()
{
    static const PredefinedTemplates result{
    {u"shiboken_conversion_pylong_to_cpp"_qs,
     u"%out = %OUTTYPE(PyLong_AsLong(%in));\n"_qs},

    // QPair/std::pair
    {u"shiboken_conversion_pysequence_to_cpppair"_qs,
     uR"(%out.first = %CONVERTTOCPP[%OUTTYPE_0](PySequence_Fast_GET_ITEM(%in, 0));
%out.second = %CONVERTTOCPP[%OUTTYPE_1](PySequence_Fast_GET_ITEM(%in, 1));
)"_qs},

    {u"shiboken_conversion_cpppair_to_pytuple"_qs,
    uR"(PyObject *%out = PyTuple_New(2);
PyTuple_SET_ITEM(%out, 0, %CONVERTTOPYTHON[%INTYPE_0](%in.first));
PyTuple_SET_ITEM(%out, 1, %CONVERTTOPYTHON[%INTYPE_1](%in.second));
return %out;
)"_qs},

    // Sequential containers
    {u"shiboken_conversion_cppsequence_to_pylist"_qs,
     uR"(PyObject *%out = PyList_New(Py_ssize_t(%in.size()));
Py_ssize_t idx = 0;
for (auto it = %in.cbegin(), end = %in.cend(); it != end; ++it, ++idx) {
    const auto &cppItem = *it;
    PyList_SET_ITEM(%out, idx, %CONVERTTOPYTHON[%INTYPE_0](cppItem));
}
return %out;)"_qs},

    // PySet
    {u"shiboken_conversion_cppsequence_to_pyset"_qs,
     uR"(PyObject *%out = PySet_New(nullptr);
for (const auto &cppItem : %in) {
    PySet_Add(%out, %CONVERTTOPYTHON[%INTYPE_0](cppItem));
}
return %out;)"_qs},

    {u"shiboken_conversion_pyiterable_to_cppsequentialcontainer"_qs,
     pySequenceToCppContainer(u"push_back"_qs, false)},
    {u"shiboken_conversion_pyiterable_to_cppsequentialcontainer_reserve"_qs,
     pySequenceToCppContainer(u"push_back"_qs, true)},
    {u"shiboken_conversion_pyiterable_to_cppsetcontainer"_qs,
     pySequenceToCppContainer(u"insert"_qs, false)},

    // Maps
    {u"shiboken_conversion_stdmap_to_pydict"_qs,
     cppMapToPyDict(false)},
    {u"shiboken_conversion_qmap_to_pydict"_qs,
     cppMapToPyDict(true)},
    {u"shiboken_conversion_pydict_to_stdmap"_qs,
     pyDictToCppMap(false)},
    {u"shiboken_conversion_pydict_to_qmap"_qs,
     pyDictToCppMap(true)},

    // Multi maps
    {u"shiboken_conversion_stdmultimap_to_pydict"_qs,
     cppMultiMapToPyDict(false)},
    {u"shiboken_conversion_qmultimap_to_pydict"_qs,
     cppMultiMapToPyDict(true)},

    // Multi hashes
    {u"shiboken_conversion_stdunorderedmultimap_to_pydict"_qs,
     cppMultiHashToPyDict(false)},
    {u"shiboken_conversion_qmultihash_to_pydict"_qs,
     cppMultiHashToPyDict(true)},

    // STL multi hash/map
    {u"shiboken_conversion_pydict_to_stdmultimap"_qs,
     pyDictToCppMultiHash(false)},
    {u"shiboken_conversion_pydict_to_qmultihash"_qs,
     pyDictToCppMultiHash(true)}
    };

    return result;
}

QByteArray containerTypeSystemSnippet(const char *name, const char *type,
                                      const char *include,
                                      const char *nativeToTarget,
                                      const char *targetToNativeType,
                                      const char *targetToNative)
{
    return QByteArrayLiteral("<container-type name=\"")
            + name + QByteArrayLiteral("\" type=\"") + type + R"(">
    <include file-name=")" + include + R"(" location="global"/>
    <conversion-rule>
        <native-to-target>
            <insert-template name=")" + nativeToTarget + R"("/>
        </native-to-target>
        <target-to-native>
            <add-conversion type=")" + targetToNativeType + R"(">
                <insert-template name=")" + targetToNative + R"("/>
            </add-conversion>
        </target-to-native>
    </conversion-rule>
</container-type>
)";
}
