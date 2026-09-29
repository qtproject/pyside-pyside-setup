// Copyright (C) 2025 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef SBK_MODULE_P_H
#define SBK_MODULE_P_H

#include <string>

namespace Shiboken::Module {

/*!
    \internal
    Makes sure that classes mentioned by \a name really exist (PYSIDE-2404).
*/
void loadLazyClassesWithNameStd(const std::string &name);

} // namespace Shiboken::Module

#endif // SBK_MODULE_H
