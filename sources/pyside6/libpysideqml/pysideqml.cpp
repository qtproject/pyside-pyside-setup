// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include "pysideqml.h"
#include "pysideqmllistproperty_p.h"
#include "pysideqmlattached_p.h"
#include "pysideqmlextended_p.h"
#include "pysideqmlforeign_p.h"
#include "pysideqmlnamedelement_p.h"
#include "pysideqmluncreatable.h"
#include "pysideqmlmetacallerror_p.h"

#include <QtQml/QQmlPropertyMap>

#include <signalmanager.h>

namespace PySide::Qml
{

void init(PyObject *module)
{
    initQtQmlListProperty(module);
    initQmlAttached(module);
    initQmlForeign(module);
    initQmlExtended(module);
    initQmlNamedElement(module);
    initQmlUncreatable(module);
    PySide::SignalManager::setQmlMetaCallErrorHandler(PySide::Qml::qmlMetaCallErrorHandler);

    qRegisterMetaType<QQmlPropertyMap *>(); // PYSIDE-1845, QQmlPropertyMap * properties
}

} //namespace PySide::Qml
