// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

// @snippet qwebenginecookiestore-setcookiefilter
auto callable = %PYARG_1;
auto callback = [callable](const QWebEngineCookieStore::FilterRequest& filterRequest) -> bool
{
    Shiboken::GilState state;
    Shiboken::AutoDecRef arglist(PyTuple_New(1));
    PyTuple_SET_ITEM(arglist, 0,
                    %CONVERTTOPYTHON[QWebEngineCookieStore::FilterRequest](filterRequest));
    Py_INCREF(callable);
    Shiboken::AutoDecRef ret(PyObject_CallObject(callable, arglist));
    Py_DECREF(callable);
    return ret.object() == Py_True;
};

%CPPSELF.%FUNCTION_NAME(callback);
// @snippet qwebenginecookiestore-setcookiefilter

// @snippet qwebengineprofile-setnotificationpresenter
auto callable = %PYARG_1;
auto callback = [callable](std::unique_ptr<QWebEngineNotification> webEngineNotification) -> void
{
    Shiboken::GilState state;
    Shiboken::AutoDecRef arglist(PyTuple_New(1));
    auto *notification = webEngineNotification.release();
    PyTuple_SET_ITEM(arglist.object(), 0,
                     %CONVERTTOPYTHON[QWebEngineNotification*](notification));
    Py_INCREF(callable);
    Shiboken::AutoDecRef ret(PyObject_CallObject(callable, arglist));
    Py_DECREF(callable);
};

%CPPSELF.%FUNCTION_NAME(callback);
// @snippet qwebengineprofile-setnotificationpresenter
