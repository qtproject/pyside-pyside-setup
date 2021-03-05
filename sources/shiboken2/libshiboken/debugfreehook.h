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

#ifndef DEBUGFREEHOOK_H
#define DEBUGFREEHOOK_H

// These functions enable C library runtime hooks to try to catch cases where
// C++ object addresses remain in hash table of valid wrappers when the address
// is passed to free.  The hooks are probably not thread safe and thus
// should only be enabled in single threaded environments

// To enable the hook, uncomment the following define.
//#define SHIBOKEN_INSTALL_FREE_DEBUG_HOOK

#ifdef SHIBOKEN_INSTALL_FREE_DEBUG_HOOK
extern "C" {

void debugInstallFreeHook(void);
void debugRemoveFreeHook(void);

} // extern "C"

#endif // SHIBOKEN_INSTALL_FREE_DEBUG_HOOK

#endif // DEBUGFREEHOOK_H
