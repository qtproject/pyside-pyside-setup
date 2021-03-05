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

#ifndef _PLUGIN_H_
#define _PLUGIN_H_

#include "customwidgets.h"

#include <QtCore/qpluginloader.h>

static inline PyCustomWidgets *findPlugin()
{
    const auto &instances = QPluginLoader::staticInstances();
    for (QObject *o : instances) {
        if (auto plugin = qobject_cast<PyCustomWidgets *>(o))
            return plugin;
    }
    return nullptr;
}

static void registerCustomWidget(PyObject *obj)
{
    static PyCustomWidgets *const plugin = findPlugin();

    if (plugin)
        plugin->registerWidgetType(obj);
    else
        qWarning("Qt for Python: Failed to find the static QUiLoader plugin.");
}

#endif
