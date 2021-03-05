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

#ifndef _PY_CUSTOM_WIDGET_H_
#define _PY_CUSTOM_WIDGET_H_

#include <shiboken.h>

#include <QtUiPlugin/QDesignerCustomWidgetInterface>

#include <QtCore/qglobal.h>

class PyCustomWidget: public QObject, public QDesignerCustomWidgetInterface
{
     Q_OBJECT
     Q_INTERFACES(QDesignerCustomWidgetInterface)

public:
    explicit PyCustomWidget(PyObject *objectType);

    bool isContainer() const override;
    bool isInitialized() const override;
    QIcon icon() const override;
    QString domXml() const override;
    QString group() const override;
    QString includeFile() const override;
    QString name() const override;
    QString toolTip() const override;
    QString whatsThis() const override;
    QWidget *createWidget(QWidget *parent) override;
    void initialize(QDesignerFormEditorInterface *core) override;

private:
    PyObject *m_pyObject = nullptr;
    const QString m_name;
    bool m_initialized = false;
};

#endif // _PY_CUSTOM_WIDGET_H_
