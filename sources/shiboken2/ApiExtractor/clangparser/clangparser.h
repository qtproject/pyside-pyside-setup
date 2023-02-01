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

#ifndef CLANGPARSER_H
#define CLANGPARSER_H

#include <clang-c/Index.h>

#include <QtCore/QByteArrayList>
#include <QtCore/QHash>
#include <QtCore/QPair>
#include <QtCore/QString>
#include <QtCore/QVector>

namespace clang {

struct Diagnostic;

class SourceFileCache {
public:
    using Snippet = QPair<const char *, const char *>;

    Snippet getCodeSnippet(const CXCursor &cursor, QString *errorMessage = nullptr);
    QString getFileName(CXFile file);

private:
    using FileBufferCache = QHash<CXFile, QByteArray>;
    using FileNameCache = QHash<CXFile, QString>;

    FileBufferCache m_fileBufferCache;
    FileNameCache m_fileNameCache;
};

class BaseVisitor {
    Q_DISABLE_COPY(BaseVisitor)
public:
    using Diagnostics = QVector<Diagnostic>;
    using CodeSnippet = SourceFileCache::Snippet;

    enum StartTokenResult { Error, Skip, Recurse };

    BaseVisitor();
    virtual ~BaseVisitor();

    // Whether location should be visited.
    // defaults to clang_Location_isFromMainFile()
    virtual bool visitLocation(const CXSourceLocation &location) const;

    virtual StartTokenResult startToken(const CXCursor &cursor) = 0;
    virtual bool endToken(const CXCursor &cursor) = 0;

    StartTokenResult cbHandleStartToken(const CXCursor &cursor);
    bool cbHandleEndToken(const CXCursor &cursor, StartTokenResult startResult);

    QString getFileName(CXFile file) { return m_fileCache.getFileName(file); }

    CodeSnippet getCodeSnippet(const CXCursor &cursor);
    QString getCodeSnippetString(const CXCursor &cursor);

    Diagnostics diagnostics() const;
    void setDiagnostics(const Diagnostics &d);
    void appendDiagnostic(const Diagnostic &d);

private:
    SourceFileCache m_fileCache;
    Diagnostics m_diagnostics;
};

bool parse(const QByteArrayList  &clangArgs, unsigned clangFlags, BaseVisitor &ctx);

} // namespace clang

#endif // !CLANGPARSER_H
