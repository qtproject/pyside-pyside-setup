// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "clangdebugutils.h"
#include "clangutils.h"

#include <QtCore/QDebug>
#include <QtCore/QString>

#ifndef QT_NO_DEBUG_STREAM

#ifdef Q_OS_WIN
const char pathSep = '\\';
#else
const char pathSep = '/';
#endif

static const char *baseName(const char *fileName)
{
    const char *b = std::strrchr(fileName, pathSep);
    return b ? b + 1 : fileName;
}

QDebug operator<<(QDebug s, const CXString &cs)
{
    s << clang_getCString(cs);
    return s;
}

QDebug operator<<(QDebug s, CXCursorKind cursorKind) // Enum
{
    const CXString kindName = clang_getCursorKindSpelling(cursorKind);
    s << kindName;
    clang_disposeString(kindName);
    return s;
}

static const char *accessSpecsStrings[]
{
    // CX_CXXInvalidAccessSpecifier, CX_CXXPublic, CX_CXXProtected, CX_CXXPrivate
    "invalid",  "public", "protected", "private"
};

QDebug operator<<(QDebug s, CX_CXXAccessSpecifier ac)
{
    s << accessSpecsStrings[ac];
    return s;
}

struct formatCXTypeName
{
    explicit formatCXTypeName(const CXType &type) : m_type(type) {}

    const CXType &m_type;
};

QDebug operator<<(QDebug debug, const formatCXTypeName &ft)
{
    CXString typeSpelling = clang_getTypeSpelling(ft.m_type);
    debug << typeSpelling;
    clang_disposeString(typeSpelling);
    return debug;
}

QDebug operator<<(QDebug debug, const CXType &type)
{
    QDebugStateSaver saver(debug);
    debug.nospace();
    debug.noquote();
    debug << "CXType(";
    if (type.kind == CXType_Invalid) {
        debug << "invalid)";
        return debug;
    }

    debug << type.kind;
    switch (type.kind) {
    case CXType_Unexposed:
        debug << " [unexposed]";
        break;
    case CXType_Elaborated:
        debug << " [elaborated]";
        break;
    default:
        break;
    }
    debug << ", " << formatCXTypeName(type) << ')';
    return debug;
}

QDebug operator<<(QDebug debug, const CXCursor &cursor)
{
    QDebugStateSaver saver(debug);
    debug.nospace();
    debug.noquote();
    const CXCursorKind kind = clang_getCursorKind(cursor);
    debug << "CXCursor(";
    if (kind >= CXCursor_FirstInvalid && kind <= CXCursor_LastInvalid) {
        debug << "invalid)";
        return debug;
    }

    const QString cursorSpelling = clang::getCursorSpelling(cursor);
    debug << '"' << cursorSpelling << '"';
    CXString cursorDisplay = clang_getCursorDisplayName(cursor);
    if (const char *dpy = clang_getCString(cursorDisplay)) {
        const QString display = QString::fromUtf8(dpy);
        if (display != cursorSpelling)
            debug << ", display=\"" << dpy << '"';
    }
    clang_disposeString(cursorDisplay);

    debug << ", kind=" << kind;

    const CXType type = clang_getCursorType(cursor);
    switch (kind) {
        case CXCursor_CXXAccessSpecifier:
        debug << ", " << clang_getCXXAccessSpecifier(cursor);
        break;
    case CXCursor_CXXBaseSpecifier:
         debug << ", inherits=\"" << clang::getCursorSpelling(clang_getTypeDeclaration(type)) << '"';
         break;
    case CXCursor_CXXMethod:
    case CXCursor_FunctionDecl:
    case CXCursor_ConversionFunction:
         debug << ", result type=\""
            << formatCXTypeName(clang_getCursorResultType(cursor)) << '"';
        break;
    case CXCursor_TypedefDecl:
        debug << ", underlyingType=\""
            << formatCXTypeName(clang_getTypedefDeclUnderlyingType(cursor)) << '"';
        break;
    default:
        break;
    }

    debug << ", type=\"" << formatCXTypeName(type) << '"';
    if (clang_Cursor_hasAttrs(cursor))
        debug << ", [attrs]";

    debug << ')';
    return debug;
}

QDebug operator<<(QDebug s, const CXSourceLocation &location)
{
    QDebugStateSaver saver(s);
    s.nospace();
    CXFile file; // void *
    unsigned line;
    unsigned column;
    unsigned offset;
    clang_getExpansionLocation(location, &file, &line, &column, &offset);
    const CXString cxFileName = clang_getFileName(file);
    // Has been observed to be 0 for invalid locations
    if (const char *cFileName = clang_getCString(cxFileName))
        s << baseName(cFileName) << ':';
    s << line << ':' << column;
    clang_disposeString(cxFileName);
    return s;
}

QDebug operator<<(QDebug s, const std::string_view &v)
{
    QDebugStateSaver saver(s);
    s.nospace();
    s.noquote();
    s << '"';
    for (auto c : v)
        s << c;
    s << '"';
    return s;
}

#endif // !QT_NO_DEBUG_STREAM
