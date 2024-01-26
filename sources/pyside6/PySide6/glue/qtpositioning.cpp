// Copyright (C) 2024 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

/*********************************************************************
 * INJECT CODE
 ********************************************************************/

// @snippet darwin_location_permission_plugin
#ifdef Q_OS_DARWIN
#include<QtCore/qplugin.h>
// register the static plugin and setup its metadata
Q_IMPORT_PLUGIN(QDarwinLocationPermissionPlugin)
#endif
// @snippet darwin_location_permission_plugin
