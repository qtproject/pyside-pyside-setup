// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#include "pysideqml.h"
#include "pysideqmllistproperty_p.h"
#include "pysideqmlattached_p.h"
#include "pysideqmlextended_p.h"
#include "pysideqmlforeign_p.h"
#include "pysideqmlnamedelement_p.h"
#include "pysideqmluncreatable.h"
#include "pysideqmlmetacallerror_p.h"

#include <QtQml/qqmlpropertymap.h>
#include <QtQml/qqmlcomponent.h>

#include <signalmanager.h>

/*!
    \module libpysideqml
    \title PySide QML library
    \brief Library for QML functionality.

    Contains the functionality for registering Python types with QML
    and the decorators of the QtQml module and the \l{QmlFeatures module}.
*/

/*!
    \group QmlFeatures
    \title QmlFeatures module

    \brief QmlFeatures module
*/

/*!
    \namespace PySide
    \brief Root namespace.
    \inmodule libpysideqml
*/

/*!
    \namespace PySide::Qml
    \brief Namespace for QML type registration and decorators.
    \inmodule libpysideqml
*/
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
    qRegisterMetaType<QQmlComponent *>(); // PYSIDE-2415, QQmlComponent * properties
}

} //namespace PySide::Qml
