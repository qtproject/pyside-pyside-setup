// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef REPORTHANDLER_H
#define REPORTHANDLER_H

#include <QtCore/QLoggingCategory>
#include <QtCore/QString>

Q_DECLARE_LOGGING_CATEGORY(lcShiboken)
Q_DECLARE_LOGGING_CATEGORY(lcShibokenDoc)

class ReportHandler
{
public:
    enum DebugLevel { NoDebug, SparseDebug, MediumDebug, FullDebug };

    static void install();
    static void startTimer();

    static DebugLevel debugLevel();
    static void setDebugLevel(DebugLevel level);
    static bool setDebugLevelFromArg(const QString &);

    static int warningCount();

    static int suppressedCount();

    static void startProgress(const QByteArray &str);
    static void endProgress();

    static bool isDebug(DebugLevel level)
    { return debugLevel() >= level; }

    static bool isSilent();
    static void setSilent(bool silent);

    static void setPrefix(const QString &p);

    static QByteArray doneMessage();

private:
    static void messageOutput(QtMsgType type, const QMessageLogContext &context, const QString &msg);
};

#endif // REPORTHANDLER_H
