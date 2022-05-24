// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef CLANGPARSER_H
#define CLANGPARSER_H

#include <clang-c/Index.h>

#include <QtCore/QByteArrayList>
#include <QtCore/QHash>
#include <QtCore/QPair>
#include <QtCore/QString>
#include <QtCore/QList>

#include <string_view>

namespace clang {

struct Diagnostic;

class SourceFileCache {
public:
    std::string_view getCodeSnippet(const CXCursor &cursor, QString *errorMessage = nullptr);
    QString getFileName(CXFile file);

private:
    using FileBufferCache = QHash<CXFile, QByteArray>;
    using FileNameCache = QHash<CXFile, QString>;

    FileBufferCache m_fileBufferCache;
    FileNameCache m_fileNameCache;
};

enum class LocationType
{
    Main, // Main header parsed for bindings
    Other, // A header parsed for bindings
    System,  // A system header
    Unknown  // Clang internal
};

class BaseVisitor {
    Q_DISABLE_COPY(BaseVisitor)
public:
    using Diagnostics = QList<Diagnostic>;

    enum StartTokenResult { Error, Skip, Recurse };

    BaseVisitor();
    virtual ~BaseVisitor();

    // Whether location should be visited.
    // defaults to clang_Location_isFromMainFile()
    virtual bool visitLocation(const QString &fileName, LocationType locationType) const;

    virtual StartTokenResult startToken(const CXCursor &cursor) = 0;
    virtual bool endToken(const CXCursor &cursor) = 0;

    StartTokenResult cbHandleStartToken(const CXCursor &cursor);
    bool cbHandleEndToken(const CXCursor &cursor, StartTokenResult startResult);

    QString getFileName(CXFile file) { return m_fileCache.getFileName(file); }
    std::string_view getCodeSnippet(const CXCursor &cursor);
    QString getCodeSnippetString(const CXCursor &cursor);

    Diagnostics diagnostics() const;
    void setDiagnostics(const Diagnostics &d);
    void appendDiagnostic(const Diagnostic &d);

    // For usage by the parser
    bool _handleVisitLocation( const CXSourceLocation &location);

private:
    SourceFileCache m_fileCache;
    Diagnostics m_diagnostics;
    CXFile m_currentCxFile{};
    bool m_visitCurrent = true;
};

bool parse(const QByteArrayList  &clangArgs,
           bool addCompilerSupportArguments,
           unsigned clangFlags, BaseVisitor &ctx);

} // namespace clang

#endif // !CLANGPARSER_H
