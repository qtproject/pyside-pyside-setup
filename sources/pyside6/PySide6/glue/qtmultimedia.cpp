// Copyright (C) 2018 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

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

// @snippet qtaudio-namespace-compatibility-alias
Py_INCREF(pyType);
PyModule_AddObject(module, "QtAudio", reinterpret_cast<PyObject *>(pyType));
// @snippet qtaudio-namespace-compatibility-alias
