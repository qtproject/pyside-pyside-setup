// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

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
