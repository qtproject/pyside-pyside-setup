// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "clangtype.h"

#include <QtCore/qdebug.h>

using namespace Qt::StringLiterals;

// Up until clang version 21, clang_getTypeSpelling() was used to retrieve type names,
// which returned fully qualified names. In clang 22, clang_getTypeSpelling() was
// changed to return the actual spelling, that is, no longer return fully qualified names
// (from for example inner class contexts) unless they were spelled out.
// clang_getFullyQualifiedName() was provided as a replacement, but that returns
// template parameters of the class as well, that is, "std::list<int>::value_type"
// instead of "std::list::value_type". Those they need to be removed for the
// type entry lookup system to work. This is done by parseTypeName().
// FIXME: Keep checking whether this can be replaced by a CXPrintingPolicy setting
// in a later clang version.

namespace clang {

// Find the start of a template starting from the closing '>'
static qsizetype findTemplateStart(QStringView sv, qsizetype pos)
{
    Q_ASSERT(pos > 0 && pos < sv.size() && sv.at(pos) == u'>');
    int level = 1;
    for (--pos; pos >= 0; --pos) {
        switch (sv.at(pos).unicode()) {
        case '>':
            ++level;
            break;
        case '<':
            if (--level == 0)
                return pos;
            break;
        default:
            break;
        }
    }
    return -1;
}

std::optional<TypeName> parseTypeName(QString t)
{
    TypeName result;
    // Skip over the trailing template parameters "list<T>::iterator<V>" ->
    // "list<T>::iterator"
    if (t.endsWith(u'>')) {
        const auto pos = findTemplateStart(t, t.size() - 1);
        if (pos == -1)
            return std::nullopt;
        result.templateParameters = t.sliced(pos, t.size() - pos);
        t.truncate(pos);
    }

    // Remove class template parameters "list<T>::iterator" -> "list::iterator"
    while (true) {
        auto specEnd = t.lastIndexOf(">::"_L1);
        if (specEnd == -1)
            break;
        const auto pos = findTemplateStart(t, specEnd);
        if (pos == -1)
            return std::nullopt;
        t.remove(pos, specEnd + 1 - pos);
    }
    result.name = t;
    return result;
}

QDebug operator<<(QDebug debug, const TypeName &ct)
{
    QDebugStateSaver saver(debug);
    debug.nospace();
    debug.noquote();
    debug << "ClangTypeName(name=\"" << ct.name << '"';
    if (!ct.templateParameters.isEmpty())
        debug << ", templateParameters=\"" << ct.templateParameters << '"';
    debug << ')';
    return debug;
}

} // namespace clang
