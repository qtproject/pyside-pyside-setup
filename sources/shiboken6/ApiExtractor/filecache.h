// Copyright (C) 2025 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef FILECACHE_H
#define FILECACHE_H

#include <QtCore/qlist.h>
#include <QtCore/qstring.h>
#include <QtCore/qstringview.h>

#include <optional>

QT_FORWARD_DECLARE_CLASS(QRegularExpression)
QT_FORWARD_DECLARE_CLASS(QDebug)

// Queue-based cache for the contents of a number of recent files with a
// convenience API for retrieving lines and regexp-delimited snippets.
class FileCache
{
public:
    using Lines = QList<QStringView>;

    std::optional<QString> fileContents(const QString &name);
    std::optional<Lines> lines(const QString &name);
    std::optional<QString> fileSnippet(const QString &name,
                                       const QString &snippetName,
                                       const QRegularExpression &snippetPattern);

    const QString &errorString() const { return m_error; }

    void formatDebug(QDebug &debug) const;

private:
    struct FileCacheEntry
    {
        QString name;
        QString contents;
        Lines lines;
    };

    qsizetype ensureEntry(const QString &name);
    qsizetype indexOf(const QString &name) const;
    static void ensureLines(FileCacheEntry *entry);

    QList<FileCacheEntry> m_cache;
    QString m_error;
    int m_hits = 0;
    int m_misses = 0;
};

QDebug operator<<(QDebug debug, const FileCache &c);

#endif // FILECACHE_H
