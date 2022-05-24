// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

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
