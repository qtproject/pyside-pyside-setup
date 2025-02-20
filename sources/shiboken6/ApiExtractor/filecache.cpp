// Copyright (C) 2025 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "filecache.h"

#include <QtCore/QDebug>
#include <QtCore/QDir>
#include <QtCore/QFile>
#include <QtCore/QRegularExpression>

#include <algorithm>

using namespace Qt::StringLiterals;

constexpr qsizetype MAX_CACHE_SIZE = 20;

static QString msgCannotFindSnippet(const QString &file, const QString &snippetLabel)
{
    return "Cannot find snippet \""_L1  + snippetLabel + "\" in \""_L1
           + QDir::toNativeSeparators(file) + "\"."_L1;
}

static QString msgUnterminatedSnippet(const QString &file, const QString &snippetLabel)
{
    return "Snippet \""_L1  + snippetLabel + "\" in \""_L1
           + QDir::toNativeSeparators(file) + "\ is not terminated."_L1;
}

static QString msgCannotOpenFileForReading(const QFile &f)
{
    return "Failed to open file \""_L1 + QDir::toNativeSeparators(f.fileName())
           + "\" for reading: "_L1 +f.errorString();
}

std::optional<QString> FileCache::fileContents(const QString &name)
{
    const qsizetype index = ensureEntry(name);
    if (index == -1)
        return std::nullopt;
    return m_cache.at(index).contents;
}

void FileCache::ensureLines(FileCacheEntry *entry)
{
    if (entry->lines.isEmpty())
        entry->lines = QStringView{entry->contents}.split(u'\n');
}

std::optional<FileCache::Lines> FileCache::lines(const QString &name)
{
    const qsizetype index = ensureEntry(name);
    if (index == -1)
        return std::nullopt;
    FileCacheEntry &entry = m_cache[index];
    ensureLines(&entry);
    return entry.lines;
}

std::optional<QString> FileCache::fileSnippet(const QString &name,
                                              const QString &snippetName,
                                              const QRegularExpression &snippetPattern)
{
    const qsizetype index = ensureEntry(name);
    if (index == -1)
        return std::nullopt;
    FileCacheEntry &entry = m_cache[index];
    ensureLines(&entry);

    // Check for a comment line and the snippet ID
    auto pred = [&snippetPattern](QStringView line) {
        return (line.contains(u'/') || line.contains(u'#'))
               && snippetPattern.matchView(line).hasMatch(); };

    const auto end = entry.lines.cend();
    const auto i1 = std::find_if(entry.lines.cbegin(), end, pred);
    if (i1 == end) {
        m_error = msgCannotFindSnippet(name, snippetName);
        return std::nullopt;
    }

    auto pos = i1;
    const auto i2 = std::find_if(++pos, end, pred);
    if (i2 == end) {
        m_error = msgUnterminatedSnippet(name, snippetName);
        return std::nullopt;
    }

    const QChar *startSnippet = i1->constData() + i1->size() + 1;
    const auto snippetSize = i2->constData() - startSnippet;
    const auto startSnippetIndex = startSnippet - entry.lines.cbegin()->constData();
    return entry.contents.sliced(startSnippetIndex, snippetSize);
}

qsizetype FileCache::ensureEntry(const QString &name)
{
    const qsizetype index = indexOf(name);
    if (index != -1) {
        ++m_hits;
        return index;
    }

    ++m_misses;
    m_error.clear();
    QFile file(name);
    if (!file.open(QIODevice::Text | QIODevice::ReadOnly)) {
        m_error = msgCannotOpenFileForReading(file);
        return -1;
    }

    QString contents = QString::fromUtf8(file.readAll());
    m_cache.prepend({name, contents, {}});
    while (m_cache.size() >= MAX_CACHE_SIZE)
        m_cache.removeLast();
    return 0;
}

qsizetype FileCache::indexOf(const QString &name) const
{
    for (qsizetype i = 0, size = m_cache.size(); i < size; ++i) {
        if (m_cache.at(i).name == name)
            return i;
    }
    return -1;
}

void FileCache::formatDebug(QDebug &debug) const
{
    debug << "FileCache(" << m_cache.size() << " entries, "
          << m_hits << " hits, " << m_misses << " misses [";
    for (const auto &e : m_cache)
        debug << QDir::toNativeSeparators(e.name) << ' ' << e.contents.size() << "B ";
    debug << "])";
}

QDebug operator<<(QDebug debug, const FileCache &c)
{
    QDebugStateSaver saver(debug);
    debug.noquote();
    debug.nospace();
    c.formatDebug(debug);
    return debug;
}
