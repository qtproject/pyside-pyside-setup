// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

// @snippet qabstractoauth-lookuphost-functor
struct QAbstractOAuthModifyFunctor : public Shiboken::PyObjectHolder
{
public:
    using Shiboken::PyObjectHolder::PyObjectHolder;

    void operator()(QAbstractOAuth::Stage stage, QMultiMap<QString, QVariant>* dictPointer);
};

void QAbstractOAuthModifyFunctor::operator()(QAbstractOAuth::Stage stage,
                                             QMultiMap<QString, QVariant>* dictPointer)
{
    auto *callable = object();
    if (!PyCallable_Check(callable)) {
        qWarning("Argument 1 of setModifyParametersFunction() must be a callable.");
        return;
    }
    Shiboken::GilState state;
    QMultiMap<QString, QVariant> dict = *dictPointer;
    Shiboken::AutoDecRef arglist(PyTuple_New(2));
    PyTuple_SetItem(arglist, 0, %CONVERTTOPYTHON[QAbstractOAuth::Stage](stage));
    PyTuple_SetItem(arglist, 1, %CONVERTTOPYTHON[QMultiMap<QString, QVariant>](dict));
    Shiboken::AutoDecRef ret(PyObject_CallObject(callable, arglist));

    if (!ret.isNull() && PyDict_Check(ret.object()) != 0) {
        PyObject *key{};
        PyObject *value{};
        Py_ssize_t pos = 0;
        // The conversions in the body run Python, so the walk takes a
        // snapshot on a free-threaded build; with a GIL it walks the dict.
#ifdef Py_GIL_DISABLED
        Shiboken::AutoDecRef items(PepDict_IterationSnapshot(ret.object()));
        while (!items.isNull() && PyDict_Next(items.object(), &pos, &key, &value)) {
#else
        while (PyDict_Next(ret.object(), &pos, &key, &value)) {
#endif
            QString cppKey = %CONVERTTOCPP[QString](key);
            QVariant cppValue = %CONVERTTOCPP[QVariant](value);
            dictPointer->replace(cppKey, cppValue);
        }
    }
}
// @snippet qabstractoauth-lookuphost-functor

// @snippet qabstractoauth-setmodifyparametersfunction
%CPPSELF.%FUNCTION_NAME(QAbstractOAuthModifyFunctor(%PYARG_1));
// @snippet qabstractoauth-setmodifyparametersfunction
