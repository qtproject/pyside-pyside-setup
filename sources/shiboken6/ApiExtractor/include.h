// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef INCLUDE_H
#define INCLUDE_H

#include <QtCore/QString>
#include <QtCore/QList>

QT_BEGIN_NAMESPACE
class QTextStream;
QT_END_NAMESPACE

class TextStream;

class Include
{
public:
    enum IncludeType {
        IncludePath,
        LocalPath,
        TargetLangImport
    };

    Include() = default;
    Include(IncludeType t, const QString &nam) : m_type(t), m_name(nam) {};

    bool isValid() const
    {
        return !m_name.isEmpty();
    }

    IncludeType type() const
    {
        return m_type;
    }

    QString name() const
    {
        return m_name;
    }

    QString toString() const;

    friend size_t qHash(const Include &);
    int compare(const Include &rhs) const;

    private:
        IncludeType m_type = IncludePath;
        QString m_name;
};

size_t qHash(const Include& inc);

inline bool operator<(const Include &lhs, const Include &rhs)
{
    return lhs.compare(rhs) < 0;
}

inline bool operator<=(const Include &lhs, const Include &rhs)
{
    return lhs.compare(rhs) <= 0;
}

inline bool operator==(const Include &lhs, const Include &rhs)
{
    return lhs.compare(rhs) == 0;
}

inline bool operator!=(const Include &lhs, const Include &rhs)
{
    return lhs.compare(rhs) != 0;
}

inline bool operator>=(const Include &lhs, const Include &rhs)
{
    return lhs.compare(rhs) >= 0;
}

inline bool operator>(const Include &lhs, const Include &rhs)
{
    return lhs.compare(rhs) > 0;
}

QTextStream& operator<<(QTextStream& out, const Include& include);
TextStream& operator<<(TextStream& out, const Include& include);
#ifndef QT_NO_DEBUG_STREAM
QDebug operator<<(QDebug d, const Include &i);
#endif

using IncludeList = QList<Include>;

struct IncludeGroup
{
    QString title;
    IncludeList includes;

    void append(const Include &include)
    {
        IncludeGroup::appendInclude(include, &includes);
    }

    static void appendInclude(const Include &include, IncludeList *list)
    {
        if (include.isValid() && !list->contains(include))
            list->append(include);
    }
};

TextStream& operator<<(TextStream &out, const IncludeGroup& include);

using IncludeGroupList = QList<IncludeGroup>;

#endif
