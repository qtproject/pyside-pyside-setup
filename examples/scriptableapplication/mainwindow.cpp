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

static const char defaultScript[] = R"(
import AppLib
print("Hello, world")
mainWindow.testFunction1()
)";

MainWindow::MainWindow()
    : m_scriptEdit(new QPlainTextEdit(QString::fromLatin1(defaultScript).trimmed(), this))
{
    setWindowTitle(tr("Scriptable Application"));

    QMenu *fileMenu = menuBar()->addMenu(tr("&File"));
    const QIcon runIcon = QIcon::fromTheme(QStringLiteral("system-run"));
    QAction *runAction = fileMenu->addAction(runIcon, tr("&Run..."), this, &MainWindow::slotRunScript);
    runAction->setShortcut(Qt::CTRL | Qt::Key_R);
    QAction *diagnosticAction = fileMenu->addAction(tr("&Print Diagnostics"), this, &MainWindow::slotPrintDiagnostics);
    diagnosticAction->setShortcut(Qt::CTRL | Qt::Key_D);
    fileMenu->addAction(tr("&Invoke testFunction1()"), this, &MainWindow::testFunction1);
    const QIcon quitIcon = QIcon::fromTheme(QStringLiteral("application-exit"));
    QAction *quitAction = fileMenu->addAction(quitIcon, tr("&Quit"), qApp, &QCoreApplication::quit);
    quitAction->setShortcut(Qt::CTRL | Qt::Key_Q);

    QMenu *editMenu = menuBar()->addMenu(tr("&Edit"));
    const QIcon clearIcon = QIcon::fromTheme(QStringLiteral("edit-clear"));
    QAction *clearAction = editMenu->addAction(clearIcon, tr("&Clear"), m_scriptEdit, &QPlainTextEdit::clear);

    QMenu *helpMenu = menuBar()->addMenu(tr("&Help"));
    const QIcon aboutIcon = QIcon::fromTheme(QStringLiteral("help-about"));
    QAction *aboutAction = helpMenu->addAction(aboutIcon, tr("&About Qt"), qApp, &QApplication::aboutQt);

    QToolBar *toolBar = new QToolBar;
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

    if (!PythonUtils::bindAppObject("__main__", "mainWindow", PythonUtils::MainWindowType, this))
       statusBar()->showMessage(tr("Error loading the application module"));
}

void MainWindow::slotRunScript()
{
    const QString text = m_scriptEdit->toPlainText().trimmed();
    const QStringList script = text.split(u'\n', Qt::SkipEmptyParts);
    if (!script.isEmpty())
        runScript(script);
}

void MainWindow::slotPrintDiagnostics()
{
    const QStringList script = QStringList()
            << "import sys" << "print('Path=', sys.path)" << "print('Executable=', sys.executable)";
    runScript(script);
}

void MainWindow::runScript(const QStringList &script)
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
