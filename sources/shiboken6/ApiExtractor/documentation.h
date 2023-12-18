// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef DOCUMENTATION_H
#define DOCUMENTATION_H

#include <QtCore/QString>
#include <QtCore/QtCompare>

QT_FORWARD_DECLARE_CLASS(QDebug)

class Documentation
{
public:
    enum Format {
        Native, // XML
        Target  // RST
    };

    enum Type {
        Detailed,
        Brief,
        Last
    };

    Documentation() = default;
    explicit Documentation(const QString &detailed,
                           const QString &brief,
                           Format fmt = Documentation::Native);

    bool isEmpty() const;

    void setValue(const QString& value, Type t = Documentation::Detailed);

    Documentation::Format format() const;
    void setFormat(Format f);

    bool equals(const Documentation &rhs) const;

    const QString &detailed() const { return m_detailed; }
    void setDetailed(const QString &detailed);

    bool hasBrief() const { return !m_brief.isEmpty(); }
    const QString &brief() const { return m_brief; }
    void setBrief(const QString &brief);

private:
    friend bool comparesEqual(const Documentation &lhs,
                              const  Documentation &rhs) noexcept
    {
        return lhs.m_format == rhs.m_format && lhs.m_detailed == rhs.m_detailed
               && lhs.m_brief == rhs.m_brief;
    }
    Q_DECLARE_EQUALITY_COMPARABLE(Documentation)

    QString m_detailed;
    QString m_brief;
    Format m_format = Documentation::Native;
};

#ifndef QT_NO_DEBUG_STREAM
QDebug operator<<(QDebug debug, const Documentation &);
#endif

#endif // DOCUMENTATION_H
