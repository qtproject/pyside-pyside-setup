// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
// Qt-Security score:significant reason:default

#include "sbkheldlocks.h"

#include <array>
#include <atomic>
#include <cstdio>
#include <string>

namespace Shiboken
{

int lockRank(RawLock lock)
{
    switch (lock) {
    case RawLock::LazyType:         return int(LockRank::LazyType);
    case RawLock::ClassHierarchy:   return int(LockRank::ClassHierarchy);
    case RawLock::ModuleData:       return int(LockRank::ModuleData);
    case RawLock::MetaObject:       return int(LockRank::MetaObject);
    case RawLock::ConnectionHash:   return int(LockRank::ConnectionHash);
    case RawLock::WrapperMap:       return int(LockRank::WrapperMap);
    case RawLock::MainThreadDelete: return int(LockRank::MainThreadDelete);
    case RawLock::State:            return int(LockRank::State);
    case RawLock::PostRoutine:      return int(LockRank::PostRoutine);
    case RawLock::QObjectMetaType:  return int(LockRank::QObjectMetaType);
    }
    return 0;
}

#ifndef NDEBUG

// One counter per lock rather than one bit: three of the locks are recursive,
// and a nested acquisition has to survive the inner release.
static constexpr size_t LockCount = 10;

static std::array<unsigned, LockCount> &heldCounts()
{
    static thread_local std::array<unsigned, LockCount> counts{};
    return counts;
}

static size_t lockIndex(RawLock lock)
{
    auto bits = static_cast<unsigned>(lock);
    size_t index = 0;
    while ((bits >>= 1) != 0)
        ++index;
    return index;
}

static const char *lockName(size_t index)
{
    static const char *names[LockCount] = {
        "state", "wrapper map", "main-thread deletion", "lazy type",
        "module data", "connection hash", "meta-object", "class hierarchy",
        "post routines", "qobject-pointer metatype"
    };
    return names[index];
}

// Every pair this process ever held at once: one word per outer lock, one
// bit per inner. Recording a nesting is one atomic or on a word the hardware
// handles, and needs no lock of its own - which it must not have: this runs
// while a raw lock is held, and a mutex here would sit below the state lock
// and take away the leaf property the rank exists to state.
static std::array<std::atomic<uint64_t>, LockCount> &nestingBits()
{
    static std::array<std::atomic<uint64_t>, LockCount> bits{};
    return bits;
}

void checkLockRank(RawLock lock)
{
    const size_t index = lockIndex(lock);
    const auto &counts = heldCounts();
    for (size_t i = 0; i < LockCount; ++i) {
        if (counts[i] == 0 || i == index)
            continue;
        // The order has to be the same everywhere, or two threads can hold
        // this pair crosswise and neither can go on. Taking a lock under one
        // that ranks above it is that mistake, and it aborts here rather
        // than deadlocking somewhere else later.
        assert(lockRank(RawLock(1u << i)) < lockRank(lock)
               || reportLocksHeld(lockName(index), "taken out of rank order"));
        nestingBits()[i].fetch_or(uint64_t(1) << index, std::memory_order_relaxed);
    }
}

void noteLockAcquired(RawLock lock)
{
    // Idempotent when TrackedGuard already asked before it waited: the
    // assertion has no state and the nesting bit is a fetch_or.
    checkLockRank(lock);
    ++heldCounts()[lockIndex(lock)];
}

void noteLockReleased(RawLock lock)
{
    auto &count = heldCounts()[lockIndex(lock)];
    assert(count > 0);
    --count;
}

bool holdsLock(RawLock lock)
{
    return heldCounts()[lockIndex(lock)] != 0;
}

bool holdsAnyLock()
{
    for (auto count : heldCounts()) {
        if (count != 0)
            return true;
    }
    return false;
}

const char *heldLockNames()
{
    // Per thread: the held set is thread-local, and two threads asking at
    // once must not overwrite each other's answer.
    static thread_local std::string names;
    names.clear();
    const auto &counts = heldCounts();
    for (size_t i = 0; i < LockCount; ++i) {
        if (counts[i] == 0)
            continue;
        if (!names.empty())
            names += ", ";
        names += lockName(i);
    }
    return names.empty() ? "none" : names.c_str();
}

bool reportLocksHeld(const char *where, const char *what)
{
    std::fprintf(stderr, "libshiboken: %s in %s(), but this thread holds: %s\n",
                 what, where, heldLockNames());
    return false;
}

// One counter per lock, for the places where the contract's exception was
// taken. Relaxed and atomic: this is a diagnostic, and it runs while a raw
// lock is held, so it must not take one of its own.
static std::array<std::atomic<unsigned>, LockCount> &exceptionCounts()
{
    static std::array<std::atomic<unsigned>, LockCount> counts{};
    return counts;
}

void noteContractException(RawLock lock)
{
    exceptionCounts()[lockIndex(lock)].fetch_add(1, std::memory_order_relaxed);
}

void checkNoRawLock(const char *where)
{
    const auto &counts = heldCounts();
    for (size_t i = 0; i < LockCount; ++i) {
        if (counts[i] == 0)
            continue;
        if (RawLock(1u << i) == RawLock::LazyType) {
            noteContractException(RawLock::LazyType);
            continue;
        }
        assert(reportLocksHeld(where, "no raw lock may be held here"));
    }
}

const char *contractExceptions()
{
    // Per thread: the report is built in a buffer that is handed out as a
    // C string, and a second thread asking must not rewrite it underneath
    // the first one's reader.
    static thread_local std::string report;
    report.clear();
    const auto &counts = exceptionCounts();
    for (size_t i = 0; i < LockCount; ++i) {
        const unsigned count = counts[i].load(std::memory_order_relaxed);
        if (count == 0)
            continue;
        if (!report.empty())
            report += '\n';
        report += lockName(i);
        report += ": ";
        report += std::to_string(count);
    }
    return report.c_str();
}

const char *lockNestings()
{
    // Per thread, as in contractExceptions().
    static thread_local std::string report;
    report.clear();
    const auto &bits = nestingBits();
    for (size_t outer = 0; outer < LockCount; ++outer) {
        const uint64_t inners = bits[outer].load(std::memory_order_relaxed);
        for (size_t inner = 0; inner < LockCount; ++inner) {
            if ((inners & (uint64_t(1) << inner)) == 0)
                continue;
            if (!report.empty())
                report += '\n';
            report += lockName(outer);
            report += " -> ";
            report += lockName(inner);
        }
    }
    return report.c_str();
}

#endif // NDEBUG

} // namespace Shiboken
