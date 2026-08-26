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

// @snippet optional-qreal-to-pyfloat
if (!%in.has_value())
    Py_RETURN_NONE;
return PyFloat_FromDouble(%in.value());
// @snippet optional-qreal-to-pyfloat

// @snippet pyfloat-to-optional-qreal
%out = PyFloat_AsDouble(%in);
// @snippet pyfloat-to-optional-qreal

// @snippet pylong-to-optional-qreal
%out = PyLong_AsDouble(%in);
// @snippet pylong-to-optional-qreal

// @snippet pynone-to-optional
%out = std::nullopt;
// @snippet pynone-to-optional
