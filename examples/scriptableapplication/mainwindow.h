// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QtWidgets/QMainWindow>

class QPlainTextEdit;

class MainWindow : public QMainWindow
{
    Q_OBJECT
public:
    MainWindow();

    void testFunction1();

private Q_SLOTS:
    void slotRunScript();
    void slotPrintDiagnostics();

private:
    void runScript(const QStringList &);

    QPlainTextEdit *m_scriptEdit;
};

#endif // MAINWINDOW_H
