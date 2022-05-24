// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

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
