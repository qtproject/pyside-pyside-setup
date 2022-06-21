// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

/*********************************************************************
 * INJECT CODE
 ********************************************************************/

// Note: Lambdas need to be inline, QTBUG-104481
// @snippet qhttpserver-route
QString rule = %CONVERTTOCPP[QString](%PYARG_1);
auto *callable = %PYARG_2;

bool cppResult = %CPPSELF.%FUNCTION_NAME(rule,
                                         [callable](const QHttpServerRequest &request) -> QString {
    Shiboken::GilState state;
    auto *requestPtr = &request;
    Shiboken::AutoDecRef arglist(PyTuple_New(1));
    PyTuple_SET_ITEM(arglist, 0,
                     %CONVERTTOPYTHON[QHttpServerRequest *](requestPtr));
    PyObject *ret = PyObject_CallObject(callable, arglist);
    if (PyErr_Occurred())
        PyErr_Print();
    if (ret == nullptr)
        return QString{};
    QString cppResult = %CONVERTTOCPP[QString](ret);
    return cppResult;
});

%PYARG_0 = %CONVERTTOPYTHON[bool](cppResult);
// @snippet qhttpserver-route

// @snippet qhttpserver-afterrequest
auto *callable = %PYARG_1;

%CPPSELF.%FUNCTION_NAME([callable](QHttpServerResponse &&response,
                                   const QHttpServerRequest &request) {
    Shiboken::GilState state;
    Shiboken::AutoDecRef arglist(PyTuple_New(2));
    auto *responsePtr = &response;
    auto *requestPtr = &request;
    PyTuple_SET_ITEM(arglist, 0,
                     %CONVERTTOPYTHON[QHttpServerResponse *](responsePtr));
    PyTuple_SET_ITEM(arglist, 1,
                     %CONVERTTOPYTHON[QHttpServerRequest *](requestPtr));
    PyObject_CallObject(callable, arglist);
    if (PyErr_Occurred())
        PyErr_Print();
    return std::move(response);
});
// @snippet qhttpserver-afterrequest
