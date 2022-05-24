// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TESTVIEW_H
#define TESTVIEW_H

#include "pysidetest_macros.h"

#include <QtCore/QObject>

QT_BEGIN_NAMESPACE
class QWidget;
class QAbstractListModel;
class QAbstractItemDelegate;
QT_END_NAMESPACE

class PYSIDETEST_API TestView : public QObject
{
    Q_OBJECT
public:
    TestView(QAbstractListModel* model, QObject* parent = 0) : QObject(parent), m_model(model) {}
    QAbstractListModel* model() { return m_model; }
    QVariant getData();

    void setItemDelegate(QAbstractItemDelegate* delegate) { m_delegate = delegate; }
    QWidget* getEditorWidgetFromItemDelegate() const;

private:
    QAbstractListModel* m_model;
    QAbstractItemDelegate* m_delegate;
};

#endif // TESTVIEW_H

