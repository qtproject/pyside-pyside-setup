// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QtWidgets/QMainWindow>

QT_FORWARD_DECLARE_CLASS(QPlainTextEdit)

class MainWindow : public QMainWindow
{
    Q_OBJECT
public:
    MainWindow();

    void testFunction1();

    static constexpr auto TEST = QLatin1StringView("test");

private Q_SLOTS:
    void slotRunScript();
    void slotPrintDiagnostics();

private:
    void runScript(const QString &);

    QPlainTextEdit *m_scriptEdit;
};

#endif // MAINWINDOW_H
