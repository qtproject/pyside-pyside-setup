/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:GPL-EXCEPT$
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** GNU General Public License Usage
** Alternatively, this file may be used under the terms of the GNU
** General Public License version 3 as published by the Free Software
** Foundation with exceptions as appearing in the file LICENSE.GPL3-EXCEPT
** included in the packaging of this file. Please review the following
** information to ensure the GNU General Public License requirements will
** be met: https://www.gnu.org/licenses/gpl-3.0.html.
**
** $QT_END_LICENSE$
**
****************************************************************************/

#include "dotview.h"

#include <QtCore/QDebug>
#include <QtCore/QDir>
#include <QtCore/QFile>
#include <QtCore/QProcess>
#include <QtCore/QTemporaryFile>

bool showDotGraph(const QString &name, const QString &graph)
{
    const QString imageType = u"jpg"_qs;

    // Write out the graph to a temporary file
    QTemporaryFile dotFile(QDir::tempPath() + u'/' + name + u"_XXXXXX.dot"_qs);
    if (!dotFile.open()) {
        qWarning("Cannot open temporary file: %s", qPrintable(dotFile.errorString()));
        return false;
    }
    const QString tempDotFile = dotFile.fileName();
    dotFile.write(graph.toUtf8());
    dotFile.close();

    // Convert to image using "dot"
    const QString imageFile = tempDotFile.left(tempDotFile.size() - 3) + imageType;
    QProcess process;
    process.start(u"dot"_qs, {u"-T"_qs + imageType, u"-o"_qs + imageFile, tempDotFile});
    if (!process.waitForStarted() || !process.waitForFinished()) {
        qWarning("Image conversion failed: %s", qPrintable(process.errorString()));
        return false;
    }
    if (process.exitStatus() != QProcess::NormalExit || process.exitCode() != 0) {
        qWarning("Image conversion failed (%d): %s",
                 process.exitCode(),
                 process.readAllStandardError().constData());
        return false;
    }

    // Launch image. Should use QDesktopServices::openUrl(),
    // but we don't link against QtGui
#ifdef Q_OS_UNIX
    const QString imageViewer = u"gwenview"_qs;
#else
    const QString imageViewer = u"mspaint"_qs;
#endif
    if (!QProcess::startDetached(imageViewer, {imageFile})) {
        qWarning("Failed to launch viewer: %s", qPrintable(imageViewer));
        return false;
    }
    qInfo().noquote().nospace() << "Viewing: "
        << QDir::toNativeSeparators(tempDotFile)
        << ' ' << QDir::toNativeSeparators(imageFile);
    return true;
}
