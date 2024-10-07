// Copyright (C) 2024 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include "webengineframe.h"

#include <QtWebEngineCore/qwebengineframe.h>

QT_BEGIN_NAMESPACE

// Enable using QWebEngineFrame as a value-type by adding a way of
// default-constructing by creating a replica with the same data members.
// (see attribute "default-constructor").
QWebEngineFrame defaultConstructedWebEngineFrame()
{
    class FriendlyWebEngineFrame // Keep in sync with QWebEngineFrame
    {
    public:
        QWeakPointer<QObject> m_w;
        quint64 m_id = 0;
    };

    FriendlyWebEngineFrame frame;
    return std::move(*reinterpret_cast<QWebEngineFrame*>(&frame));
}

QT_END_NAMESPACE
