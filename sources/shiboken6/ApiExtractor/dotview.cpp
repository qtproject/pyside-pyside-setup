// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "dotview.h"

#include <QtCore/QDebug>
#include <QtCore/QDir>
#include <QtCore/QFile>
#include <QtCore/QProcess>
#include <QtCore/QTemporaryFile>

using namespace Qt::StringLiterals;

bool showDotGraph(const QString &name, const QString &graph)
{
    const QString imageType = u"jpg"_s;

    // Write out the graph to a temporary file
    QTemporaryFile dotFile(QDir::tempPath() + u'/' + name + u"_XXXXXX.dot"_s);
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
    process.start(u"dot"_s, {u"-T"_s + imageType, u"-o"_s + imageFile, tempDotFile});
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
    const QString imageViewer = u"gwenview"_s;
#else
    const QString imageViewer = u"mspaint"_s;
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
