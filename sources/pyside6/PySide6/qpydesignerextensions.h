/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:LGPL$
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** GNU Lesser General Public License Usage
** Alternatively, this file may be used under the terms of the GNU Lesser
** General Public License version 3 as published by the Free Software
** Foundation and appearing in the file LICENSE.LGPL3 included in the
** packaging of this file. Please review the following information to
** ensure the GNU Lesser General Public License version 3 requirements
** will be met: https://www.gnu.org/licenses/lgpl-3.0.html.
**
** GNU General Public License Usage
** Alternatively, this file may be used under the terms of the GNU
** General Public License version 2.0 or (at your option) the GNU General
** Public license version 3 or any later version approved by the KDE Free
** Qt Foundation. The licenses are as published by the Free Software
** Foundation and appearing in the file LICENSE.GPL2 and LICENSE.GPL3
** included in the packaging of this file. Please review the following
** information to ensure the GNU General Public License requirements will
** be met: https://www.gnu.org/licenses/gpl-2.0.html and
** https://www.gnu.org/licenses/gpl-3.0.html.
**
** $QT_END_LICENSE$
**
****************************************************************************/

#ifndef QPYDESIGNEREXTENSIONS_H
#define QPYDESIGNEREXTENSIONS_H

#include <QtDesigner/QDesignerContainerExtension>
#include <QtDesigner/QDesignerMemberSheetExtension>
#include <QtDesigner/QDesignerPropertySheetExtension>
#include <QtDesigner/QDesignerTaskMenuExtension>
#include <QtUiPlugin/QDesignerCustomWidgetCollectionInterface>
#include <QtUiPlugin/QDesignerCustomWidgetInterface>

// Not automatically found since "find_package(Qt6 COMPONENTS Designer)" is not used

#ifdef Q_MOC_RUN
Q_DECLARE_INTERFACE(QDesignerContainerExtension, "org.qt-project.Qt.Designer.Container")
Q_DECLARE_INTERFACE(QDesignerMemberSheetExtension, "org.qt-project.Qt.Designer.MemberSheet")
Q_DECLARE_EXTENSION_INTERFACE(QDesignerPropertySheetExtension, "org.qt-project.Qt.Designer.PropertySheet")
Q_DECLARE_INTERFACE(QDesignerTaskMenuExtension, "org.qt-project.Qt.Designer.TaskMenu")
Q_DECLARE_INTERFACE(QDesignerCustomWidgetCollectionInterface, "org.qt-project.Qt.QDesignerCustomWidgetCollectionInterface")
#endif

// Extension implementations need to inherit QObject which cannot be done in Python.
// Provide a base class (cf QPyTextObject).

class QPyDesignerContainerExtension : public QObject, public QDesignerContainerExtension
{
    Q_OBJECT
    Q_INTERFACES(QDesignerContainerExtension)
public:
    explicit QPyDesignerContainerExtension(QObject *parent = nullptr) : QObject(parent) {}
};

class QPyDesignerMemberSheetExtension : public QObject, public QDesignerMemberSheetExtension
{
    Q_OBJECT
    Q_INTERFACES(QDesignerMemberSheetExtension)
public:
    explicit QPyDesignerMemberSheetExtension(QObject *parent = nullptr) : QObject(parent) {}
};

class QPyDesignerPropertySheetExtension : public QObject, public QDesignerPropertySheetExtension
{
    Q_OBJECT
    Q_INTERFACES(QDesignerPropertySheetExtension)
public:
    explicit QPyDesignerPropertySheetExtension(QObject *parent = nullptr) : QObject(parent) {}
};

class QPyDesignerTaskMenuExtension : public QObject, public QDesignerTaskMenuExtension
{
    Q_OBJECT
    Q_INTERFACES(QDesignerTaskMenuExtension)
public:
    explicit QPyDesignerTaskMenuExtension(QObject *parent = nullptr) : QObject(parent) {}
};

struct _object; // PyObject

class QPyDesignerCustomWidgetCollection : public QDesignerCustomWidgetCollectionInterface
{
public:
    ~QPyDesignerCustomWidgetCollection();

    static QPyDesignerCustomWidgetCollection *instance();

    QList<QDesignerCustomWidgetInterface *> customWidgets() const override;

    static void addCustomWidget(QDesignerCustomWidgetInterface *c);

    static bool _registerCustomWidgetHelper(_object *typeArg, _object *kwds);

private:
    QPyDesignerCustomWidgetCollection();

    QList<QDesignerCustomWidgetInterface *> m_customWidgets;
};

#endif // QPYDESIGNEREXTENSIONS_H
