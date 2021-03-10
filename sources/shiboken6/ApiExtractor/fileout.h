/****************************************************************************
**
** Copyright (C) 2016 The Qt Company Ltd.
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

#ifndef FILEOUT_H
#define FILEOUT_H

#include "textstream.h"

QT_FORWARD_DECLARE_CLASS(QFile)

class FileOut
{
    QByteArray m_buffer;
public:
    Q_DISABLE_COPY(FileOut)

    enum State { Failure, Unchanged, Success };

    explicit FileOut(QString name);
    ~FileOut();

    QString filePath() const { return m_name; }

    State done();
    State done(QString *errorMessage);

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
