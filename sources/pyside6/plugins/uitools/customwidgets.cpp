// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include "customwidgets.h"
#include "customwidget.h"

PyCustomWidgets::PyCustomWidgets(QObject *parent)
    : QObject(parent)
{
}

PyCustomWidgets::~PyCustomWidgets()
{
    qDeleteAll(m_widgets);
}

void PyCustomWidgets::registerWidgetType(PyObject *widget)
{
    m_widgets.append(new PyCustomWidget(widget));
}

QList<QDesignerCustomWidgetInterface *> PyCustomWidgets::customWidgets() const
{
    return m_widgets;
}
