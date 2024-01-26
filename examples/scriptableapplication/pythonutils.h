// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

#ifndef PYTHONUTILS_H
#define PYTHONUTILS_H

#include <QtCore/QStringList>

QT_FORWARD_DECLARE_CLASS(QObject)

namespace PythonUtils {

enum AppLibTypes
{
    MainWindowType = 0 // SBK_MAINWINDOW_IDX
};

enum State
{
    PythonUninitialized,
    PythonInitialized,
    AppModuleLoaded
};

State init();

bool bindAppObject(const QString &moduleName, const QString &name,
                   int index, QObject *o);

bool runScript(const QString &script);

} // namespace PythonUtils

#endif // PYTHONUTILS_H
