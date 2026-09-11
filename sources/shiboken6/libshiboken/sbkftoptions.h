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

/// Kill switches for what free-threaded builds add, as bit flags in one
/// variable, in the style of PYSIDE6_OPTION_PYTHON_ENUM:
///
///     PYSIDE6_OPTION_FT=0b111111  all of them (the default)
///     PYSIDE6_OPTION_FT=0b011111  without the MI offsets measure
///     PYSIDE6_OPTION_FT=0b000011  the locks only
///     PYSIDE6_OPTION_FT=off       without any of them
///
/// A set bit keeps the measure, a cleared bit takes it away and puts back
/// what was there before it. Unset means all of them, and that is the only
/// supported configuration - clearing a bit is a testing device, not a
/// tuning knob.
///
/// It exists because a measure that cannot be removed proves nothing. Every
/// test in tests/manually/freethreading that claims to demonstrate a fix
/// runs the same scenario twice against the same binary, once with the bit
/// and once without, and has to see the failure return. A mechanism no
/// scenario can take away does not belong here.
enum Option : int
{
    LazyTypeLock     = 0x01, ///< serializes lazy type creation
    StateLock        = 0x02, ///< the short-lived lock on the binding state
    CallGuard        = 0x04, ///< serializes calls reaching one C++ object
    /// Only the type QML asked for may take the placement address. Cleared,
    /// the first constructor to run takes it, whoever it is.
    QmlPlacementType = 0x08,
    /// No process-wide lock spans QML construction. Cleared, one is taken
    /// across the Python call, as it was before the placement context.
    QmlPlacementFree = 0x10,
    /// The multiple-inheritance offsets of a type are computed once, by the
    /// initializer of a function-local static. Cleared, the sentinel check
    /// that used to guard them is back, and two threads reaching a type for
    /// the first time sort and move the same array at the same time.
    MiOffsetsOnce    = 0x20
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
