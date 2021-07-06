/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
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

#ifndef QTDBUSHELPER_H
#define QTDBUSHELPER_H

#include <QtDBus/qdbusmessage.h>
#include <QtDBus/qdbuspendingcall.h>
#include <QtDBus/qdbusreply.h>

namespace QtDBusHelper {

// A Python-bindings friendly, non-template QDBusReply

class QDBusReply {
public:
    QDBusReply();

    // Enable constructing QDBusReply from a QDBusMessage which is returned by
    // call().
    explicit QDBusReply(const QDBusMessage &reply) :
        m_error(reply),
        m_data(reply.arguments().value(0, {}))
    {
    }

    // Enable constructing QDBusReply from an original Qt QDBusReply for
    // the functions we declare (QDBusConnectionInterface::registeredServiceNames())
    template <class T>
    explicit QDBusReply(const ::QDBusReply<T> &qr) :
        m_error(qr.error()),
        m_data(QVariant(qr.value()))
    {
    }

    explicit QDBusReply(const ::QDBusReply<void> &qr) :
        m_error(qr.error())
    {
    }

    bool isValid() const { return !m_error.isValid(); }

    QVariant value() const
    {
        return m_data;
    }

    const QDBusError &error() const { return m_error; }

private:
    QDBusError m_error;
    QVariant m_data;
};

inline QDBusReply::QDBusReply() = default;

} // namespace QtDBusHelper

#endif // QTDBUSHELPER_H
