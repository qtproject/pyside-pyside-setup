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

#include "fileout.h"
#include "messages.h"
#include "reporthandler.h"
#include "exception.h"

#include <QtCore/QFileInfo>
#include <QtCore/QDir>
#include <QtCore/QDebug>

#include <cstdio>

bool FileOut::m_dryRun = false;
bool FileOut::m_diff = false;

#ifdef Q_OS_LINUX
static const char colorDelete[] = "\033[31m";
static const char colorAdd[] = "\033[32m";
static const char colorInfo[] = "\033[36m";
static const char colorReset[] = "\033[0m";
#else
static const char colorDelete[] = "";
static const char colorAdd[] = "";
static const char colorInfo[] = "";
static const char colorReset[] = "";
#endif

FileOut::FileOut(QString n) :
    stream(&m_buffer),
    m_name(std::move(n)),
    m_isDone(false)
{
}

FileOut::~FileOut()
{
    if (!m_isDone) {
        qCWarning(lcShiboken).noquote().nospace() << __FUNCTION__
            << " file " << m_name << " not written.";
    }
}

static QList<int> lcsLength(const QByteArrayList &a, const QByteArrayList &b)
{
    const int height = a.size() + 1;
    const int width = b.size() + 1;

    QList<int> res(width * height, 0);

    for (int row = 1; row < height; row++) {
        for (int col = 1; col < width; col++) {
            if (a[row-1] == b[col-1])
                res[width * row + col] = res[width * (row-1) + col-1] + 1;
            else
                res[width * row + col] = qMax(res[width * row     + col-1],
                                              res[width * (row-1) + col]);
        }
    }
    return res;
}

enum Type {
    Add,
    Delete,
    Unchanged
};

struct Unit
{
    Type type;
    int start;
    int end;

    void print(const QByteArrayList &a, const QByteArrayList &b) const;
};

void Unit::print(const QByteArrayList &a, const QByteArrayList &b) const
{
    switch (type) {
    case Unchanged:
        if ((end - start) > 9) {
            for (int i = start; i <= start + 2; i++)
                std::printf("  %s\n", a.at(i).constData());
            std::printf("%s=\n= %d more lines\n=%s\n",
                        colorInfo, end - start - 6, colorReset);
            for (int i = end - 2; i <= end; i++)
                std::printf("  %s\n", a.at(i).constData());
        } else {
            for (int i = start; i <= end; i++)
                std::printf("  %s\n", a.at(i).constData());
        }
        break;
    case Add:
        std::fputs(colorAdd, stdout);
        for (int i = start; i <= end; i++)
            std::printf("+ %s\n", b.at(i).constData());
        std::fputs(colorReset, stdout);
        break;
    case Delete:
        std::fputs(colorDelete, stdout);
        for (int i = start; i <= end; i++)
            std::printf("- %s\n", a.at(i).constData());
        std::fputs(colorReset, stdout);
        break;
    }
}

static void unitAppend(Type type, int pos, QList<Unit> *units)
{
    if (!units->isEmpty() && units->last().type == type)
        units->last().end = pos;
    else
        units->append(Unit{type, pos, pos});
}

static QList<Unit> diffHelper(const QList<int> &lcs,
                                const QByteArrayList &a, const QByteArrayList &b,
                                int row, int col)
{
    if (row > 0 && col > 0 && a.at(row - 1) == b.at(col - 1)) {
        QList<Unit> result = diffHelper(lcs, a, b, row - 1, col - 1);
        unitAppend(Unchanged, row - 1, &result);
        return result;
    }

    const int width = b.size() + 1;
    if (col > 0
        && (row == 0 || lcs.at(width * row + col -1 ) >= lcs.at(width * (row - 1) + col))) {
        QList<Unit> result = diffHelper(lcs, a, b, row, col - 1);
        unitAppend(Add, col - 1, &result);
        return result;
    }
    if (row > 0
        && (col == 0 || lcs.at(width * row + col-1) < lcs.at(width * (row - 1) + col))) {
        QList<Unit> result = diffHelper(lcs, a, b, row - 1, col);
        unitAppend(Delete, row - 1, &result);
        return result;
    }
    return {};
}

static void diff(const QByteArrayList &a, const QByteArrayList &b)
{
    const QList<Unit> res = diffHelper(lcsLength(a, b), a, b, a.size(), b.size());
    for (const Unit &unit : res)
        unit.print(a, b);
}

FileOut::State FileOut::done()
{
    if (m_isDone)
        return Success;

    bool fileEqual = false;
    QFile fileRead(m_name);
    QFileInfo info(fileRead);
    stream.flush();
    QByteArray original;
    if (info.exists() && (m_diff || (info.size() == m_buffer.size()))) {
        if (!fileRead.open(QIODevice::ReadOnly))
            throw Exception(msgCannotOpenForReading(fileRead));

        original = fileRead.readAll();
        fileRead.close();
        fileEqual = (original == m_buffer);
    }

    if (fileEqual) {
        m_isDone = true;
        return Unchanged;
    }

    if (!FileOut::m_dryRun) {
        QDir dir(info.absolutePath());
        if (!dir.mkpath(dir.absolutePath())) {
            const QString message = QStringLiteral("Unable to create directory '%1'")
                                        .arg(QDir::toNativeSeparators(dir.absolutePath()));
            throw Exception(message);
        }

        QFile fileWrite(m_name);
        if (!fileWrite.open(QIODevice::WriteOnly))
            throw Exception(msgCannotOpenForWriting(fileWrite));
        if (fileWrite.write(m_buffer) == -1 || !fileWrite.flush())
            throw Exception(msgWriteFailed(fileWrite, m_buffer.size()));
    }
    if (m_diff) {
        std::printf("%sFile: %s%s\n", colorInfo, qPrintable(m_name), colorReset);
        ::diff(original.split('\n'), m_buffer.split('\n'));
        std::printf("\n");
    }

    m_isDone = true;

    return Success;
}
