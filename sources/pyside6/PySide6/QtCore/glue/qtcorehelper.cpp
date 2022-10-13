// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include <qtcorehelper.h>

#include <QtCore/qdebug.h>

namespace QtCoreHelper {

// Data classes for the generic argument data classes. The argument is freed
// via QMetaType
class QGenericArgumentData
{
public:
    explicit QGenericArgumentData(const QMetaType &type, const void *aData) :
        m_type(type), m_argument(m_type.name(), aData)
    {
    }

    ~QGenericArgumentData()
    {
        if (m_type.isValid())
            m_type.destroy(m_argument.data());
    }

    const QMetaType m_type;
    const QGenericArgument m_argument;
};

class QGenericReturnArgumentData
{
public:
    explicit QGenericReturnArgumentData(const QMetaType &type, void *aData) :
          m_type(type), m_argument(m_type.name(), aData)
    {
    }

    ~QGenericReturnArgumentData()
    {
        if (m_type.isValid())
            m_type.destroy(m_argument.data());
    }

    const QMetaType m_type;
    const QGenericReturnArgument m_argument;
};

QGenericArgumentHolder::QGenericArgumentHolder()
{
}

QGenericArgumentHolder::QGenericArgumentHolder(const QMetaType &type, const void *aData) :
    d(std::make_shared<QGenericArgumentData>(type, aData))
{
}

QGenericArgumentHolder::QGenericArgumentHolder(const QGenericArgumentHolder &) = default;
QGenericArgumentHolder::QGenericArgumentHolder(QGenericArgumentHolder &&) = default;
QGenericArgumentHolder &QGenericArgumentHolder::operator=(const QGenericArgumentHolder &) = default;
QGenericArgumentHolder &QGenericArgumentHolder::operator=(QGenericArgumentHolder &&) = default;
QGenericArgumentHolder::~QGenericArgumentHolder() = default;

QGenericArgument QGenericArgumentHolder::toGenericArgument() const
{
    return d ? d->m_argument : QGenericArgument{};
}

QMetaType QGenericArgumentHolder::metaType() const
{
    return d ? d->m_type : QMetaType{};
}

const void *QGenericArgumentHolder::data() const
{
    return d ? d->m_argument.data() : nullptr;
}

QGenericReturnArgumentHolder::QGenericReturnArgumentHolder(const QMetaType &type, void *aData) :
      d(std::make_shared<QGenericReturnArgumentData>(type, aData))
{
}

QGenericReturnArgumentHolder::QGenericReturnArgumentHolder(const QGenericReturnArgumentHolder &) = default;
QGenericReturnArgumentHolder::QGenericReturnArgumentHolder(QGenericReturnArgumentHolder &&) = default;
QGenericReturnArgumentHolder &QGenericReturnArgumentHolder::operator=(const QGenericReturnArgumentHolder &) = default;
QGenericReturnArgumentHolder &QGenericReturnArgumentHolder::operator=(QGenericReturnArgumentHolder &&) = default;
QGenericReturnArgumentHolder::~QGenericReturnArgumentHolder() = default;

QGenericReturnArgument QGenericReturnArgumentHolder::toGenericReturnArgument() const
{
    return d->m_argument;
}

QMetaType QGenericReturnArgumentHolder::metaType() const
{
    return d->m_type;
}

const void *QGenericReturnArgumentHolder::data() const
{
    return d->m_argument.data();
}

} // namespace QtCoreHelper
