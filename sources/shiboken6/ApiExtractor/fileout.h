// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef FILEOUT_H
#define FILEOUT_H

#include "textstream.h"

class Exception;

QT_FORWARD_DECLARE_CLASS(QFile)

class FileOut
{
    QByteArray m_buffer;
public:
    Q_DISABLE_COPY(FileOut)

    enum State { Unchanged, Success };

    explicit FileOut(QString name);
    ~FileOut();

    QString filePath() const { return m_name; }

    State done() noexcept(false);

    TextStream stream;

    static bool diff() { return m_diff; }
    static void setDiff(bool diff) { m_diff = diff; }

    static bool dryRun() { return m_dryRun; }
    static void setDryRun(bool dryRun) { m_dryRun = dryRun; }

private:
    QString m_name;
    bool m_isDone;
    static bool m_dryRun;
    static bool m_diff;
};

#endif // FILEOUT_H
