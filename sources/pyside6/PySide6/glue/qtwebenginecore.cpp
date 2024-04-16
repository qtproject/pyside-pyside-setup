// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

// @snippet qwebenginecookiestore-functor
struct QWebEngineCookieFilterFunctor : public Shiboken::PyObjectHolder
{
    using Shiboken::PyObjectHolder::PyObjectHolder;

    bool operator()(const QWebEngineCookieStore::FilterRequest& filterRequest) const;
};

bool QWebEngineCookieFilterFunctor::operator()(const QWebEngineCookieStore::FilterRequest &
                                               filterRequest) const
{
    Shiboken::GilState state;
    Shiboken::AutoDecRef arglist(PyTuple_New(1));
    PyTuple_SET_ITEM(arglist, 0,
                     %CONVERTTOPYTHON[QWebEngineCookieStore::FilterRequest](filterRequest));
    Shiboken::AutoDecRef ret(PyObject_CallObject(object(), arglist));
    return ret.object() == Py_True;
}
// @snippet qwebenginecookiestore-functor

// @snippet qwebenginecookiestore-setcookiefilter
%CPPSELF.%FUNCTION_NAME(QWebEngineCookieFilterFunctor(%PYARG_1));
// @snippet qwebenginecookiestore-setcookiefilter

// @snippet qwebengineprofile-functor
struct QWebEngineNotificationFunctor : public Shiboken::PyObjectHolder
{
    using Shiboken::PyObjectHolder::PyObjectHolder;

    void operator()(std::unique_ptr<QWebEngineNotification> webEngineNotification);
};

void QWebEngineNotificationFunctor::operator()
    (std::unique_ptr<QWebEngineNotification> webEngineNotification)
{
    Shiboken::GilState state;
    Shiboken::AutoDecRef arglist(PyTuple_New(1));
    auto *notification = webEngineNotification.release();
    PyTuple_SET_ITEM(arglist.object(), 0,
                     %CONVERTTOPYTHON[QWebEngineNotification*](notification));
    Shiboken::AutoDecRef ret(PyObject_CallObject(object(), arglist));
};
// @snippet qwebengineprofile-functor

// @snippet qwebengineprofile-setnotificationpresenter
%CPPSELF.%FUNCTION_NAME(QWebEngineNotificationFunctor(%PYARG_1));
// @snippet qwebengineprofile-setnotificationpresenter

// @snippet qwebenginepage-javascriptprompt-virtual-redirect
std::pair<bool, QString> resultPair = javaScriptPromptPyOverride(gil, pyOverride.object(), securityOrigin, msg, defaultValue);
result->assign(resultPair.second);
return resultPair.first;
// @snippet qwebenginepage-javascriptprompt-virtual-redirect

// @snippet qwebenginepage-javascriptprompt-return
QString str;
%RETURN_TYPE retval_ = %CPPSELF.%FUNCTION_NAME(%1, %2, %3, &str);
%PYARG_0 = PyTuple_New(2);
PyTuple_SET_ITEM(%PYARG_0, 0, %CONVERTTOPYTHON[%RETURN_TYPE](retval_));
PyTuple_SET_ITEM(%PYARG_0, 1, %CONVERTTOPYTHON[QString](str));
// @snippet qwebenginepage-javascriptprompt-return
