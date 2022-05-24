// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "testview.h"

#include <QtCore/QDebug>
#include <QtCore/QAbstractListModel>
#include <QtWidgets/QAbstractItemDelegate>
#include <QtWidgets/QWidget>

QVariant
TestView::getData()
{
    QModelIndex index;
    return m_model->data(index);
}

QWidget*
TestView::getEditorWidgetFromItemDelegate() const
{
    if (!m_delegate)
        return nullptr;

    QModelIndex index;
    QStyleOptionViewItem options;
    return m_delegate->createEditor(nullptr, options, index);
}
