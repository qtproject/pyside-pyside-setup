// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef _PY_DESIGNER_CUSTOM_WIDGETS_H_
#define _PY_DESIGNER_CUSTOM_WIDGETS_H_

#include <QtUiPlugin/QDesignerCustomWidgetCollectionInterface>

// A Qt Designer plugin proxying the QDesignerCustomWidgetCollectionInterface
// instance set as as a dynamic property on QCoreApplication by the PySide6
// Qt Designer module.
class PyDesignerCustomWidgets: public QObject,
                               public QDesignerCustomWidgetCollectionInterface
{
    Q_OBJECT
    Q_INTERFACES(QDesignerCustomWidgetCollectionInterface)
    Q_PLUGIN_METADATA(IID "org.qt-project.Qt.PySide.PyDesignerCustomWidgetsInterface")

public:
    explicit PyDesignerCustomWidgets(QObject *parent = nullptr);
    ~PyDesignerCustomWidgets();

    QList<QDesignerCustomWidgetInterface *> customWidgets() const override;
};

#endif // _PY_DESIGNER_CUSTOM_WIDGETS_H_
