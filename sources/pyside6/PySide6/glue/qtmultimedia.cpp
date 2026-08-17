// Copyright (C) 2018 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

// @snippet qvideoframe-bits
#include "object.h"
%BEGIN_ALLOW_THREADS
%RETURN_TYPE %0 = %CPPSELF.%FUNCTION_NAME(%1);
%END_ALLOW_THREADS
const auto size = %CPPSELF.mappedBytes(%1);
%PYARG_0 = Shiboken::Buffer::newObject(%0, size, Shiboken::Buffer::ReadWrite);
// @snippet qvideoframe-bits

// @snippet capture-maximumframerate
const std::optional<qreal> result = %CPPSELF.%FUNCTION_NAME();
if (result.has_value()) {
    %PYARG_0 = PyFloat_FromDouble(result.value());
} else {
    Py_INCREF(Py_None);
    %PYARG_0 = Py_None;
}
// @snippet capture-maximumframerate

// @snippet capture-setmaximumframerate
if (%PYARG_1 == Py_None) {
    %CPPSELF.%FUNCTION_NAME({});
} else if (PyFloat_Check(%PYARG_1) != 0) {
    const auto value = qreal(PyFloat_AsDouble(%PYARG_1));
    %CPPSELF.%FUNCTION_NAME(value);
} else if (PyLong_Check(%PYARG_1) != 0) {
    const auto value = qreal( PyLong_AsDouble(%PYARG_1));
    %CPPSELF.%FUNCTION_NAME(value);
} else {
    PyErr_SetString(PyExc_TypeError, "parameter must be float or None");
}
// @snippet capture-setmaximumframerate

// @snippet qaudiobuffer-data
unsigned char *data = %CPPSELF.%FUNCTION_NAME<unsigned char>();
const auto size = %CPPSELF.byteCount();
%PYARG_0 = Shiboken::Buffer::newObject(data, size, Shiboken::Buffer::ReadWrite);
// @snippet qaudiobuffer-data

// @snippet qaudiobuffer-const-data
const unsigned char *data = %CPPSELF.%FUNCTION_NAME<unsigned char>();
const auto size = %CPPSELF.byteCount();
%PYARG_0 = Shiboken::Buffer::newObject(data, size);
// @snippet qaudiobuffer-const-data

// @snippet qaudio-convertvolume
const float result = QtAudio::convertVolume(%1, %2, %3);
%PYARG_0 = %CONVERTTOPYTHON[float](result);
// @snippet qaudio-convertvolume
