// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PY_DESIGNER_CUSTOM_WIDGETS_H_
#define PY_DESIGNER_CUSTOM_WIDGETS_H_

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
    Q_DISABLE_COPY_MOVE(PyDesignerCustomWidgets)

    explicit PyDesignerCustomWidgets(QObject *parent = nullptr);
    ~PyDesignerCustomWidgets() override;

    QList<QDesignerCustomWidgetInterface *> customWidgets() const override;
};

#endif // PY_DESIGNER_CUSTOM_WIDGETS_H_
