// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

#include "mainwindow.h"

#include <QApplication>
#include <QScreen>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    MainWindow mainWindow;
    const QRect availableGeometry =  mainWindow.screen()->availableGeometry();
    mainWindow.resize(availableGeometry.width() / 2, availableGeometry.height() / 2);
    mainWindow.show();
    return a.exec();
}
