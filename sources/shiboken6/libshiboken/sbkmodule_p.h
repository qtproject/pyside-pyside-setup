// Copyright (C) 2025 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef SBK_MODULE_P_H
#define SBK_MODULE_P_H

#include <string>

namespace Shiboken::Module {

/// PYSIDE-2404: Make sure that mentioned classes really exist.
void loadLazyClassesWithNameStd(const std::string &name);

} // namespace Shiboken::Module

#endif // SBK_MODULE_H
