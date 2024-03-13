// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

#include "mainwindow.h"
#include "pythonutils.h"

#include <QtWidgets/QApplication>
#include <QtWidgets/QMenu>
#include <QtWidgets/QMenuBar>
#include <QtWidgets/QPlainTextEdit>
#include <QtWidgets/QStatusBar>
#include <QtWidgets/QToolBar>
#include <QtWidgets/QVBoxLayout>

#include <QtGui/QAction>
#include <QtGui/QFontDatabase>
#include <QtGui/QIcon>

#include <QtCore/QDebug>
#include <QtCore/QTextStream>

using namespace Qt::StringLiterals;

static const auto defaultScript = R"(import AppLib
print("Hello, world")
mainWindow.testFunction1()
)"_L1;

MainWindow::MainWindow()
    : m_scriptEdit(new QPlainTextEdit(defaultScript, this))
{
    setWindowTitle(tr("Scriptable Application"));

    auto  *fileMenu = menuBar()->addMenu(tr("&File"));
    const QIcon runIcon = QIcon::fromTheme("system-run"_L1);
    auto *runAction = fileMenu->addAction(runIcon, tr("&Run..."),
                                          this, &MainWindow::slotRunScript);
    runAction->setShortcut(Qt::CTRL | Qt::Key_R);
    auto *diagnosticAction = fileMenu->addAction(tr("&Print Diagnostics"),
                                                 this, &MainWindow::slotPrintDiagnostics);
    diagnosticAction->setShortcut(Qt::CTRL | Qt::Key_D);
    fileMenu->addAction(tr("&Invoke testFunction1()"),
                        this, &MainWindow::testFunction1);
    const QIcon quitIcon = QIcon::fromTheme(QIcon::ThemeIcon::ApplicationExit);
    auto *quitAction = fileMenu->addAction(quitIcon, tr("&Quit"),
                                           qApp, &QCoreApplication::quit);
    quitAction->setShortcut(Qt::CTRL | Qt::Key_Q);

    auto *editMenu = menuBar()->addMenu(tr("&Edit"));
    const QIcon clearIcon = QIcon::fromTheme(QIcon::ThemeIcon::EditClear);
    auto *clearAction = editMenu->addAction(clearIcon, tr("&Clear"),
                                            m_scriptEdit, &QPlainTextEdit::clear);

    auto *helpMenu = menuBar()->addMenu(tr("&Help"));
    const QIcon aboutIcon = QIcon::fromTheme(QIcon::ThemeIcon::HelpAbout);
    auto *aboutAction = helpMenu->addAction(aboutIcon, tr("&About Qt"),
                                            qApp, &QApplication::aboutQt);

    auto *toolBar = new QToolBar;
    addToolBar(toolBar);
    toolBar->addAction(quitAction);
    toolBar->addSeparator();
    toolBar->addAction(clearAction);
    toolBar->addSeparator();
    toolBar->addAction(runAction);
    toolBar->addSeparator();
    toolBar->addAction(aboutAction);

    m_scriptEdit->setFont(QFontDatabase::systemFont(QFontDatabase::FixedFont));
    setCentralWidget(m_scriptEdit);

    if (!PythonUtils::bindAppObject("__main__"_L1, "mainWindow"_L1,
                                    PythonUtils::MainWindowType, this)) {
       statusBar()->showMessage(tr("Error loading the application module"));
    }
}

void MainWindow::slotRunScript()
{
    const QString text = m_scriptEdit->toPlainText().trimmed();
    if (!text.isEmpty())
        runScript(text);
}

void MainWindow::slotPrintDiagnostics()
{
    const QString script = R"P(import sys
print('Path=', sys.path)
print('Executable=', sys.executable)
)P"_L1;
    runScript(script);
}

void MainWindow::runScript(const QString &script)
{
    if (!::PythonUtils::runScript(script))
        statusBar()->showMessage(tr("Error running script"));
}

void MainWindow::testFunction1()
{
    static int n = 1;
    QString message;
    QTextStream(&message) << __FUNCTION__ << " called #" << n++;
    qDebug().noquote() << message;
    statusBar()->showMessage(message);
}
