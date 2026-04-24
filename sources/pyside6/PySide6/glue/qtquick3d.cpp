// Copyright (C) 2024 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

/*********************************************************************
 * INJECT CODE
 ********************************************************************/

// @snippet qquick3dinstancing-getinstancebuffer-virtual-redirect
std::pair<QByteArray, int> resultPair = getInstanceBufferOverride(gil, pyOverride.object());
if (instanceCount != nullptr)
    *instanceCount = resultPair.second;
return resultPair.first;
// @snippet qquick3dinstancing-getinstancebuffer-virtual-redirect

// @snippet qquick3dinstancing-getinstancebuffer-return
int count{};
%RETURN_TYPE retval_ = %CPPSELF.%FUNCTION_NAME(&count);
%PYARG_0 = PyTuple_New(2);
PyTuple_SetItem(%PYARG_0, 0, %CONVERTTOPYTHON[%RETURN_TYPE](retval_));
PyTuple_SetItem(%PYARG_0, 1, %CONVERTTOPYTHON[int](count));
// @snippet qquick3dinstancing-getinstancebuffer-return
