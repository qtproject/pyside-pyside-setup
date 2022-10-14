// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

/*********************************************************************
 * INJECT CODE
 ********************************************************************/

// @snippet qcanbus-available-devices
QString errorMessage;
const QList<QCanBusDeviceInfo> result = %CPPSELF.%FUNCTION_NAME(%1, &errorMessage);
%PYARG_0 = PyTuple_New(2);
PyTuple_SET_ITEM(%PYARG_0, 0, %CONVERTTOPYTHON[QList<QCanBusDeviceInfo>](result));
PyTuple_SET_ITEM(%PYARG_0, 1, %CONVERTTOPYTHON[QString](errorMessage));
// @snippet qcanbus-available-devices

// @snippet qcanbus-createdevice
PyObject *pyDevice{};
QString errorMessage;
if (auto *device = %CPPSELF.%FUNCTION_NAME(%1, %2, &errorMessage)) {
    pyDevice = %CONVERTTOPYTHON[%RETURN_TYPE](device);
    // Ownership transferences (target)
    Shiboken::Object::getOwnership(pyDevice);
} else {
    pyDevice = Py_None;
    Py_INCREF(pyDevice);
}
%PYARG_0 = PyTuple_New(2);
PyTuple_SET_ITEM(%PYARG_0, 0, pyDevice);
PyTuple_SET_ITEM(%PYARG_0, 1, %CONVERTTOPYTHON[QString](errorMessage));
// @snippet qcanbus-createdevice
