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
///     PYSIDE6_OPTION_FT unset     all of them (the default)
///     PYSIDE6_OPTION_FT=on        the same, spelled out
///     PYSIDE6_OPTION_FT=0b11      the locks only
///     PYSIDE6_OPTION_FT=off       without any of them
///
/// Taking one measure away means setting every other bit, and how many
/// there are grows with the enum below - which is why no example here
/// spells that number out. It went stale twice. The tests build the mask
/// from this header (ftoptions.py), and so should anything else.
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
    MiOffsetsOnce    = 0x20,
    /// A thread with no thread state does address checks only. Cleared, the
    /// virtual-call preflight narrows by type before it attaches, which
    /// reads Py_TYPE and walks tp_mro with no thread state.
    NativePreflight  = 0x40,
    /// A retired identity stays in the wrapper map as a tombstone until the
    /// destruction that retires it can no longer reach the address. Cleared,
    /// the entry is removed where it always was, and a lookup in the window
    /// that follows publishes a wrapper for an object about to be destroyed.
    Tombstones       = 0x80,
    /// A type that invalidates such wrappers itself may still be converted
    /// while it is being destroyed - what destroyed(QObject *) needs, since
    /// its argument is meant to be used. Cleared, the tombstone refuses
    /// every dying identity and the handler gets a dead wrapper.
    DyingConversionException = 0x100,
    /// A wrapper handed out under that exception belongs to the tombstone
    /// that let it through: it stays out of the wrapper map, and the
    /// tombstone invalidates it when it falls. Cleared, it is registered
    /// like any other wrapper and stays valid over an address whose object
    /// is already gone.
    DyingStrays      = 0x200,
    /// A destruction that C++ started leaves a tombstone too, and it stands
    /// until the memory is handed back - the generated wrapper's operator
    /// delete is what says so. Cleared, the entry is simply removed where
    /// Object::destroy() always removed it, and the stretch from there to
    /// the last base destructor is open again.
    ExternalTombstones = 0x400,
    /// A generated constructor claims its native slot in one transaction.
    /// Cleared, the check and the write are two steps again, and two threads
    /// initializing the same object both believe they won.
    ConstructorCommit = 0x800,
    /// A generated constructor reserves its pointer slot before it builds
    /// anything. Cleared, the slot is claimed after the C++ constructor as
    /// it was, and the thread that loses has already built its object and,
    /// for a QObject, hung it in Qt's tree.
    ConstructorClaim = 0x1000,
    /// Parsing a Python type for a dynamic meta-object happens with no
    /// binding lock held. Cleared, the instance builder is built under the
    /// meta-object lock as it was, and the attribute lookups, warnings and
    /// enum resolution of parsePythonType() run with a raw lock held.
    MetaObjectParseOutsideLock = 0x2000,
    /// A lease asks the instance whether it is a wrapper. Cleared, it
    /// compares the metatype for identity, and a class that brings a
    /// metaclass of its own - class Meta(type(QObject), ABCMeta) - is not
    /// recognized as one: the call runs with no lease at all.
    MetatypeSubclassLease = 0x4000,
    /// A lease carries the C++ pointer it copied in the transaction that
    /// granted it, and its holder uses that copy. Cleared, the holder reads
    /// the wrapper's pointer array a second time, after the transaction -
    /// where a concurrent Object::destroy() has already detached it.
    LeaseSnapshot = 0x8000,
    /// A waiting claim covers only the object it was requested on;
    /// the rest of the owned set derives the claim from the current parent
    /// chain, so a child moving out leaves it behind and one moving in picks
    /// it up. Cleared, the request marks the whole owned set once.
    ClaimByAncestry = 0x10000,
    /// A child detached because its parent is torn down keeps the claim it
    /// derived. Cleared, the claim goes with the edge, and a child that keeps
    /// validCppObject is callable while the parent's destructor frees it.
    /// Only meaningful with ClaimByAncestry.
    ClaimThroughTeardown = 0x20000,
    /// A lease taken inside an argument's conversion - on a container
    /// element, on a wrapper passed as void * - is kept until the native call
    /// has returned. Cleared, it ends with the conversion, and a concurrent
    /// Shiboken.delete() frees the element before the call uses its pointer.
    ConversionLeasesKept = 0x1000000,
    /// The deallocator claims what the parent's destructor takes along, and
    /// hands that destructor to the last lease when a call on a child is
    /// still open. Cleared, it destroys the owned set without looking, and a
    /// child is freed under a call in flight.
    DeallocClaim = 0x2000000,
    /// The instance dict is created under the object's critical section, as
    /// CPython creates it, and never replaced: tp_clear empties it. Cleared,
    /// a first access can overwrite a dict another thread created, and
    /// tp_clear releases the dict under a reader.
    DictPublishOnce = 0x10000000
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
