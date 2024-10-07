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

// @snippet qwebenginepage-findtext
auto callable = %PYARG_3;
auto callback = [callable](const QWebEngineFindTextResult &result)
{
    Shiboken::GilState state;
    Shiboken::AutoDecRef arglist(PyTuple_New(1));
    PyTuple_SET_ITEM(arglist, 0, %CONVERTTOPYTHON[QWebEngineFindTextResult](result));
    Shiboken::AutoDecRef ret(PyObject_CallObject(callable, arglist));
    Py_DECREF(callable);

};
Py_INCREF(callable);
%CPPSELF.%FUNCTION_NAME(%1, %2, callback);
// @snippet qwebenginepage-findtext

// @snippet qwebenginepage-print
auto printer = %PYARG_1;
auto callable = %PYARG_2;
auto callback = [printer, callable](bool succeeded)
{
    if (!PyCallable_Check(callable)) {
        qWarning("Argument 2 of %FUNCTION_NAME must be a callable.");
        return;
    }
    Shiboken::GilState state;
    Shiboken::AutoDecRef arglist(PyTuple_New(1));
    PyTuple_SET_ITEM(arglist, 0, %CONVERTTOPYTHON[bool](succeeded));
    Shiboken::AutoDecRef ret(PyObject_CallObject(callable, arglist));
    Py_DECREF(callable);
    Py_DECREF(printer);

};
Py_INCREF(printer); // Add a reference to the printer until asynchronous printing has finished
Py_INCREF(callable);
%CPPSELF.%FUNCTION_NAME(%1, callback);
// @snippet qwebenginepage-print

// @snippet qwebenginepage-convertto
auto callable = %PYARG_1;
auto callback = [callable](const QString &text)
{
    Shiboken::GilState state;
    Shiboken::AutoDecRef arglist(PyTuple_New(1));
    PyTuple_SET_ITEM(arglist, 0, %CONVERTTOPYTHON[QString](text));
    Shiboken::AutoDecRef ret(PyObject_CallObject(callable, arglist));
    Py_DECREF(callable);
};

Py_INCREF(callable);
%CPPSELF.%FUNCTION_NAME(callback);
// @snippet qwebenginepage-convertto

// @snippet qwebenginepage-runjavascript
auto callable = %PYARG_3;
auto callback = [callable](const QVariant &result)
{
    Shiboken::GilState state;
    Shiboken::AutoDecRef arglist(PyTuple_New(1));
    switch (result.type()) {
    case QVariant::Bool: {
        const bool value = result.toBool();
        PyTuple_SET_ITEM(arglist, 0, %CONVERTTOPYTHON[QString](value));
    }
    break;
    case QVariant::Int:
    case QVariant::UInt:
    case QVariant::LongLong:
    case QVariant::ULongLong:
    case QVariant::Double: {
        const double number = result.toDouble();
        PyTuple_SET_ITEM(arglist, 0, %CONVERTTOPYTHON[double](number));
    }
    break;
    default: {
        const QString value = result.toString();
        PyTuple_SET_ITEM(arglist, 0, %CONVERTTOPYTHON[QString](value));
    }
    break;
    }
    // PyTuple_SET_ITEM(arglist, 0, %CONVERTTOPYTHON[bool](found));
    Shiboken::AutoDecRef ret(PyObject_CallObject(callable, arglist));
    Py_DECREF(callable);
};

Py_INCREF(callable);
%CPPSELF.%FUNCTION_NAME(%1, %2, callback);
// @snippet qwebenginepage-runjavascript

// @snippet qwebenginepage-printtopdf
auto callable = %PYARG_1;
auto callback = [callable](const QByteArray &pdf)
{
    if (!PyCallable_Check(callable)) {
        qWarning("Argument 1 of %FUNCTION_NAME must be a callable.");
        return;
    }
    Shiboken::GilState state;
    Shiboken::AutoDecRef arglist(PyTuple_New(1));
    PyTuple_SET_ITEM(arglist, 0, %CONVERTTOPYTHON[QByteArray](pdf));
    Shiboken::AutoDecRef ret(PyObject_CallObject(callable, arglist));
    Py_DECREF(callable);
};

Py_INCREF(callable);
%CPPSELF.%FUNCTION_NAME(callback, %2);
// @snippet qwebenginepage-printtopdf
