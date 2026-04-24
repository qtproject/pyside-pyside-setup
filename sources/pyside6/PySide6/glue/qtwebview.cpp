// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

// @snippet qwebview-runjavascriptfunctor
struct RunJavascriptFunctor : public Shiboken::PyObjectHolder
{
    using Shiboken::PyObjectHolder::PyObjectHolder;

    void operator()(const QVariant &result)
    {
        Shiboken::GilState state;
        Shiboken::AutoDecRef arglist(PyTuple_Pack(1, PySide::Variant::javascriptVariantToPython(result)));
        Shiboken::AutoDecRef ret(PyObject_CallObject(object(), arglist));
        release(); // single shot
    }
};
// @snippet qwebview-runjavascriptfunctor

// @snippet qwebview-runjavascript
using RunJavascriptCallback = std::function<void(const QVariant &)>;

if (%PYARG_2 != nullptr && %PYARG_2 != Py_None) {
    %CPPSELF.%FUNCTION_NAME(%1, RunJavascriptCallback(RunJavascriptFunctor(%PYARG_2)));
} else {
    %CPPSELF.%FUNCTION_NAME(%1, RunJavascriptCallback{});
}
// @snippet qwebview-runjavascript
