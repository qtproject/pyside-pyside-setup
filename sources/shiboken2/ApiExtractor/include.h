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

#ifndef INCLUDE_H
#define INCLUDE_H

#include <qtcompat.h>

#include <QString>
#include <QVector>

QT_BEGIN_NAMESPACE
class QTextStream;
QT_END_NAMESPACE

class Include
{
public:
    enum IncludeType {
        IncludePath,
        LocalPath,
        TargetLangImport,
        InvalidInclude
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

    bool operator<(const Include& other) const
    {
        return m_name < other.m_name;
    }

    bool operator==(const Include& other) const
    {
        return m_type == other.m_type && m_name == other.m_name;
    }

    friend QtCompatHashFunctionType qHash(const Include&);
    private:
        IncludeType m_type = IncludePath;
        QString m_name;
};

QtCompatHashFunctionType qHash(const Include& inc);
QTextStream& operator<<(QTextStream& out, const Include& include);
#ifndef QT_NO_DEBUG_STREAM
QDebug operator<<(QDebug d, const Include &i);
#endif

using IncludeList = QVector<Include>;

#endif
