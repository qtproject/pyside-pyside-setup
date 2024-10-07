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

// @snippet qwebenginepage-runjavascript-2
using RunJavascriptCallback = std::function<void(const QVariant &)>;

if (%PYARG_2 != nullptr && %PYARG_2 != Py_None) {
    %CPPSELF.%FUNCTION_NAME(%1, RunJavascriptCallback(RunJavascriptFunctor(%PYARG_2)));
} else {
    %CPPSELF.%FUNCTION_NAME(%1, 0, RunJavascriptCallback{});
}
// @snippet qwebenginepage-runjavascript-2

// @snippet qwebenginepage-runjavascript-3
using RunJavascriptCallback = std::function<void(const QVariant &)>;

if (%PYARG_3 != nullptr && %PYARG_3 != Py_None) {
    %CPPSELF.%FUNCTION_NAME(%1, %2, RunJavascriptCallback(RunJavascriptFunctor(%PYARG_3)));
} else {
    %CPPSELF.%FUNCTION_NAME(%1, %2, RunJavascriptCallback{});
}
// @snippet qwebenginepage-runjavascript-3

// @snippet qwebenginepage-printtopdf
using PrintToPdfCallback = std::function<void(const QByteArray &)>;

%CPPSELF.%FUNCTION_NAME(PrintToPdfCallback(PrintToPdfFunctor(%PYARG_1)), %2, %3);
// @snippet qwebenginepage-printtopdf

// @snippet qwebenginepage-findframebyname
auto frameOptional = %CPPSELF.%FUNCTION_NAME(%1);
if (frameOptional.has_value()) {
    const %RETURN_TYPE &frame = frameOptional.value();
    %PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](frame);
} else {
    Py_INCREF(Py_None);
    %PYARG_0 = Py_None;
}
// @snippet qwebenginepage-findframebyname

// @snippet qwebengineframe-printtopdf
using PrintToPdfCallback = std::function<void(const QByteArray &)>;

%CPPSELF.%FUNCTION_NAME(PrintToPdfCallback(PrintToPdfFunctor(%PYARG_1)));
// @snippet qwebengineframe-printtopdf
