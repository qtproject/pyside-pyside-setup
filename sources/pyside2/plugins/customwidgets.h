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

#ifndef _PY_CUSTOM_WIDGETS_H_
#define _PY_CUSTOM_WIDGETS_H_

#include <shiboken.h>

#include <QtUiPlugin/QDesignerCustomWidgetInterface>

#include <QtCore/qlist.h>

// A static plugin linked to the QtUiLoader Python module
class PyCustomWidgets: public QObject, public QDesignerCustomWidgetCollectionInterface
{
    Q_OBJECT
    Q_INTERFACES(QDesignerCustomWidgetCollectionInterface)
    Q_PLUGIN_METADATA(IID "org.qt-project.Qt.PySide.PyCustomWidgetsInterface")

public:
    explicit PyCustomWidgets(QObject *parent = nullptr);
    ~PyCustomWidgets();

    QList<QDesignerCustomWidgetInterface*> customWidgets() const override;

    // Called from added function QUiLoader::registerCustomWidget()
    void registerWidgetType(PyObject* widget);

private:
    QList<QDesignerCustomWidgetInterface *> m_widgets;
};

#endif
