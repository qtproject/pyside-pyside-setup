// Copyright (C) 2024 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#include "webenginepage_functors.h"

#include "autodecref.h"
#include "gilstate.h"
#include "sbkconverter.h"

#include "pysidevariantutils.h"

#include <QtCore/qbytearray.h>
#include <QtCore/qvariant.h>

QT_BEGIN_NAMESPACE

void RunJavascriptFunctor::operator()(const QVariant &result)
{
    Shiboken::GilState state;
    Shiboken::AutoDecRef arglist(PyTuple_Pack(1, PySide::Variant::javascriptVariantToPython(result)));
    Shiboken::AutoDecRef ret(PyObject_CallObject(object(), arglist));
    release(); // single shot
}

void PrintToPdfFunctor::operator()(const QByteArray &pdf)
{
    Shiboken::GilState state;
    Shiboken::AutoDecRef arglist(PyTuple_New(1));

    Shiboken::Conversions::SpecificConverter converter("QByteArray");
    PyObject *pyPdf = converter.toPython(&pdf);
    PyTuple_SetItem(arglist, 0, pyPdf);
    Shiboken::AutoDecRef ret(PyObject_CallObject(object(), arglist));
    release(); // single shot
}

QT_END_NAMESPACE
