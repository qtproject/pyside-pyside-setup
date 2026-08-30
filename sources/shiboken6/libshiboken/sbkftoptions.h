// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef SBK_FTOPTIONS_H
#define SBK_FTOPTIONS_H

#include "sbkpython.h"
#include "shibokenmacros.h"

// Free-threaded builds only: with a GIL there are no locks to switch off.
#ifdef Py_GIL_DISABLED

namespace Shiboken::FreeThreading {

/// Kill switches for the locks that free-threaded builds add, as bit flags in
/// one variable, in the style of PYSIDE6_OPTION_PYTHON_ENUM:
///
///     PYSIDE6_OPTION_FT=0b111     all of them (the default)
///     PYSIDE6_OPTION_FT=0b011     without the per-object call guard
///     PYSIDE6_OPTION_FT=0b001     without the state lock either
///     PYSIDE6_OPTION_FT=off       without any of them
///
/// A set bit keeps its lock, a cleared bit takes it away. Unset means all of
/// them, and that is the only supported configuration - clearing a bit is a
/// testing device, not a tuning knob.
///
/// It exists because a lock that is never removed proves nothing; the A/B
/// harness in tests/manually/freethreading runs each scenario against the same
/// binary once with its lock and once without. A mechanism that no scenario
/// can take away does not belong here.
enum Option : int
{
    LazyTypeLock = 0x1, ///< serializes lazy type creation
    StateLock    = 0x2, ///< the short-lived lock on the binding state
    CallGuard    = 0x4  ///< serializes calls reaching one C++ object
};

/// Whether opt is enabled. The environment is read once, on first use.
///
/// Out of line on purpose. This header reaches libshiboken, libpyside and
/// every generated module, and -fvisibility=hidden would give each of them
/// its own copy of the flags to parse and keep.
LIBSHIBOKEN_API bool optionEnabled(Option opt);

} // namespace Shiboken::FreeThreading

#endif // Py_GIL_DISABLED

#endif // SBK_FTOPTIONS_H
