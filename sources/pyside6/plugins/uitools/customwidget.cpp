// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include "customwidget.h"
#include <QtCore/qdebug.h>

// Part of the static plugin linked to the QtUiLoader Python module,
// allowing it to create a custom widget written in Python.
PyCustomWidget::PyCustomWidget(PyObject *objectType) :
    m_pyObject(objectType),
    m_name(QString::fromUtf8(reinterpret_cast<PyTypeObject *>(objectType)->tp_name))
{
}

bool PyCustomWidget::isContainer() const
{
    return false;
}

bool PyCustomWidget::isInitialized() const
{
    return m_initialized;
}

QIcon PyCustomWidget::icon() const
{
    return QIcon();
}

QString PyCustomWidget::domXml() const
{
    return QString();
}

QString PyCustomWidget::group() const
{
    return QString();
}

QString PyCustomWidget::includeFile() const
{
    return QString();
}

QString PyCustomWidget::name() const
{
    return m_name;
}

QString PyCustomWidget::toolTip() const
{
    return QString();
}

QString PyCustomWidget::whatsThis() const
{
    return QString();
}

// A copy of this code exists in PyDesignerCustomWidget::createWidget()
// (see sources/pyside6/PySide6/QtDesigner/qpydesignercustomwidgetcollection.cpp).
QWidget *PyCustomWidget::createWidget(QWidget *parent)
{
    // Create a python instance and return cpp object
    PyObject *pyParent = nullptr;
    bool unknownParent = false;
    if (parent) {
        pyParent = reinterpret_cast<PyObject *>(Shiboken::BindingManager::instance().retrieveWrapper(parent));
        if (pyParent) {
            Py_INCREF(pyParent);
        } else {
            static Shiboken::Conversions::SpecificConverter converter("QWidget*");
            pyParent = converter.toPython(&parent);
            unknownParent = true;
        }
    } else {
        Py_INCREF(Py_None);
        pyParent = Py_None;
    }

    Shiboken::AutoDecRef pyArgs(PyTuple_New(1));
    PyTuple_SET_ITEM(pyArgs, 0, pyParent); // tuple will keep pyParent reference

    // Call python constructor
    auto result = reinterpret_cast<SbkObject *>(PyObject_CallObject(m_pyObject, pyArgs));
    if (!result) {
        qWarning("Unable to create a Python custom widget of type \"%s\".",
                 qPrintable(m_name));
        PyErr_Print();
        return nullptr;
    }

    if (unknownParent) // if parent does not exist in python, transfer the ownership to cpp
        Shiboken::Object::releaseOwnership(result);
    else
        Shiboken::Object::setParent(pyParent, reinterpret_cast<PyObject *>(result));

    return reinterpret_cast<QWidget *>(Shiboken::Object::cppPointer(result, Py_TYPE(result)));
}

void PyCustomWidget::initialize(QDesignerFormEditorInterface *)
{
    m_initialized = true;
}
