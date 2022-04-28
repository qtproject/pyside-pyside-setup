/****************************************************************************
**
** Copyright (C) 2022 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:LGPL$
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** GNU Lesser General Public License Usage
** Alternatively, this file may be used under the terms of the GNU Lesser
** General Public License version 3 as published by the Free Software
** Foundation and appearing in the file LICENSE.LGPL3 included in the
** packaging of this file. Please review the following information to
** ensure the GNU Lesser General Public License version 3 requirements
** will be met: https://www.gnu.org/licenses/lgpl-3.0.html.
**
** GNU General Public License Usage
** Alternatively, this file may be used under the terms of the GNU
** General Public License version 2.0 or (at your option) the GNU General
** Public license version 3 or any later version approved by the KDE Free
** Qt Foundation. The licenses are as published by the Free Software
** Foundation and appearing in the file LICENSE.GPL2 and LICENSE.GPL3
** included in the packaging of this file. Please review the following
** information to ensure the GNU General Public License requirements will
** be met: https://www.gnu.org/licenses/gpl-2.0.html and
** https://www.gnu.org/licenses/gpl-3.0.html.
**
** $QT_END_LICENSE$
**
****************************************************************************/

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
    d(new QGenericArgumentData(type, aData))
{
}

QGenericArgumentHolder::QGenericArgumentHolder(const QGenericArgumentHolder &) = default;
QGenericArgumentHolder::QGenericArgumentHolder(QGenericArgumentHolder &&) = default;
QGenericArgumentHolder &QGenericArgumentHolder::operator=(const QGenericArgumentHolder &) = default;
QGenericArgumentHolder &QGenericArgumentHolder::operator=(QGenericArgumentHolder &&) = default;
QGenericArgumentHolder::~QGenericArgumentHolder() = default;

QGenericArgumentHolder::operator QGenericArgument() const
{
    return d.isNull() ? QGenericArgument{} : d->m_argument;
}

QMetaType QGenericArgumentHolder::metaType() const
{
    return d.isNull() ? QMetaType{} : d->m_type;
}

const void *QGenericArgumentHolder::data() const
{
    return d.isNull() ? nullptr : d->m_argument.data();
}

QGenericReturnArgumentHolder::QGenericReturnArgumentHolder(const QMetaType &type, void *aData) :
      d(new QGenericReturnArgumentData(type, aData))
{
}

QGenericReturnArgumentHolder::QGenericReturnArgumentHolder(const QGenericReturnArgumentHolder &) = default;
QGenericReturnArgumentHolder::QGenericReturnArgumentHolder(QGenericReturnArgumentHolder &&) = default;
QGenericReturnArgumentHolder &QGenericReturnArgumentHolder::operator=(const QGenericReturnArgumentHolder &) = default;
QGenericReturnArgumentHolder &QGenericReturnArgumentHolder::operator=(QGenericReturnArgumentHolder &&) = default;
QGenericReturnArgumentHolder::~QGenericReturnArgumentHolder() = default;

QGenericReturnArgumentHolder::operator QGenericReturnArgument() const
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
