/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:COMM$
**
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** $QT_END_LICENSE$
**
****************************************************************************/

#ifndef REPORTHANDLER_H
#define REPORTHANDLER_H

#include <QLoggingCategory>
#include <QString>

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
