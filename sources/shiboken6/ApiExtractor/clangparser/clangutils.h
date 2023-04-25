// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef CLANGUTILS_H
#define CLANGUTILS_H

#include <clang-c/Index.h>
#include <QtCore/QPair>
#include <QtCore/QString>
#include <QtCore/QStringList>
#include <QtCore/QList>

#include <functional>

QT_FORWARD_DECLARE_CLASS(QDebug)

bool operator==(const CXCursor &c1, const CXCursor &c2);
size_t qHash(const CXCursor &c, size_t seed = 0);

bool operator==(const CXType &t1, const CXType &t2);
size_t qHash(const CXType &ct, size_t seed);

namespace clang {

QString getCursorKindName(CXCursorKind cursorKind);
QString getCursorSpelling(const CXCursor &cursor);
QString getCursorDisplayName(const CXCursor &cursor);
QString getTypeName(const CXType &type);
QString getResolvedTypeName(const CXType &type);
inline QString getCursorTypeName(const CXCursor &cursor)
    { return getTypeName(clang_getCursorType(cursor)); }
inline QString getCursorResultTypeName(const CXCursor &cursor)
    { return getTypeName(clang_getCursorResultType(cursor)); }

inline bool isCursorValid(const CXCursor &c)
{
    return c.kind < CXCursor_FirstInvalid || c.kind >  CXCursor_LastInvalid;
}

QString getFileName(CXFile file); // Uncached,see BaseVisitor for a cached version

struct SourceLocation
{
    bool equals(const SourceLocation &rhs) const;

    CXFile file = nullptr;
    unsigned line = 0;
    unsigned column = 0;
    unsigned offset = 0;
};

inline bool operator==(const SourceLocation &l1, const SourceLocation &l2)
{ return l1.equals(l2); }

inline bool operator!=(const SourceLocation &l1, const SourceLocation &l2)
{ return !l1.equals(l2); }

SourceLocation getExpansionLocation(const CXSourceLocation &location);

using SourceRange =QPair<SourceLocation, SourceLocation>;

SourceLocation getCursorLocation(const CXCursor &cursor);
CXString getFileNameFromLocation(const CXSourceLocation &location);
SourceRange getCursorRange(const CXCursor &cursor);

struct Diagnostic {
    enum  Source { Clang, Other };

    Diagnostic() = default;
    // Clang
    static Diagnostic fromCXDiagnostic(CXDiagnostic cd);
    // Other
    explicit Diagnostic(const QString &m, const CXCursor &c, CXDiagnosticSeverity s = CXDiagnostic_Warning);
    void setLocation(const SourceLocation &);

    QString message;
    QStringList childMessages;
    QString file;
    unsigned line = 0;
    unsigned column = 0;
    unsigned offset = 0;
    Source source = Clang;
    CXDiagnosticSeverity severity = CXDiagnostic_Warning;
};

QList<Diagnostic> getDiagnostics(CXTranslationUnit tu);
CXDiagnosticSeverity maxSeverity(const QList<Diagnostic> &ds);

// Parse a template argument list "a<b<c,d>,e>" and invoke a handler
// with each match (level and string). Return begin and end of the list.
using TemplateArgumentHandler = std::function<void (int, QStringView)>;

QPair<qsizetype, qsizetype>
    parseTemplateArgumentList(const QString &l,
                              const TemplateArgumentHandler &handler,
                              qsizetype from = 0);

#ifndef QT_NO_DEBUG_STREAM
QDebug operator<<(QDebug, const SourceLocation &);
QDebug operator<<(QDebug, const Diagnostic &);
QDebug operator<<(QDebug debug, const CXCursor &cursor);
QDebug operator<<(QDebug debug, const CXType &type);
#endif // QT_NO_DEBUG_STREAM
} // namespace clang

#endif // CLANGUTILS_H
