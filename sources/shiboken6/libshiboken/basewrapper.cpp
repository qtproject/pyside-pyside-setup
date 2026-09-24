// Copyright (C) 2019 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:critical reason:low-level-memory-management

#include "autodecref.h"
#include "basewrapper.h"
#include "basewrapper_p.h"
#include "bindingmanager.h"
#include "gilstate.h"
#include "helper.h"
#include "pep384ext.h"
#include "pep384impl_p.h"
#include "sbkconverter.h"
#include "sbkerrors.h"
#include "sbkfeature_base.h"
#include "sbkstaticstrings.h"
#include "sbkstaticstrings_p.h"
#include "sbkstring.h"
#include "sbktypefactory.h"
#include "signature.h"
#include "signature_p.h"
#include "threadstatesaver.h"
#include "voidptr.h"
// Not under Py_GIL_DISABLED: the wrapper map, the connection hash and the
// meta-object builder have their locks in either build, and the type helpers
// below state the state lock's leaf property in code the two builds share.
#include "sbkheldlocks.h"
// Same reason: a failpoint in code the two builds share has to compile in
// both, where the macro expands to nothing.
#include "sbkfailpoint.h"
#ifdef Py_GIL_DISABLED
#  include "sbkftoptions.h"
#  include "sbkstatelock.h"
#endif

#include <algorithm>
#ifdef Py_GIL_DISABLED
#include <atomic>
#endif
#include <cctype>
#include <cstddef>
#include <cstdlib>
#include <cstring>
#include <iostream>
#ifdef Py_GIL_DISABLED
#include <iterator>
#include <new>
#endif
#include <set>
#include <sstream>
#include <string>

#ifdef __APPLE__
#  include <dlfcn.h>
#endif

namespace {
    void _destroyParentInfo(SbkObject *obj, bool keepReference);
    void _detachChildren(SbkObject *obj, bool keepReference);
}

struct BaseWrapperGlobals
{
    PyTypeObject *sbkObjectType = nullptr;
    PyTypeObject *sbkObjectMetaType = nullptr;
    PyObject *qAppLast = nullptr;
};

static BaseWrapperGlobals *baseWrapperGlobals()
{
    static BaseWrapperGlobals result;
    return &result;
}

#ifdef Py_GIL_DISABLED

// ---- Destruction claims ----------------------------------------------------
// See "Destruction claims follow the parent graph" in the free-threading notes.

// Claims accepted and not extracted yet. Written under the state lock, read
// without it: while it is zero, an object's own flag is the whole answer.
static std::atomic<int> &waitingClaims()
{
    static std::atomic<int> instance{0};
    return instance;
}

// Defined further below. Declared inside its namespace: a second declaration
// at file scope would make calls from within Shiboken::Object ambiguous.
namespace Shiboken::Object
{
static std::vector<SbkObject *> collectOwnedLocked(SbkObject *root);
static bool detachFirstChild(SbkObject *parent, bool keepReference);
} // namespace Shiboken::Object

static SbkObject *parentOfLocked(SbkObject *self)
{
    SBK_ASSERT_STATE_LOCKED();
    auto *pInfo = self->d->parentInfo;
    return pInfo != nullptr ? pInfo->parent : nullptr;
}

/// Whether a destruction claim covers \a self - its own, or one made on an
/// object it is currently a descendant of.
static bool isClaimedLocked(SbkObject *self)
{
    SBK_ASSERT_STATE_LOCKED();
    if (self->d->directDestruction)
        return true;
    // Nothing waits, so nothing can be inherited. This holds only because
    // every write of directDestruction except the waiting root's covers the
    // whole owned set below the node (stampOwnedSetLocked(),
    // keepClaimThroughTeardownLocked(), claimDeallocLocked()): a descendant
    // left to the derivation
    // would lose its claim right here.
    if (waitingClaims().load(std::memory_order_relaxed) == 0
        || !Shiboken::FreeThreading::optionEnabled(Shiboken::FreeThreading::ClaimByAncestry)) {
        return false;
    }
    // Tortoise and hare: setParent() accepts a cycle, and a set of seen nodes
    // would allocate inside a transaction.
    SbkObject *slow = self;
    SbkObject *fast = self;
    for (;;) {
        for (int step = 0; step < 2; ++step) {
            fast = parentOfLocked(fast);
            if (fast == nullptr)
                return false;
            if (fast->d->directDestruction)
                return true;
        }
        slow = parentOfLocked(slow);
        if (slow == fast)
            return false;   // a cycle, and no claim anywhere in it
    }
}

/// isClaimedLocked() for a caller that holds no lock. The two unlocked reads
/// may be stale, so the answer is advisory, like isValid() in general; the
/// answer that gates a call is taken in acquireCallLeaseLocked().
static bool isClaimed(SbkObject *self)
{
    SBK_ASSERT_STATE_UNLOCKED();
    if (self->d->directDestruction)
        return true;
    if (waitingClaims().load(std::memory_order_relaxed) == 0)
        return false;
    Shiboken::StateLockGuard guard;
    return isClaimedLocked(self);
}

/// Stamp the claim \a child derives onto its whole owned set, before the edge
/// is removed because the parent is torn down (B6-1). Called from the two
/// sites that detach for a teardown; removeParentLocked() cannot tell one
/// from a reparent.
/// See "A teardown keeps the claim" in the free-threading notes.
static void keepClaimThroughTeardownLocked(SbkObject *child)
{
    SBK_ASSERT_STATE_LOCKED();
    if (!Shiboken::FreeThreading::optionEnabled(Shiboken::FreeThreading::ClaimThroughTeardown))
        return;
    if (!isClaimedLocked(child))
        return;
    for (SbkObject *o : Shiboken::Object::collectOwnedLocked(child))
        o->d->directDestruction = true;
}

#endif // Py_GIL_DISABLED

namespace Shiboken
{
// Walk through the first level of non-user-type Sbk base classes relevant for
// C++ object allocation. Return true from the predicate to terminate.
template <class Predicate>
bool walkThroughBases(PyTypeObject *currentType, Predicate predicate)
{
    // Reads tp_bases and calls PyType_IsSubtype(). The state lock is a leaf,
    // and every lease and lifecycle transaction rests on that; a path that
    // reaches here from inside one aborts rather than waiting for the next
    // review to find it.
    SBK_ASSERT_LOCK_NOT_HELD(State);
    PyObject *bases = currentType->tp_bases;
    const Py_ssize_t numBases = PyTuple_Size(bases);
    bool result = false;
    for (Py_ssize_t i = 0; !result && i < numBases; ++i) {
        auto *type = reinterpret_cast<PyTypeObject *>(PyTuple_GetItem(bases, i));
        if (PyType_IsSubtype(type, SbkObject_TypeF()) != 0) {
            result = PepType_SOTP(type)->is_user_type
                     ? walkThroughBases(type, predicate) : predicate(type);
        }
    }
    return result;
}

int getTypeIndexOnHierarchy(PyTypeObject *baseType, PyTypeObject *desiredType)
{
    int index = -1;
    walkThroughBases(baseType, [&index, desiredType](PyTypeObject *node) {
        ++index;
        return PyType_IsSubtype(node, desiredType) != 0;
    });
    return index;
}

int getNumberOfCppBaseClasses(PyTypeObject *baseType)
{
    int count = 0;
    walkThroughBases(baseType, [&count](PyTypeObject *) {
        ++count;
        return false;
    });
    return count;
}

std::vector<PyTypeObject *> getCppBaseClasses(PyTypeObject *baseType)
{
    std::vector<PyTypeObject *> cppBaseClasses;
    walkThroughBases(baseType, [&cppBaseClasses](PyTypeObject *node) {
        cppBaseClasses.push_back(node);
        return false;
    });
    return cppBaseClasses;
}

using DestructorEntries = std::vector<DestructorEntry>;

// The destructor functions of one type, in the order the cptr array uses.
// Type-invariant: only the instance pointers differ, so this can be gathered
// before a state-lock transaction and zipped with cptr inside it. That is
// what keeps walkThroughBases() - which reads tp_bases and calls
// PyType_IsSubtype() - off the locked path.
using DestructorFunctions = std::vector<ObjectDestructor>;

#ifdef Py_GIL_DISABLED
// Only the free-threaded destruction path gathers them ahead of its
// transaction; with a GIL the destructors are read where they are used.
static DestructorFunctions getDestructorFunctions(PyTypeObject *type)
{
    DestructorFunctions result;
    walkThroughBases(type, [&result](PyTypeObject *node) {
        result.push_back(PepType_SOTP(node)->cpp_dtor);
        return false;
    });
    return result;
}
#endif // Py_GIL_DISABLED

DestructorEntries getDestructorEntries(SbkObject *o)
{
    DestructorEntries result;
    void **cptrs = o->d->cptr;
    walkThroughBases(Shiboken::pyType(o), [&result, cptrs](PyTypeObject *node) {
        auto *sotp = PepType_SOTP(node);
        auto index = result.size();
        result.push_back(DestructorEntry{sotp->cpp_dtor,
                                         cptrs[index]});
        return false;
    });
    return result;
}

static void callDestructor(const DestructorEntries &dts)
{
    for (const auto &e : dts) {
        Shiboken::ThreadStateSaver threadSaver;
        threadSaver.save();
        e.destructor(e.cppInstance);
    }
}

} // namespace Shiboken

extern "C"
{

// PYSIDE-939: A general replacement for object_dealloc.
void Sbk_object_dealloc(PyObject *self)
{
    // PYSIDE-939: Handling references correctly.
    // This was not needed before Python 3.8 (Python issue 35810)
    Py_DECREF(Py_TYPE(self));

    PepExt_TypeCallFree(self);
}

static void SbkObjectType_tp_dealloc(PyTypeObject *type);
static PyTypeObject *SbkObjectType_tp_new(PyTypeObject *metatype, PyObject *args, PyObject *kwds);

static DestroyQAppHook DestroyQApplication = nullptr;

// PYSIDE-1470: Provide a hook to kill an Application from Shiboken.
void setDestroyQApplication(DestroyQAppHook func)
{
    DestroyQApplication = func;
}

#ifdef Py_GIL_DISABLED
// The instance dict pointer, which CPython's generic attribute code reads
// and writes too.
// See "The instance dictionary is published once" in the free-threading notes.
static PyObject *loadDictAcquire(PyObject **field)
{
#  ifndef Py_LIMITED_API
    return static_cast<PyObject *>(_Py_atomic_load_ptr_acquire(field));
#  else
    return *field;
#  endif
}

static void storeDictRelease(PyObject **field, PyObject *dict)
{
#  ifndef Py_LIMITED_API
    _Py_atomic_store_ptr_release(field, dict);
#  else
    *field = dict;
#  endif
}
#endif // Py_GIL_DISABLED

// PYSIDE-535: Use the C API in PyPy instead of `op->ob_dict`, directly
LIBSHIBOKEN_API PyObject *SbkObject_GetDict_NoRef(PyObject *op)
{
    assert(Shiboken::Object::checkType(op));
#ifdef PYPY_VERSION
    Shiboken::GilState state;
    auto *ret = PyObject_GenericGetDict(op, nullptr);
    Py_DECREF(ret);
    return ret;
#else
    auto *sbkObj = reinterpret_cast<SbkObject *>(op);
#  ifdef Py_GIL_DISABLED
    // Created as CPython creates a tp_dictoffset dict, and never replaced, so
    // the borrow lasts as long as the wrapper.
    // See "The instance dictionary is published once" in the free-threading notes.
    if (Shiboken::FreeThreading::optionEnabled(Shiboken::FreeThreading::DictPublishOnce)) {
        PyObject *dict = loadDictAcquire(&sbkObj->ob_dict);
        if (dict == nullptr) {
            Shiboken::GilState state;
            SBK_FAILPOINT("dict-before-publish");
            PyCriticalSection section;
            PyCriticalSection_Begin(&section, op);
            dict = sbkObj->ob_dict;
            if (dict == nullptr) {
                dict = PyDict_New();
                storeDictRelease(&sbkObj->ob_dict, dict);
            }
            PyCriticalSection_End(&section);
        }
        return dict;
    }
    // DictPublishOnce cleared: a plain test and store.
    if (!sbkObj->ob_dict) {
        Shiboken::GilState state;
        SBK_FAILPOINT("dict-before-publish");
        sbkObj->ob_dict = PyDict_New();
    }
    return sbkObj->ob_dict;
#  else
    if (!sbkObj->ob_dict) {
        Shiboken::GilState state;
        sbkObj->ob_dict = PyDict_New();
    }
    return sbkObj->ob_dict;
#  endif
#endif
}

static int
check_set_special_type_attr(PyTypeObject *type, PyObject *value, const char *name)
{
    if (!(type->tp_flags & Py_TPFLAGS_HEAPTYPE)) {
        PyErr_Format(PyExc_TypeError,
                     "can't set %s.%s", type->tp_name, name);
        return 0;
    }
    if (!value) {
        PyErr_Format(PyExc_TypeError,
                     "can't delete %s.%s", type->tp_name, name);
        return 0;
    }
    return 1;
}

// PYSIDE-1177: Add a setter to allow setting type doc.
static int
type_set_doc(PyObject *obType, PyObject *value, void * /* context */)
{
    auto *type = reinterpret_cast<PyTypeObject *>(obType);
    if (!check_set_special_type_attr(type, value, "__doc__"))
        return -1;
    PyType_Modified(type);
    Shiboken::AutoDecRef tpDict(PepType_GetDict(type));
    return PyDict_SetItem(tpDict.object(), Shiboken::PyMagicName::doc(), value);
}

// PYSIDE-908: The function PyType_Modified does not work in PySide, so we need to
// explicitly pass __doc__.
static PyGetSetDef SbkObjectType_tp_getset[] = {
    {"__doc__",  Sbk_TypeGet___doc__, type_set_doc, nullptr, nullptr},
    {"__dict__",  Sbk_TypeGet___dict__, nullptr, nullptr, nullptr},
    {nullptr, nullptr, nullptr, nullptr, nullptr}  // Sentinel
};

static PyTypeObject *createObjectTypeType()
{
    PyType_Slot SbkObjectType_Type_slots[] = {
        {Py_tp_dealloc, reinterpret_cast<void *>(SbkObjectType_tp_dealloc)},
        {Py_tp_getattro, reinterpret_cast<void *>(mangled_type_getattro)},
        {Py_tp_base, static_cast<void *>(&PyType_Type)},
        {Py_tp_alloc, reinterpret_cast<void *>(PyType_GenericAlloc)},
        {Py_tp_new, reinterpret_cast<void *>(SbkObjectType_tp_new)},
        {Py_tp_free, reinterpret_cast<void *>(PyObject_GC_Del)},
        {Py_tp_getset, reinterpret_cast<void *>(SbkObjectType_tp_getset)},
        {0, nullptr}
    };

    // PYSIDE-535: The tp_itemsize field is inherited and does not need to be set.
    //             In PyPy, it _must_ not be set, because it would have the meanin
    //             that a `__len__` field must be defined. Not doing so creates
    //             a hard-to-find crash.
    //
    // PYSIDE-2230: In Python < 3.12, the decision which base class should create
    //              the instance is arbitrarily drawn by the size of the type.
    //              Ignoring this creates a bug in the new version of bug_825 that
    //              selects the wrong metatype.
    //
    PyType_Spec SbkObjectType_Type_spec = {
#if SHIBOKEN_MAJOR_VERSION >= 7 // PYSIDE-3336
        "2:shiboken6.Shiboken.ObjectType",
#else
        "1:Shiboken.ObjectType",
#endif
        static_cast<int>(PyType_Type.tp_basicsize) + 1,           // see above
        0, // sizeof(PyMemberDef), not for PyPy without a __len__ defined
        Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE|Py_TPFLAGS_TYPE_SUBCLASS,
        SbkObjectType_Type_slots,
    };

    PyType_Spec SbkObjectType_Type_spec_312 = {
#if SHIBOKEN_MAJOR_VERSION >= 7 // PYSIDE-3336
        "2:shiboken6.Shiboken.ObjectType",
#else
        "1:Shiboken.ObjectType",
#endif
        -long(sizeof(SbkObjectTypePrivate)),
        0, // sizeof(PyMemberDef), not for PyPy without a __len__ defined
        Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE|Py_TPFLAGS_TYPE_SUBCLASS,
        SbkObjectType_Type_slots,
    };

    return SbkType_FromSpec(_PepRuntimeVersion() >= 0x030C00 ?
                            &SbkObjectType_Type_spec_312 :
                            &SbkObjectType_Type_spec);
}

PyTypeObject *SbkObjectType_TypeF(void)
{
    auto *globals = baseWrapperGlobals();
    if (globals->sbkObjectMetaType == nullptr)
        globals->sbkObjectMetaType = createObjectTypeType();
    return globals->sbkObjectMetaType;
}

static PyObject *SbkObjectGetDict(PyObject *pObj, void *)
{
    auto *ret = SbkObject_GetDict_NoRef(pObj);
    Py_XINCREF(ret);
    return ret;
}

static PyGetSetDef SbkObject_tp_getset[] = {
    {const_cast<char *>("__dict__"), SbkObjectGetDict, nullptr, nullptr, nullptr},
    {nullptr, nullptr, nullptr, nullptr, nullptr} // Sentinel
};

static int SbkObject_tp_traverse(PyObject *self, visitproc visit, void *arg)
{
    auto *sbkSelf = reinterpret_cast<SbkObject *>(self);

    //Visit children
    if (auto *pInfo = sbkSelf->d->parentInfo) {
        for (SbkObject *c : pInfo->children)
             Py_VISIT(c);
    }

    //Visit refs
    if (auto *rInfo = sbkSelf->d->referredObjects) {
        for (const auto &p : *rInfo)
            Py_VISIT(p.second);
    }

    if (sbkSelf->ob_dict)
        Py_VISIT(sbkSelf->ob_dict);

    // This was not needed before Python 3.9 (Python issue 35810 and 40217)
    Py_VISIT(Py_TYPE(self));
    return 0;
}

static int SbkObject_tp_clear(PyObject *self)
{
    auto *sbkSelf = reinterpret_cast<SbkObject *>(self);

    // Only the children are detached here, never the link to our own C++
    // parent: that parent still holds this object in its C++ child list and
    // deletes it, so handing ownership back to Python would make the wrapper
    // delete it a second time. The reference cycle is broken by clearing the
    // instance dict below, and the parent link is torn down when the parent
    // itself is cleared or deallocated.
#ifdef Py_GIL_DISABLED
    // No precheck: parentInfo is published under the state lock, and every
    // helper below reads it there and does nothing without one.
    // See "Who may read parentInfo" in the free-threading notes.
    _detachChildren(sbkSelf, true);
#else
    if (sbkSelf->d->parentInfo)
        _detachChildren(sbkSelf, true);
#endif

    Shiboken::Object::clearReferences(sbkSelf);

#ifdef Py_GIL_DISABLED
    // The contents go, which breaks the cycle; the dict stays until the
    // wrapper is freed.
    // See "The instance dictionary is published once" in the free-threading notes.
    SBK_FAILPOINT("clear-before-dict");
    if (Shiboken::FreeThreading::optionEnabled(Shiboken::FreeThreading::DictPublishOnce)) {
        if (PyObject *dict = loadDictAcquire(&sbkSelf->ob_dict))
            PyDict_Clear(dict);
        return 0;
    }
#endif
    if (sbkSelf->ob_dict)
        Py_CLEAR(sbkSelf->ob_dict);
    return 0;
}

static PyTypeObject *createObjectType()
{
    PyType_Slot SbkObject_Type_slots[] = {
        {Py_tp_getattro, reinterpret_cast<void *>(SbkObject_GenericGetAttr)},
        {Py_tp_setattro, reinterpret_cast<void *>(SbkObject_GenericSetAttr)},
        {Py_tp_dealloc, reinterpret_cast<void *>(SbkDeallocWrapperWithPrivateDtor)},
        {Py_tp_traverse, reinterpret_cast<void *>(SbkObject_tp_traverse)},
        {Py_tp_clear, reinterpret_cast<void *>(SbkObject_tp_clear)},
        // unsupported: {Py_tp_weaklistoffset, (void *)offsetof(SbkObject, weakreflist)},
        {Py_tp_getset, reinterpret_cast<void *>(SbkObject_tp_getset)},
        // unsupported: {Py_tp_dictoffset, (void *)offsetof(SbkObject, ob_dict)},
        {0, nullptr}
    };

    PyType_Spec SbkObject_Type_spec = {
#if SHIBOKEN_MAJOR_VERSION >= 7 // PYSIDE-3336
        "2:shiboken6.Shiboken.Object",
#else
        "1:Shiboken.Object",
#endif
        sizeof(SbkObject),
        0,
        Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE|Py_TPFLAGS_HAVE_GC,
        SbkObject_Type_slots,
    };

    // PYSIDE-2230: When creating this type, we cannot easily handle the metaclass.
    //              In versions < Python 3.12, the metaclass can only be set
    //              indirectly by a base which has that metaclass.
    //              But before 3.12 is the minimum version, we cannot use the new
    //              function, although we would need this for 3.12 :-D
    //              We do a special patching here that is triggered through Py_None.
    auto *type = SbkType_FromSpec_BMDWB(&SbkObject_Type_spec,
                                        Py_None,     // bases, spectial flag!
                                        SbkObjectType_TypeF(),
                                        offsetof(SbkObject, ob_dict),
                                        offsetof(SbkObject, weakreflist),
                                        nullptr);    // bufferprocs
    return type;
}

PyTypeObject *SbkObject_TypeF(void)
{
    auto *globals = baseWrapperGlobals();
    if (globals->sbkObjectType == nullptr)
        globals->sbkObjectType = createObjectType();    // bufferprocs
    return globals->sbkObjectType;
}

static const char *SbkObject_SignatureStrings[] = {
    "Shiboken.Object(self)",
    nullptr}; // Sentinel

static int mainThreadDeletionHandler(void *)
{
    if (Py_IsInitialized())
        Shiboken::BindingManager::instance().runDeletionInMainThread();
    return 0;
}

#ifdef Py_GIL_DISABLED
namespace Shiboken::Object {
// A child whose C++ instance the parent's destructor is about to delete, and
// what a tombstone for it needs. Both the wrapper and its type are pinned:
// running the invalidation plan decrefs, and the child can otherwise be gone
// before the destructor that frees its C++ instance has even run.
struct DyingChild
{
    SbkObject *wrapper;
    PyTypeObject *type;
    std::vector<void *> cptrs;
};

// Defined with the other state-lock transactions, declared here: both
// destruction paths need it, and this is the first of them.
static std::vector<DyingChild> collectDyingChildren(SbkObject *root);

// A deallocation whose destructor waits for the last lease in its owned set.
// The wrapper is freed by then and is a key only; the lease holders are
// pinned, because the edges that led to them are gone.
// See "The deallocator claims the owned set" in the free-threading notes.
struct PendingDealloc
{
    SbkObject *wrapper;
    PyTypeObject *type; // a reference
    bool multicpp;
    bool deleteInMainThread;
    Shiboken::DestructorEntries entries;
    Shiboken::DestructorEntry entry;
    std::vector<void *> retiredCptrs;
    std::vector<DyingChild> children;
    std::vector<SbkObject *> busy; // references
    std::vector<SbkObject *> stamped; // references
};

static bool claimDeallocLocked(SbkObject *self, PendingDealloc &pending);
static void releaseDeallocStamps(const std::vector<SbkObject *> &stamped);
static void releaseDeallocStampsInMainThread(std::vector<SbkObject *> &&stamped);
} // namespace Shiboken::Object

// Free-threaded twin of the deallocation path. Kept here, not in the
// state-lock chapter, because it is static and used a few lines down. It
// follows the twin below step for step, apart from the transactions and the
// __APPLE__ diagnostic, which is not worth having twice.
static void SbkDeallocWrapperCommon(PyObject *pyObj, bool canDelete)
{
    SBK_ASSERT_STATE_UNLOCKED();
    SBK_ASSERT_NO_RAW_LOCK();
    auto *sbkObj = reinterpret_cast<SbkObject *>(pyObj);
    PyTypeObject *pyType = Py_TYPE(pyObj);

    // Need to decref the type if this is the dealloc func; if type
    // is subclassed, that dealloc func will decref (see subtype_dealloc
    // in typeobject.c in the python sources)
    auto *dealloc = PyType_GetSlot(pyType, Py_tp_dealloc);

    // PYSIDE-939: Additional rule: Also when a subtype is heap allocated,
    // then the subtype_dealloc deref will be suppressed, and we need again
    // to supply a decref.
    const bool needTypeDecref = dealloc == SbkDeallocWrapper
        || dealloc == SbkDeallocWrapperWithPrivateDtor
        || (pyType->tp_base->tp_flags & Py_TPFLAGS_HEAPTYPE) != 0;

    // Ensure that the GC is no longer tracking this object to avoid a
    // possible reentrancy problem.  Since there are multiple steps involved
    // in deallocating a SbkObject it is possible for the garbage collector to
    // be invoked and it trying to delete this object while it is still in
    // progress from the first time around, resulting in a double delete and a
    // crash.
    PyObject_GC_UnTrack(pyObj);

    // What this deallocation is going to destroy, decided before anything
    // below can run Python. It used to be read further down, after the map
    // entry was already dealt with, and the entry cannot be dealt with
    // correctly without knowing it.
    auto &bindingManager = Shiboken::BindingManager::instance();
    auto *sotp = PepType_SOTP(pyType);
    const int numBases = sotp->is_multicpp
        ? Shiboken::getNumberOfCppBaseClasses(pyType) : 1;
    // Gathered before the lock: the walk reads tp_bases and calls
    // PyType_IsSubtype(), and the state lock stays a leaf.
    const auto dtors = sotp->is_multicpp ? Shiboken::getDestructorFunctions(pyType)
                                         : Shiboken::DestructorFunctions{};
    Shiboken::DestructorEntries entries;
    void *cptr = nullptr;
    std::vector<void *> retiredCptrs;
    {
        // Read-only: at refcount zero nobody else is here, but the lock owns
        // these fields. Only the instance pointers are read here; the
        // destructors come from the list gathered above.
        Shiboken::StateLockGuard guard;
        auto *priv = sbkObj->d;
        // destroy() and callCppDestructors() detach cptr under this lock, so a
        // wrapper that went through them arrives with none.
        canDelete &= priv->hasOwnership && priv->validCppObject && priv->cptr != nullptr;
        if (canDelete) {
            retiredCptrs.assign(priv->cptr, priv->cptr + numBases);
            if (sotp->is_multicpp) {
                entries.reserve(dtors.size());
                for (size_t i = 0; i < dtors.size(); ++i)
                    entries.push_back(Shiboken::DestructorEntry{dtors[i], priv->cptr[i]});
            } else {
                cptr = priv->cptr[0];
            }
        }
    }

    // Take the object out of the wrapper map before anything below can run
    // Python code. The refcount is already zero here, but the map used to keep
    // the entry until deallocData(), several steps down. A lookup in between -
    // a weakref callback, a __del__, C++ re-entering the binding - was handed
    // this very wrapper and increfed it back to life, while the deallocation
    // carried on and freed it underneath. The invariant callers rely on is
    // "in the map implies alive", and this is where it has to be restored.
    //
    // Where a C++ object is going to be destroyed, the entry does not go: it
    // becomes a tombstone, because between removing it and the destructor
    // below a lookup saw true absence and published a wrapper for an object
    // about to die. A tombstone stands for a destruction that is going to
    // happen - a wrapper that owns nothing destroys nothing, and there the
    // entry is removed the way it always was, so a conversion of that address
    // gets the fresh, valid wrapper it should. The same goes for the owned
    // children: their entries are released inside deallocData() and the
    // destructor deletes them a step later.
    std::vector<Shiboken::Object::DyingChild> children;
    const bool tombstones = canDelete
        && Shiboken::FreeThreading::optionEnabled(Shiboken::FreeThreading::Tombstones);
    if (tombstones) {
        children = Shiboken::Object::collectDyingChildren(sbkObj);
        bindingManager.markWrapperDying(sbkObj);
        for (const auto &child : children)
            bindingManager.markWrapperDying(child.wrapper, child.cptrs.data());
    } else {
        // Also the A/B side: with Tombstones cleared the entry goes the way
        // it went before, so a test can watch the window come back.
        retiredCptrs.clear();
        bindingManager.unregisterWrapper(sbkObj);
    }

    // Check that Python is still initialized as sometimes this is called by a static destructor
    // after Python interpeter is shutdown.
    SBK_FAILPOINT("dealloc-before-weakrefs");
    // PyObject_ClearWeakRefs() checks the list itself, under its lock.
    // See "The weakref list head is CPython's" in the free-threading notes.
    if (Py_IsInitialized())
        PyObject_ClearWeakRefs(pyObj);

    SBK_FAILPOINT("dealloc-before-destroy");

    bool deferredDeletion = false;
    std::vector<SbkObject *> stamped;
    // The destructor takes the owned set along: no new lease from here, and
    // a lease still open gets the destructor.
    // See "The deallocator claims the owned set" in the free-threading notes.
    if (canDelete
        && Shiboken::FreeThreading::optionEnabled(Shiboken::FreeThreading::DeallocClaim)) {
        Shiboken::Object::PendingDealloc pending{sbkObj, pyType, sotp->is_multicpp != 0,
                                                 sotp->delete_in_main_thread != 0,
                                                 std::move(entries), {sotp->cpp_dtor, cptr},
                                                 std::move(retiredCptrs), std::move(children),
                                                 {}, {}};
        bool handedToLease = false;
        {
            Shiboken::StateLockGuard guard;
            handedToLease = Shiboken::Object::claimDeallocLocked(sbkObj, pending);
        }
        if (handedToLease) {
            canDelete = false;
            deferredDeletion = true;
        } else {
            entries = std::move(pending.entries);
            retiredCptrs = std::move(pending.retiredCptrs);
            children = std::move(pending.children);
            stamped = std::move(pending.stamped);
        }
    }

    if (canDelete && sotp->delete_in_main_thread
        && Shiboken::currentThreadId() != Shiboken::mainThreadId()) {
        if (sotp->is_multicpp) {
            for (const auto &e : entries)
                bindingManager.addToDeletionInMainThread(e);
        } else {
            bindingManager.addToDeletionInMainThread({sotp->cpp_dtor, cptr});
        }
        // The retirements go into the same queue right here, directly behind
        // the destructors they wait for. Queued after deallocData() they can
        // miss it altogether: deallocData() runs Python, and the main thread
        // may drain everything queued so far while it does - the tombstone
        // would then stand over an address whose destructor has already run,
        // and refuse it until a second drain comes past.
        if (!retiredCptrs.empty())
            bindingManager.retireAfterDeletionInMainThread(sbkObj, retiredCptrs, pyType);
        for (const auto &child : children) {
            bindingManager.retireAfterDeletionInMainThread(child.wrapper, child.cptrs,
                                                           child.type);
        }
        if (!stamped.empty())
            Shiboken::Object::releaseDeallocStampsInMainThread(std::move(stamped));
        Py_AddPendingCall(mainThreadDeletionHandler, nullptr);
        canDelete = false;
        deferredDeletion = true;
    }

    /* Save the current exception, if any. */
    Shiboken::Errors::Stash errorStash;

    // deallocData() frees the wrapper, so everything the destructors need was
    // read above.
    Shiboken::Object::deallocData(sbkObj, true);

    // The tombstone's window: the wrapper is gone, the C++ object is not.
    SBK_FAILPOINT("dealloc-before-cpp-dtor");

    if (canDelete) {
        if (sotp->is_multicpp) {
            callDestructor(entries);
        } else {
            Shiboken::ThreadStateSaver threadSaver;
            if (Py_IsInitialized())
                threadSaver.save();
            sotp->cpp_dtor(cptr);
        }
    }

    /* Restore the saved exception. */
    errorStash.restore();

    // The tombstones fall here: past the destructor for an owning wrapper,
    // past deallocData() for a non-owning one. Either way this lifecycle can
    // no longer destroy anything at those addresses, so a wrapper published
    // from now on is a wrapper for whatever lives there next. The exception
    // is a destructor handed to the main thread - that one has not run yet,
    // so its tombstone travels with it. sbkObj is a key from here on, and is
    // not dereferenced: deallocData() freed it.
    // The other side of the window above: the C++ object is gone, the
    // tombstone still stands, and a conversion that the dying-conversion
    // exception lets through here is one nothing outside this file could
    // ever invalidate.
    SBK_FAILPOINT("dealloc-before-retire");

    if (!deferredDeletion) {
        if (!retiredCptrs.empty())
            bindingManager.retireWrapper(sbkObj, retiredCptrs.data(), pyType);
        for (const auto &child : children)
            bindingManager.retireWrapper(child.wrapper, child.cptrs.data(), child.type);
        Shiboken::Object::releaseDeallocStamps(stamped);
    }
    // The child pins go back last and with no lock held: this can be a
    // child's final reference, and its deallocator re-enters the binding
    // layer. Its own entry is a tombstone by then and it owns nothing, so
    // that deallocation takes neither of the two branches above.
    for (const auto &child : children) {
        Py_DECREF(reinterpret_cast<PyObject *>(child.wrapper));
        Py_DECREF(reinterpret_cast<PyObject *>(child.type));
    }

    if (needTypeDecref)
        Py_DECREF(pyType);
    // PYSIDE-939: Handling references correctly.
    // This was not needed before Python 3.8 (Python issue 35810)
    Py_DECREF(pyType);
}
#else // Py_GIL_DISABLED
static void SbkDeallocWrapperCommon(PyObject *pyObj, bool canDelete)
{
    auto *sbkObj = reinterpret_cast<SbkObject *>(pyObj);
    PyTypeObject *pyType = Py_TYPE(pyObj);

    // Need to decref the type if this is the dealloc func; if type
    // is subclassed, that dealloc func will decref (see subtype_dealloc
    // in typeobject.c in the python sources)
    auto *dealloc = PyType_GetSlot(pyType, Py_tp_dealloc);

    // PYSIDE-939: Additional rule: Also when a subtype is heap allocated,
    // then the subtype_dealloc deref will be suppressed, and we need again
    // to supply a decref.
    const bool needTypeDecref = dealloc == SbkDeallocWrapper
        || dealloc == SbkDeallocWrapperWithPrivateDtor
        || (pyType->tp_base->tp_flags & Py_TPFLAGS_HEAPTYPE) != 0;

#ifdef __APPLE__
    // Just checking once that our assumptions are right.
    if (false) {
        void *p = PyType_GetSlot(pyType, Py_tp_dealloc);
        Dl_info dl_info;
        dladdr(p, &dl_info);
        fprintf(stderr, "tp_dealloc is %s\n", dl_info.dli_sname);
    }
    // Gives one of our functions
    //  "Sbk_object_dealloc"
    //  "SbkDeallocWrapperWithPrivateDtor"
    //  "SbkDeallocQAppWrapper"
    //  "SbkDeallocWrapper"
    // but for typedealloc_test.py we get
    //  "subtype_dealloc"
#endif

    // Ensure that the GC is no longer tracking this object to avoid a
    // possible reentrancy problem.  Since there are multiple steps involved
    // in deallocating a SbkObject it is possible for the garbage collector to
    // be invoked and it trying to delete this object while it is still in
    // progress from the first time around, resulting in a double delete and a
    // crash.
    PyObject_GC_UnTrack(pyObj);

    // Take the object out of the wrapper map before anything below can run
    // Python code. The refcount is already zero here, but the map used to keep
    // the entry until deallocData(), several steps down. A lookup in between -
    // a weakref callback, a __del__, C++ re-entering the binding - was handed
    // this very wrapper and increfed it back to life, while the deallocation
    // carried on and freed it underneath. The invariant callers rely on is
    // "in the map implies alive", and this is where it has to be restored.
    // Only the entry goes; the flags stay, canDelete below still reads them.
    auto &bindingManager = Shiboken::BindingManager::instance();
    bindingManager.unregisterWrapper(sbkObj);

    // Check that Python is still initialized as sometimes this is called by a static destructor
    // after Python interpeter is shutdown.
    if (sbkObj->weakreflist && Py_IsInitialized())
        PyObject_ClearWeakRefs(pyObj);

    // If I have ownership and is valid delete C++ pointer
    auto *sotp = PepType_SOTP(pyType);
    canDelete &= sbkObj->d->hasOwnership && sbkObj->d->validCppObject;
    if (canDelete) {
        if (sotp->delete_in_main_thread && Shiboken::currentThreadId() != Shiboken::mainThreadId()) {
            if (sotp->is_multicpp) {
                 const auto entries = Shiboken::getDestructorEntries(sbkObj);
                 for (const auto &e : entries)
                     bindingManager.addToDeletionInMainThread(e);
            } else {
                Shiboken::DestructorEntry e{sotp->cpp_dtor, sbkObj->d->cptr[0]};
                bindingManager.addToDeletionInMainThread(e);
            }
            Py_AddPendingCall(mainThreadDeletionHandler, nullptr);
            canDelete = false;
        }
    }

    /* Save the current exception, if any. */
    Shiboken::Errors::Stash errorStash;

    if (canDelete) {
        if (sotp->is_multicpp) {
            const auto entries = Shiboken::getDestructorEntries(sbkObj);
            Shiboken::Object::deallocData(sbkObj, true);
            callDestructor(entries);
        } else {
            void *cptr = sbkObj->d->cptr[0];
            Shiboken::Object::deallocData(sbkObj, true);

            Shiboken::ThreadStateSaver threadSaver;
            if (Py_IsInitialized())
                threadSaver.save();
            sotp->cpp_dtor(cptr);
        }
    } else {
        Shiboken::Object::deallocData(sbkObj, true);
    }

    /* Restore the saved exception. */
    errorStash.restore();

    if (needTypeDecref)
        Py_DECREF(pyType);
    // PYSIDE-939: Handling references correctly.
    // This was not needed before Python 3.8 (Python issue 35810)
    Py_DECREF(pyType);
}
#endif // Py_GIL_DISABLED

static inline PyObject *_Sbk_NewVarObject(PyTypeObject *type)
{
    // PYSIDE-1970: Support __slots__, implemented by PyVarObject
    auto const baseSize = sizeof(SbkObject);
    auto varCount = Py_SIZE(reinterpret_cast<PyObject *>(type));
    auto *self = PyObject_GC_NewVar(PyObject, type, varCount);
    if (varCount)
        std::memset(reinterpret_cast<char *>(self) + baseSize, 0, varCount * sizeof(void *));
    return self;
}

void SbkDeallocWrapper(PyObject *pyObj)
{
    SbkDeallocWrapperCommon(pyObj, true);
}

void SbkDeallocQAppWrapper(PyObject *pyObj)
{
    SbkDeallocWrapper(pyObj);
    // PYSIDE-571: make sure to create a singleton deleted qApp.
    Py_DECREF(MakeQAppWrapper(nullptr));
}

void SbkDeallocWrapperWithPrivateDtor(PyObject *self)
{
    SbkDeallocWrapperCommon(self, false);
}

void SbkObjectType_tp_dealloc(PyTypeObject *type)
{
    SbkObjectTypePrivate *sotp = PepType_SOTP(type);
    auto *pyObj = reinterpret_cast<PyObject *>(type);

    PyObject_GC_UnTrack(pyObj);
#if !defined(Py_LIMITED_API) && !defined(PYPY_VERSION)
    Py_TRASHCAN_BEGIN(pyObj, 1);
#endif
    if (sotp) {
        if (sotp->user_data && sotp->d_func) {
            sotp->d_func(sotp->user_data);
            sotp->user_data = nullptr;
        }
        free(sotp->original_name);
        sotp->original_name = nullptr;
        if (!Shiboken::ObjectType::isUserType(type))
            Shiboken::Conversions::deleteConverter(sotp->converter);
        PepType_SOTP_delete(type);
    }
#if !defined(Py_LIMITED_API) && !defined(PYPY_VERSION)
    Py_TRASHCAN_END;
#endif
    // PYSIDE-939: Handling references correctly.
    // This was not needed before Python 3.8 (Python issue 35810)
    Py_DECREF(Py_TYPE(pyObj));
}

////////////////////////////////////////////////////////////////////////////
//
// Support for the qApp macro.
//
// qApp is a macro in Qt5. In Python, we simulate that a little by a
// variable that monitors Q*Application.instance().
// This variable is also able to destroy the app by qApp.shutdown().
//

PyObject *MakeQAppWrapper(PyTypeObject *type)
{
    PyObject *&qApp_last = baseWrapperGlobals()->qAppLast;

    // protecting from multiple application instances
    if (type != nullptr && qApp_last != Py_None) {
        const char *res_name = qApp_last != nullptr
            ? PepType_GetNameStr(Py_TYPE(qApp_last)) : "<Unknown>";
        const char *type_name = PepType_GetNameStr(type);
        PyErr_Format(PyExc_RuntimeError,
                     "libshiboken: Please destroy the %s singleton before"
                     " creating a new %s instance.", res_name, type_name);
        return nullptr;
    }

    // monitoring the last application state
    PyObject *qApp_curr = type != nullptr ? _Sbk_NewVarObject(type) : Py_None;
    Shiboken::AutoDecRef builtins(PepEval_GetFrameBuiltins());
    if (PyDict_SetItem(builtins.object(), Shiboken::PyName::qApp(), qApp_curr) < 0)
        return nullptr;
    builtins.reset(nullptr);
    qApp_last = qApp_curr;
    // Note: This Py_INCREF would normally be wrong because the qApp
    // object already has a reference from PyObject_GC_New. But this is
    // exactly the needed reference that keeps qApp alive from alone!
    Py_INCREF(qApp_curr);
    // PYSIDE-1470: As a side effect, the interactive "_" variable tends to
    //              create reference cycles. This is disturbing when trying
    //              to remove qApp with del.
    // PYSIDE-1758: Since we moved to an explicit qApp.shutdown() call, we
    //              no longer initialize "_" with Py_None.
    return qApp_curr;
}

static PyTypeObject *SbkObjectType_tp_new(PyTypeObject *metatype, PyObject *args, PyObject *kwds)
{
    // Check if all bases are new style before calling type.tp_new
    // Was causing gc assert errors in test_bug704.py when
    // this check happened after creating the type object.
    // Argument parsing take from type.tp_new code.

    // PYSIDE-595: Also check if all bases allow inheritance.
    // Before we changed to heap types, it was sufficient to remove the
    // Py_TPFLAGS_BASETYPE flag. That does not work, because PySide does
    // not respect this flag itself!
    PyObject *name{};
    PyObject *pyBases{};
    PyObject *dict{};
    static const char *kwlist[] = { "name", "bases", "dict", nullptr};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OO!O!:sbktype", const_cast<char **>(kwlist),
                                     &name,
                                     &PyTuple_Type, &pyBases,
                                     &PyDict_Type, &dict))
        return nullptr;

    for (Py_ssize_t i=0, i_max=PyTuple_Size(pyBases); i < i_max; i++) {
        PyObject *baseType = PyTuple_GetItem(pyBases, i);
        if (PepExt_Type_GetNewSlot(reinterpret_cast<PyTypeObject *>(baseType)) == SbkDummyNew) {
            // PYSIDE-595: A base class does not allow inheritance.
            return reinterpret_cast<PyTypeObject *>(SbkDummyNew(metatype, args, kwds));
        }
    }

    PyTypeObject *newType = PepType_Type_tp_new(metatype, args, kwds);

    if (!newType)
        return nullptr;

    SbkObjectTypePrivate *sotp = PepType_SOTP(newType);

    const auto bases = Shiboken::getCppBaseClasses(newType);
    if (bases.size() == 1) {
        SbkObjectTypePrivate *parentType = PepType_SOTP(bases.front());
        sotp->mi_init = parentType->mi_init;
        sotp->mi_specialcast = parentType->mi_specialcast;
        sotp->type_discovery = parentType->type_discovery;
        sotp->cpp_dtor = parentType->cpp_dtor;
        sotp->is_multicpp = 0;
        sotp->converter = parentType->converter;
    } else {
        sotp->mi_init = nullptr;
        sotp->mi_specialcast = nullptr;
        sotp->type_discovery = nullptr;
        sotp->cpp_dtor = nullptr;
        sotp->is_multicpp = 1;
        sotp->converter = nullptr;
    }
    if (bases.size() == 1) {
        const char *original_name = PepType_SOTP(bases.front())->original_name;
        if (original_name == nullptr)
            original_name = "object";
        sotp->original_name = strdup(original_name);
    }
    else
        sotp->original_name = strdup("object");
    sotp->user_data = nullptr;
    sotp->d_func = nullptr;
    sotp->is_user_type = 1;

    // PYSIDE-1463: Prevent feature switching while in the creation process
    auto saveFeature = initSelectableFeature(nullptr);
    for (PyTypeObject *base : bases) {
        sotp = PepType_SOTP(base);
        if (sotp->subtype_init)
            sotp->subtype_init(newType, args, kwds);
    }
    initSelectableFeature(saveFeature);
    return newType;
}

static PyObject *_setupNew(PyObject *obSelf, PyTypeObject *subtype)
{
    auto *obSubtype = reinterpret_cast<PyObject *>(subtype);
    auto *sbkSubtype = subtype;
    auto *self = reinterpret_cast<SbkObject *>(obSelf);

    Py_INCREF(obSubtype);
    auto *d = new SbkObjectPrivate;

    auto *sotp = PepType_SOTP(sbkSubtype);
    int numBases = ((sotp && sotp->is_multicpp) ?
        Shiboken::getNumberOfCppBaseClasses(subtype) : 1);
    d->cptr = new void *[numBases];
    std::memset(static_cast<void*>(d->cptr), 0, sizeof(void *) *size_t(numBases));
    d->hasOwnership = true;
    d->containsCppWrapper = false;
    d->validCppObject = false;
    d->parentInfo = nullptr;
    d->referredObjects = nullptr;
    d->cppObjectCreated = false;
    d->isQAppSingleton = false;
#ifdef Py_GIL_DISABLED
    d->directDestruction = false;
    d->activeCalls = 0;
    d->constructingSlots = 0;
#endif
    self->ob_dict = nullptr;
    self->weakreflist = nullptr;
    self->d = d;
    PyObject_GC_Track(obSelf);
    return obSelf;
}

PyObject *SbkObject_tp_new(PyTypeObject *subtype, PyObject * /* args */, PyObject * /* kwds */)
{
    PyObject *self = _Sbk_NewVarObject(subtype);
    return _setupNew(self, subtype);
}

PyObject *SbkQApp_tp_new(PyTypeObject *subtype, PyObject *, PyObject *)
{
    auto *obSelf = MakeQAppWrapper(subtype);
    auto *self = reinterpret_cast<SbkObject *>(obSelf);
    if (self == nullptr)
        return nullptr;
    auto *ret = _setupNew(obSelf, subtype);
    self->d->isQAppSingleton = true;
    return ret;
}

PyObject *SbkDummyNew(PyTypeObject *type, PyObject *, PyObject *)
{
    // PYSIDE-595: Give the same error as type_call does when tp_new is NULL.
    const char regret[] = "¯\\_(ツ)_/¯";
    PyErr_Format(PyExc_TypeError,
                 "cannot create '%.100s' instances %s", type->tp_name, regret);
    return nullptr;
}

// PYSIDE-74: Fallback used in all types now.
PyObject *FallbackRichCompare(PyObject *self, PyObject *other, int op)
{
    // This is a very simple implementation that supplies a simple identity.
    static const char * const opstrings[] = {"<", "<=", "==", "!=", ">", ">="};
    PyObject *res{};

    switch (op) {

    case Py_EQ:
        res = (self == other) ? Py_True : Py_False;
        break;
    case Py_NE:
        res = (self != other) ? Py_True : Py_False;
        break;
    default:
        PyErr_Format(PyExc_TypeError,
                     "'%s' not supported between instances of '%.100s' and '%.100s'",
                     opstrings[op],
                     self->ob_type->tp_name,
                     other->ob_type->tp_name);
        return nullptr;
    }
    Py_INCREF(res);
    return res;
}

bool SbkObjectType_Check(PyTypeObject *type)
{
    auto *meta = SbkObjectType_TypeF();
    auto *obType = reinterpret_cast<PyObject *>(type);
    return Py_TYPE(obType) == meta || PyType_IsSubtype(Py_TYPE(obType), meta);
}

// Global functions from folding.

// The common end.
PyObject *Sbk_ReturnFromPython_None()
{
    if (Shiboken::Errors::occurred() != nullptr) {
        return {};
    }
    Py_RETURN_NONE;
}

PyObject *Sbk_ReturnFromPython_Result(PyObject *pyResult)
{
    if (Shiboken::Errors::occurred() != nullptr || pyResult == nullptr) {
        Py_XDECREF(pyResult);
        return {};
    }
    return pyResult;
}

PyObject *Sbk_ReturnFromPython_Self(PyObject *self)
{
    if (Shiboken::Errors::occurred() != nullptr) {
        return {};
    }
    Py_INCREF(self);
    return self;
}

} //extern "C"

// Determine name of a Python override of a virtual method according to features
// and populate name cache.
static PyObject *overrideMethodName(PyObject *pySelf, const char *methodName,
                                    Shiboken::CacheSlot *nameCache)
{
    // PYSIDE-1626: Touch the type to initiate switching early.
    auto *obType = Py_TYPE(pySelf);
    SbkObjectType_UpdateFeature(obType);

    const int flag = currentSelectId(obType);
    const int propFlag = isdigit(methodName[0]) ? methodName[0] - '0' : 0;
    const bool is_snake = flag & 0x01;
    PyObject *pyMethodName = nameCache[is_snake].get();  // borrowed
    if (pyMethodName == nullptr) {
        if (propFlag)
            methodName += 2; // skip the propFlag and ':'
        // getSnakeCaseName() interns, and interning hands out a new
        // reference every time: threads that lose the race here used to drop
        // theirs on the floor. publish() gives the slot to one of them and
        // releases the rest.
        pyMethodName = nameCache[is_snake].publish(
            Shiboken::String::getSnakeCaseName(methodName, is_snake));
    }
    return pyMethodName;
}

#ifdef Py_GIL_DISABLED
// Whether an unattached thread does address checks only. The A/B harness can
// take that away to show what happens without it.
static bool nativePreflight()
{
    return Shiboken::FreeThreading::optionEnabled(
        Shiboken::FreeThreading::NativePreflight);
}
#endif

// The virtual function call

PyObject *Sbk_GetPyOverride(const void *voidThis, PyTypeObject *typeObject,
                            Shiboken::GilState &gil, const char *funcName,
                            Shiboken::CacheSlot &resultCache,
                            Shiboken::CacheSlot *nameCache)
{
    if (Py_IsInitialized() == 0 || resultCache.get() == Py_None)
        return nullptr; // Bail out, execute C++ call (wrappers may outlive Python).

    auto &bindingManager = Shiboken::BindingManager::instance();
#ifdef Py_GIL_DISABLED
    // Address comparison only, so it needs no thread state - a virtual
    // arriving from a Qt thread has none yet. Narrowing by type happens after
    // the attach, in acquireWrapper() below. Not done on a build with a GIL,
    // where a borrow is safe.
    const bool present = nativePreflight()
        ? bindingManager.hasWrapper(voidThis)
        : bindingManager.hasWrapper(voidThis, typeObject);
    if (!present)
        return nullptr;

    gil.acquire();

    // A virtual call can arrive from a C++ destructor, so the wrapper may
    // already be dying; an empty result covers that as well as "gone in the
    // meantime". Needs the thread state taken just above, and for the same
    // reason every path below that calls gil.release() has to reset() this
    // first - letting it go is a decref.
    auto wrapperRef = bindingManager.acquireWrapper(voidThis, typeObject);
    if (wrapperRef.isNull()) {
        gil.release();
        return nullptr;
    }
    auto *wrapper = wrapperRef.object();
    auto *pySelf = wrapperRef.pyObject();
#else // Py_GIL_DISABLED
    SbkObject *wrapper = bindingManager.retrieveWrapper(voidThis, typeObject);
    // The refcount can be 0 if the object is dieing and someone called
    // a virtual method from the destructor
    if (wrapper == nullptr)
        return nullptr;
    auto *pySelf = reinterpret_cast<PyObject *>(wrapper);
    if (Py_REFCNT(pySelf) == 0)
        return nullptr;

    gil.acquire();
#endif // Py_GIL_DISABLED
    PyObject *cached = resultCache.get();
    if (cached == Py_None) { // PYSIDE 3246, some other thread may have determined the override
#ifdef Py_GIL_DISABLED
        wrapperRef.reset();
#endif
        gil.release();
        return nullptr;
    }

    if (cached != nullptr) // recreate the callable from function/self
        return PepExt_Type_CallDescrGet(cached, pySelf, nullptr);

    PyObject *pyMethodName = overrideMethodName(pySelf, funcName, nameCache);
    auto *wrapper_dict = SbkObject_GetDict_NoRef(pySelf);

    // Note: This special case was implemented for duck-punching, which happens
    // in the instance dict. It does not work with properties.
    // This is not cached to avoid leaking. FIXME PYSIDE 7: Remove (PYSIDE-2916)?
#ifdef Py_GIL_DISABLED
    if (PyObject *method = PepDict_GetItemOwned(wrapper_dict, pyMethodName))
        return method;

    auto *pyOverride = Shiboken::BindingManager::getOverride(wrapper, pyMethodName);
    if (pyOverride == nullptr) {
        // A failed mro lookup also answers nullptr, and the cache is
        // permanent for this object: cache "no override" only without an
        // error, or a passing failure disables the override for good.
        //
        // Under Py_GIL_DISABLED only. Errors::occurred() un-parks an error
        // that storeErrorOrPrint() stashed earlier, so asking here would move
        // the point at which a GIL build raises it - on the virtual dispatch
        // of every wrapper.
        if (Shiboken::Errors::occurred() == nullptr)
        {
            Py_INCREF(Py_None);
            resultCache.publish(Py_None);
        }
        wrapperRef.reset();
        gil.release();
        return nullptr; // No override, execute C++ call
    }
#else
    if (PyObject *method = PyDict_GetItem(wrapper_dict, pyMethodName)) {
        Py_INCREF(method);
        return method;
    }

    auto *pyOverride = Shiboken::BindingManager::getOverride(wrapper, pyMethodName);
    if (pyOverride == nullptr) {
        Py_INCREF(Py_None);
        resultCache.publish(Py_None);
        gil.release();
        return nullptr; // No override, execute C++ call
    }
#endif

    if (Shiboken::Errors::occurred() != nullptr) {
        // Give up.
        Py_XDECREF(pyOverride);
        Py_INCREF(Py_None);
        resultCache.publish(Py_None);
#ifdef Py_GIL_DISABLED
        wrapperRef.reset();
#endif
        gil.release();
        return nullptr; // // Give up.
    }

    // This call uses what it found, whoever wins the slot. They normally
    // agree, but not always: the attribute can be duck-punched or switched
    // between another thread's lookup and this one, and then the slot may
    // end up holding Py_None or a different callable. publish() takes the
    // reference from getOverride() and drops it again if it loses, so the
    // one taken here is what keeps the override alive across the call.
    Py_INCREF(pyOverride);
    resultCache.publish(pyOverride);
    // recreate the callable from function/self
    PyObject *result = PepExt_Type_CallDescrGet(pyOverride, pySelf, nullptr);
    Py_DECREF(pyOverride);
    return result;
}

namespace
{

#ifdef Py_GIL_DISABLED
// Invalidate and detach the children of obj. Their C++ instances belong to
// obj's C++ instance and are deleted by it, so no ownership is handed back.
void _detachChildren(SbkObject *obj, bool keepReference)
{
    SBK_ASSERT_STATE_UNLOCKED();
    // See "A teardown detaches the edge it read" in the free-threading notes.
    if (Shiboken::FreeThreading::optionEnabled(Shiboken::FreeThreading::DetachCheckedParent)) {
        while (Shiboken::Object::detachFirstChild(obj, keepReference)) {
        }
        return;
    }
    // DetachCheckedParent cleared: the pick and the removal are two
    // transactions, and a reparent in between loses its new edge.
    // One child per round, read inside a transaction: the container is the
    // one setParentLocked() and removeParentLocked() mutate. The loop body
    // must stay outside, because invalidate() and removeParent() take the
    // lock themselves and it is not recursive. The child is pinned for the
    // trip: nothing else keeps it alive once removeParent() has handed the
    // parent reference back.
    while (true) {
        SbkObject *first = nullptr;
        {
            Shiboken::StateLockGuard guard;
            Shiboken::ParentInfo *pInfo = obj->d->parentInfo;
            if (pInfo == nullptr || pInfo->children.empty())
                break;
            first = *pInfo->children.begin();
            // Still under the lock and still attached: the last moment at
            // which the child can be seen to derive obj's claim.
            keepClaimThroughTeardownLocked(first);
            Py_INCREF(reinterpret_cast<PyObject *>(first));
        }
        // Mark child as invalid
        Shiboken::Object::invalidate(first);
        SBK_FAILPOINT("detach-mid-round");
        Shiboken::Object::removeParent(first, false, keepReference);
        Py_DECREF(reinterpret_cast<PyObject *>(first));
    }
}
#else // Py_GIL_DISABLED
// Invalidate and detach the children of obj. Their C++ instances belong to
// obj's C++ instance and are deleted by it, so no ownership is handed back.
void _detachChildren(SbkObject *obj, bool keepReference)
{
    Shiboken::ParentInfo *pInfo = obj->d->parentInfo;
    if (pInfo) {
        while(!pInfo->children.empty()) {
            SbkObject *first = *pInfo->children.begin();
            // Mark child as invalid
            Shiboken::Object::invalidate(first);
            Shiboken::Object::removeParent(first, false, keepReference);
        }
    }
}
#endif // Py_GIL_DISABLED

void _destroyParentInfo(SbkObject *obj, bool keepReference)
{
#ifdef Py_GIL_DISABLED
    _detachChildren(obj, keepReference);
    Shiboken::Object::removeParent(obj, false);
#else
    if (obj->d->parentInfo) {
        _detachChildren(obj, keepReference);
        Shiboken::Object::removeParent(obj, false);
    }
#endif
}

}

namespace Shiboken
{

// Wrapper metatype and base type ----------------------------------------------------------

void _initMainThreadId(); // helper.cpp

static std::string msgFailedToInitializeType(const char *description)
{
    std::ostringstream stream;
    stream << "libshiboken: Failed to initialize " << description;
    if (PyErr_Occurred() != nullptr) {
        Shiboken::Errors::Stash stash;
        if (auto *str = PyObject_Str(stash.getException()))
            stream << ": " << Shiboken::String::toCString(str);
    }
    stream << '.';
    return stream.str();
}

namespace Conversions { void init(); }

void init()
{
    static bool shibokenAlreadInitialised = false;
    if (shibokenAlreadInitialised) // Leave guard in place until fully ported to multi phase init
        return;

    _initMainThreadId();

    Conversions::init();

    //Init private data
    Pep384_Init();

    auto *type = SbkObjectType_TypeF();
    if (type == nullptr || PyType_Ready(type) < 0)
        Py_FatalError(msgFailedToInitializeType("Shiboken.BaseWrapperType metatype").c_str());

    type = SbkObject_TypeF();
    if (type == nullptr || PyType_Ready(type) < 0)
        Py_FatalError(msgFailedToInitializeType("Shiboken.BaseWrapper type").c_str());

    VoidPtr::init();

    shibokenAlreadInitialised = true;
}

// PYSIDE-1415: Publish Shiboken objects.
// PYSIDE-1735: Initialize the whole Shiboken startup.
void initShibokenSupport(PyObject *module)
{
    auto *type = SbkObject_TypeF();
    auto *obType = reinterpret_cast<PyObject *>(type);
    Py_INCREF(obType);
    PepModule_AddType(module, type);

    // PYSIDE-1735: When the initialization was moved into Shiboken import, this
    //              Py_INCREF became necessary. No idea why.
    Py_INCREF(module);
    init_shibokensupport_module();

    if (InitSignatureStrings(type, SbkObject_SignatureStrings) < 0)
        Py_FatalError("libshiboken: Error in initShibokenSupport");
}

// setErrorAboutWrongArguments now gets overload info from the signature module.
// Info can be nullptr and contains extra info.
void setErrorAboutWrongArguments(PyObject *args, const char *funcName, PyObject *info,
                                 const char *className)
{
    if (className != nullptr) {
        std::string text = std::string(className);
        text += '.';
        text += funcName;
        SetError_Argument(args, text.c_str(), info);
        return;
    }
    SetError_Argument(args, funcName, info);
}

PyObject *returnWrongArguments(PyObject *args, const char *memberName, PyObject *info,
                               const Module::TypeInitStruct &initStruct)
{
    setErrorAboutWrongArguments(args, memberName, info, initStruct.fullName);
    return {};
}

PyObject *returnWrongArguments(PyObject *args, const char *memberName,
                               const Module::TypeInitStruct &initStruct)
{
    setErrorAboutWrongArguments(args, memberName, nullptr, initStruct.fullName);
    return {};
}

PyObject *returnWrongArguments(PyObject *args, const char *globalFuncName, PyObject *info)
{
    setErrorAboutWrongArguments(args, globalFuncName, info);
    return {};
}

PyObject *returnWrongArguments(PyObject *args, const char *globalFuncName)
{
    setErrorAboutWrongArguments(args, globalFuncName, nullptr);
    return {};
}

int returnWrongArguments_Zero(PyObject *args, const char *memberName, PyObject *info,
                              const Module::TypeInitStruct &initStruct)
{
    setErrorAboutWrongArguments(args, memberName, info, initStruct.fullName);
    return 0;
}

int returnWrongArguments_Zero(PyObject *args, const char *globalFuncName, PyObject *info)
{
    setErrorAboutWrongArguments(args, globalFuncName, info);
    return 0;
}

int returnWrongArguments_MinusOne(PyObject *args, const char *memberName, PyObject *info,
                                  const Module::TypeInitStruct &initStruct)
{
    setErrorAboutWrongArguments(args, memberName, info, initStruct.fullName);
    return -1;
}

int returnWrongArguments_MinusOne(PyObject *args, const char *memberName,
                                  const Module::TypeInitStruct &initStruct)
{
    setErrorAboutWrongArguments(args, memberName, nullptr, initStruct.fullName);
    return -1;
}

int returnWrongArguments_MinusOne(PyObject *args, const char *globalFuncName, PyObject *info)
{
    setErrorAboutWrongArguments(args, globalFuncName, info);
    return -1;
}

PyObject *returnFromRichCompare(PyObject *result)
{
    if (result && !PyErr_Occurred())
        return result;
    // Keep the exception of a failed argument conversion instead of guessing
    // that no operator matched. Under Py_GIL_DISABLED only: replacing it is
    // what a build with a GIL has always done here.
    // See "A failed conversion stops the entry" in the free-threading notes.
#ifdef Py_GIL_DISABLED
    if (!Shiboken::Errors::conversionFailed())
#endif
        Shiboken::Errors::setOperatorNotImplemented();
    return {};
}

PyObject *checkInvalidArgumentCount(Py_ssize_t numArgs, Py_ssize_t minArgs, Py_ssize_t maxArgs)
{
    PyObject *result = nullptr;
    // for seterror_argument(), signature/errorhandler.py
    if (numArgs > maxArgs) {
        static PyObject *const tooMany = Shiboken::String::createStaticString(">");
        result = tooMany;
        Py_INCREF(result);
    } else if (numArgs < minArgs) {
        static PyObject *const tooFew = Shiboken::String::createStaticString("<");
        static PyObject *const noArgs = Shiboken::String::createStaticString("0");
        result = numArgs > 0 ? tooFew : noArgs;
        Py_INCREF(result);
    }
    return result;
}

std::vector<SbkObject *> splitPyObject(PyObject *pyObj)
{
    std::vector<SbkObject *> result;
    if (PySequence_Check(pyObj)) {
        AutoDecRef lst(PySequence_Fast(pyObj, "Invalid keep reference object."));
        if (!lst.isNull()) {
            for (Py_ssize_t i = 0, i_max = PySequence_Size(lst.object()); i < i_max; ++i) {
                Shiboken::AutoDecRef item(PySequence_GetItem(lst.object(), i));
                if (Object::checkType(item))
                    result.push_back(reinterpret_cast<SbkObject *>(item.object()));
            }
        }
    } else {
        result.push_back(reinterpret_cast<SbkObject *>(pyObj));
    }
    return result;
}

template <class Iterator>
inline void decRefPyObjectList(Iterator i1, Iterator i2)
{
    for (; i1 != i2; ++i1)
        Py_DECREF(i1->second);
}

namespace ObjectType
{

bool checkType(PyTypeObject *type)
{
    SBK_ASSERT_LOCK_NOT_HELD(State);
    return PyType_IsSubtype(type, SbkObject_TypeF()) != 0;
}

bool isUserType(PyTypeObject *type)
{
    return checkType(type) && PepType_SOTP(type)->is_user_type;
}

bool canCallConstructor(PyTypeObject *myType, PyTypeObject *ctorType)
{
    auto findBasePred = [ctorType](PyTypeObject *type) { return type == ctorType; };
    if (!walkThroughBases(myType, findBasePred)) {
        PyErr_Format(PyExc_TypeError,
                     "libshiboken: %s isn't a direct base class of %s", ctorType->tp_name, myType->tp_name);
        return false;
    }
    return true;
}

bool hasCast(PyTypeObject *type)
{
    return PepType_SOTP(type)->mi_specialcast != nullptr;
}

void *cast(PyTypeObject *sourceType, SbkObject *obj, PyTypeObject *pyTargetType)
{
    auto *sotp = PepType_SOTP(sourceType);
    return sotp->mi_specialcast(Object::cppPointer(obj, pyTargetType), pyTargetType);
}

void setCastFunction(PyTypeObject *type, SpecialCastFunction func)
{
    auto *sotp = PepType_SOTP(type);
    sotp->mi_specialcast = func;
}

void setOriginalName(PyTypeObject *type, const char *name)
{
    auto *sotp = PepType_SOTP(type);
    if (sotp->original_name)
        free(sotp->original_name);
    sotp->original_name = strdup(name);
}

const char *getOriginalName(PyTypeObject *type)
{
    return PepType_SOTP(type)->original_name;
}

void setTypeDiscoveryFunctionV2(PyTypeObject *type, TypeDiscoveryFuncV2 func)
{
    PepType_SOTP(type)->type_discovery = func;
}

void copyMultipleInheritance(PyTypeObject *type, PyTypeObject *other)
{
    auto *sotp_type = PepType_SOTP(type);
    auto *sotp_other = PepType_SOTP(other);
    sotp_type->mi_init = sotp_other->mi_init;
    sotp_type->mi_specialcast = sotp_other->mi_specialcast;
    // mi_offsets is not copied: mi_init() computes it at the point of use.
}

void setMultipleInheritanceFunction(PyTypeObject *type, MultipleInheritanceInitFunction function)
{
    PepType_SOTP(type)->mi_init = function;
}

MultipleInheritanceInitFunction getMultipleInheritanceFunction(PyTypeObject *type)
{
    return PepType_SOTP(type)->mi_init;
}

void setDestructorFunction(PyTypeObject *type, ObjectDestructor func)
{
    PepType_SOTP(type)->cpp_dtor = func;
}

PyTypeObject *
introduceWrapperType(PyObject *enclosingObject,
                     const char *typeName,
                     const char *originalName,
                     PyType_Spec *typeSpec,
                     ObjectDestructor cppObjDtor,
                     PyObject *bases,
                     unsigned wrapperFlags)
{
    assert(PySequence_Size(bases) > 0);
    typeSpec->slots[0].pfunc = PySequence_GetItem(bases, 0);

    auto *type = SbkType_FromSpecBasesMeta(typeSpec, bases, SbkObjectType_TypeF());
    if (type == nullptr) {
        // Reporting the failure beats crashing in PepType_SOTP() below: a
        // failure here means the type spec or one of its bases is unusable,
        // and the traceback names the type instead of a null dereference.
        PyErr_Format(PyExc_SystemError, "libshiboken: Cannot create type '%s'", typeName);
        return nullptr;
    }

    auto *sotp = PepType_SOTP(type);
    if (wrapperFlags & DeleteInMainThread)
        sotp->delete_in_main_thread = 1;
    sotp->type_behaviour = (wrapperFlags & Value) != 0
                           ? BEHAVIOUR_VALUETYPE : BEHAVIOUR_OBJECTTYPE;

    setOriginalName(type, originalName);
    setDestructorFunction(type, cppObjDtor);
    auto *ob_type = reinterpret_cast<PyObject *>(type);

    if (wrapperFlags & InternalWrapper) {
        // Type wraps another wrapper class and isn't part of any module.  This is used to extend
        // Qt types with additional functionality, but from within PySide itself.  In order for
        // the re-wrapped class to call the autogenerated __init__ method, is_user_type must be set
        // to 1.  Otherwise the Shiboken::ObjectType::canCallConstructor test will fail.
        // This is currently only used by QtRemoteObjects to create types dynamically.
        sotp->is_user_type = 1;
        return type;
    }

    if (wrapperFlags & InnerClass) {
        // PYSIDE-2230: Instead of tp_dict, use the enclosing type.
        //              This stays interface compatible.
        if (PyType_Check(enclosingObject)) {
            AutoDecRef tpDict(PepType_GetDict(reinterpret_cast<PyTypeObject *>(enclosingObject)));
            return PyDict_SetItemString(tpDict, typeName, ob_type) == 0 ? type : nullptr;
        }
        if (PyDict_Check(enclosingObject))
            return PyDict_SetItemString(enclosingObject, typeName, ob_type) == 0 ? type : nullptr;
    }

    // PyModule_AddObject steals type's reference.
    Py_INCREF(ob_type);
    if (PepModule_AddType(enclosingObject, type) != 0) {
        std::cerr << "Warning: " << __FUNCTION__ << " returns nullptr for "
            << typeName << '/' << originalName << " due to PyModule_AddObject(enclosingObject="
            << enclosingObject << ", ob_type=" << ob_type << ") failing\n";
        return nullptr;
    }
    return type;
}

void setSubTypeInitHook(PyTypeObject *type, SubTypeInitHook func)
{
    assert(SbkObjectType_Check(type));
    PepType_SOTP(type)->subtype_init = func;
}

void *getTypeUserData(PyTypeObject *type)
{
    assert(SbkObjectType_Check(type));
    return PepType_SOTP(type)->user_data;
}

void setTypeUserData(PyTypeObject *type, void *userData, DeleteUserDataFunc d_func)
{
    assert(SbkObjectType_Check(type));
    auto *sotp = PepType_SOTP(type);
    sotp->user_data = userData;
    sotp->d_func = d_func;
}

// Try to find the exact type of cptr.
PyTypeObject *typeForTypeName(const char *typeName)
{
    PyTypeObject *result{};
    if (typeName) {
        if (PyTypeObject *pyType = Shiboken::Conversions::getPythonTypeObject(typeName))
            result = pyType;
    }
    return result;
}

bool hasSpecialCastFunction(PyTypeObject *sbkType)
{
    const auto *d = PepType_SOTP(sbkType);
    return d != nullptr && d->mi_specialcast != nullptr;
}

// Find whether base is a direct single line base class of type
// (no multiple inheritance), that is, a C++ pointer cast can safely be done.
static bool isDirectAncestor(PyTypeObject *type, PyTypeObject *base)
{
    if (type == base)
        return true;
    if (PyTuple_Size(type->tp_bases) == 0)
        return false;
    auto *sbkObjectType = SbkObject_TypeF();
    auto *firstBase = reinterpret_cast<PyTypeObject *>(PyTuple_GetItem(type->tp_bases, 0));
    return firstBase != sbkObjectType
           && PyType_IsSubtype(type, sbkObjectType) != 0
           && isDirectAncestor(firstBase, base);
}

bool canDowncastTo(PyTypeObject *baseType, PyTypeObject *targetType)
{
    return isDirectAncestor(targetType, baseType);
}

} // namespace ObjectType


namespace Object
{

#ifndef Py_GIL_DISABLED
static void recursive_invalidate(SbkObject *self, std::set<SbkObject *> &seen);
#endif

bool checkType(PyObject *pyObj)
{
    return ObjectType::checkType(Py_TYPE(pyObj));
}

bool isUserType(PyObject *pyObj)
{
    return ObjectType::isUserType(Py_TYPE(pyObj));
}

Py_hash_t hash(PyObject *pyObj)
{
    assert(Shiboken::Object::checkType(pyObj));
    return reinterpret_cast<Py_hash_t>(pyObj);
}

static void setSequenceOwnership(PyObject *pyObj, bool owner)
{
    if (!pyObj)
        return;

    const Py_ssize_t length = PyList_Check(pyObj) != 0 || PyTuple_Check(pyObj)  != 0
                                  ? PySequence_Size(pyObj) : -1;
    if (length >= 0) {
        if (length > 0) {
            const auto objs = splitPyObject(pyObj);
            if (owner) {
                for (SbkObject *o : objs)
                    getOwnership(o);
            } else {
                for (SbkObject *o : objs)
                    releaseOwnership(o);
            }
        }
    } else if (Object::checkType(pyObj)) {
        if (owner)
            getOwnership(reinterpret_cast<SbkObject *>(pyObj));
        else
            releaseOwnership(reinterpret_cast<SbkObject *>(pyObj));
    }
}

// One of the writers of validCppObject that takes no state lock, like
// setCppPointer(): the callers are generated constructors, and there no other
// thread can reach the object yet. The flag is a RelaxedFlag, so the write
// itself is defined; what would need the lock is a decision made from it,
// and none is made here.
void setValidCpp(SbkObject *pyObj, bool value)
{
    pyObj->d->validCppObject = value;
}

void setHasCppWrapper(SbkObject *pyObj, bool value)
{
    pyObj->d->containsCppWrapper = value;
}

bool hasCppWrapper(SbkObject *pyObj)
{
    return pyObj->d->containsCppWrapper;
}

bool wasCreatedByPython(SbkObject *pyObj)
{
    return pyObj->d->cppObjectCreated;
}

#ifndef Py_GIL_DISABLED  // free-threaded twin: see the state-lock chapter below
void callCppDestructors(SbkObject *pyObj)
{
    auto *priv = pyObj->d;
    // Idempotent under the guard: a concurrent Shiboken.delete() of the same
    // object may already have claimed the C++ pointer and cleared cptr.
    if (priv->cptr == nullptr || !priv->validCppObject)
        return;
    if (priv->isQAppSingleton && DestroyQApplication) {
        // PYSIDE-1470: Allow to destroy the application from Shiboken.
        DestroyQApplication();
        return;
    }
    auto *sotp = PepType_SOTP(Shiboken::pyType(pyObj));

    // All bookkeeping first, while the guard cannot have been suspended; the
    // C++ destructors run last, on a snapshot of the pointers. Running the
    // destructor first is unsafe: ThreadStateSaver detaches the thread, which
    // suspends the critical section, and a concurrent delete of the same
    // object then passes the check above and destroys the C++ object a second
    // time. Same order as the dealloc path in SbkDeallocWrapperCommon().
    DestructorEntries entries;
    void *cptr0 = nullptr;
    if (sotp->is_multicpp)
        entries = getDestructorEntries(pyObj);
    else
        cptr0 = priv->cptr[0];

    if (priv->containsCppWrapper)
        BindingManager::instance().releaseWrapper(pyObj);

    /* invalidate needs to be called before deleting pointer array because
       it needs to delete entries for them from the BindingManager hash table;
       also release wrapper explicitly if object contains C++ wrapper because
       invalidate doesn't */
    invalidate(pyObj);

    delete[] priv->cptr;
    priv->cptr = nullptr;
    priv->validCppObject = false;

    if (sotp->is_multicpp) {
        callDestructor(entries);
    } else {
        Shiboken::ThreadStateSaver threadSaver;
        threadSaver.save();
        sotp->cpp_dtor(cptr0);
    }
}
#endif // !Py_GIL_DISABLED

bool hasOwnership(SbkObject *pyObj)
{
    return pyObj->d->hasOwnership;
}

#ifndef Py_GIL_DISABLED  // free-threaded twin: see the state-lock chapter below
void getOwnership(SbkObject *sbkObj)
{
    // skip if already have the ownership
    if (sbkObj->d->hasOwnership)
        return;

    // skip if this object has parent
    if (sbkObj->d->parentInfo && sbkObj->d->parentInfo->parent)
        return;

    // Get back the ownership
    sbkObj->d->hasOwnership = true;

    if (sbkObj->d->containsCppWrapper)
        Py_DECREF(reinterpret_cast<PyObject *>(sbkObj)); // Remove extra ref
    else
        makeValid(sbkObj); // Make the object valid again
}
#endif // !Py_GIL_DISABLED

void getOwnership(PyObject *pyObj)
{
    if (pyObj)
        setSequenceOwnership(pyObj, true);
}

#ifndef Py_GIL_DISABLED  // free-threaded twin: see the state-lock chapter below
void releaseOwnership(SbkObject *sbkObj)
{
    // skip if the ownership have already moved to c++
    auto *ob  = reinterpret_cast<PyObject *>(sbkObj);
    auto *selfType = Py_TYPE(ob);
    if (!sbkObj->d->hasOwnership || Shiboken::Conversions::pythonTypeIsValueType(PepType_SOTP(selfType)->converter))
        return;

    // remove object ownership
    sbkObj->d->hasOwnership = false;

    // If We have control over object life
    if (sbkObj->d->containsCppWrapper)
        Py_INCREF(ob); // keep the python object alive until the wrapper destructor call
    else
        invalidate(sbkObj); // If I do not know when this object will die We need to invalidate this to avoid use after
}
#endif // !Py_GIL_DISABLED

void releaseOwnership(PyObject *pyObj)
{
    setSequenceOwnership(pyObj, false);
}

#ifndef Py_GIL_DISABLED  // free-threaded twin: see the state-lock chapter below
/* Needed forward declarations */
static void recursive_invalidate(PyObject *pyobj, std::set<SbkObject *> &seen);

void invalidate(PyObject *pyobj)
{
    std::set<SbkObject *> seen;
    recursive_invalidate(pyobj, seen);
}

void invalidate(SbkObject *self)
{
    std::set<SbkObject *> seen;
    recursive_invalidate(self, seen);
}

static void recursive_invalidate(PyObject *pyobj, std::set<SbkObject *> &seen)
{
    const auto objs = splitPyObject(pyobj);
    for (SbkObject *o : objs)
        recursive_invalidate(o, seen);
}

// The object and its children, and deliberately not what it refers to. The
// tag that fills referredObjects exists for the case where a parent link
// would be wrong: "our hypothetical view cannot become a parent of the model,
// since the said model could be used by other views as well"
// (typesystem_arguments.rst). A referred object outlives the holder's C++
// instance, so marking it invalid claims an address the binding never had -
// the shared &QObject::staticMetaObject is referred to by every QObject that
// ever asked for its metaObject().
static void recursive_invalidate(SbkObject *self, std::set<SbkObject *> &seen)
{
    // Skip if this object not is a valid object or if it's already been seen
    if (!self || reinterpret_cast<PyObject *>(self) == Py_None || seen.find(self) != seen.end())
        return;
    seen.insert(self);

    if (!self->d->containsCppWrapper) {
        self->d->validCppObject = false; // Mark object as invalid only if this is not a wrapper class
        BindingManager::instance().releaseWrapper(self);
    }

    // If it is a parent invalidate all children.
    if (self->d->parentInfo) {
        // Create a copy because this list can be changed during the process
        ChildrenList copy = self->d->parentInfo->children;

        for (SbkObject *child : copy) {
            // invalidate the child
            recursive_invalidate(child, seen);

            // if the parent not is a wrapper class, then remove children from him, because We do not know when this object will be destroyed
            if (!self->d->validCppObject)
                removeParent(child, true, true);
        }
    }
}

void makeValid(SbkObject *self)
{
    // Skip if this object not is a valid object
    if (!self || reinterpret_cast<PyObject *>(self) == Py_None || self->d->validCppObject)
        return;

    // Mark object as invalid only if this is not a wrapper class
    self->d->validCppObject = true;

    // If it is a parent make  all children valid
    if (self->d->parentInfo) {
        for (SbkObject *child : self->d->parentInfo->children)
            makeValid(child);
    }

    // If has ref to other objects make all valid again
    if (self->d->referredObjects) {
        const RefCountMap &refCountMap = *(self->d->referredObjects);
        for (const auto &p : refCountMap) {
            if (Shiboken::Object::checkType(p.second))
                makeValid(reinterpret_cast<SbkObject *>(p.second));
        }
    }
}
#endif // !Py_GIL_DISABLED

void *cppPointer(SbkObject *pyObj, PyTypeObject *desiredType)
{
    PyTypeObject *pyType = Shiboken::pyType(pyObj);
    auto *sotp = PepType_SOTP(pyType);
    int idx = 0;
    if (sotp->is_multicpp)
        idx = getTypeIndexOnHierarchy(pyType, desiredType);
    // One load, not two: Object::destroy() nulls cptr from another thread,
    // and a second read could find null where the test saw a pointer. With a
    // GIL the two reads cannot be interleaved, so this is free threading only
    // in effect.
    auto *cptr = pyObj->d->cptr;
    if (cptr != nullptr)
        return cptr[idx];
    return nullptr;
}

std::vector<void *> cppPointers(SbkObject *pyObj)
{
    int n = getNumberOfCppBaseClasses(Shiboken::pyType(pyObj));
    std::vector<void *> ptrs(n);
    for (int i = 0; i < n; ++i)
        ptrs[i] = pyObj->d->cptr[i];
    return ptrs;
}


// The one writer of cptr that takes no state lock. On the call that matters -
// the first, successful tp_init - it runs between the allocation and
// registerWrapper(), where the wrapper is in no map and has reached no other
// thread. A second tp_init on a published wrapper reads cptr unlocked, and is
// refused by the alreadyInitialized check below; that call is already broken
// on a build with a GIL, where the read follows a Shiboken.delete().
bool setCppPointer(SbkObject *sbkObj, PyTypeObject *desiredType, void *cptr)
{
    PyTypeObject *type = Shiboken::pyType(sbkObj);
    int idx = 0;
    if (PepType_SOTP(type)->is_multicpp)
        idx = getTypeIndexOnHierarchy(type, desiredType);

    // The slot is claimed in one transaction. Read and write used to be two
    // steps, and a Python subclass can hand self to another thread before it
    // calls the base __init__: both threads then saw an empty slot, both
    // constructed a C++ object, and both reported success. One of the two
    // objects was left with nobody to delete it.
    bool alreadyInitialized = true;
    bool detached = false;
#ifdef Py_GIL_DISABLED
    if (Shiboken::FreeThreading::optionEnabled(Shiboken::FreeThreading::ConstructorCommit)) {
        // Before the transaction, which is where a second thread has to be
        // able to get in: the point of the test is that it changes nothing.
        SBK_FAILPOINT("ctor-before-publish");
        StateLockGuard guard;
        // The array can already be detached: another thread called
        // Shiboken.delete() on self before the base __init__ ran. Reported
        // after the transaction, like the refusal below.
        detached = sbkObj->d->cptr == nullptr;
        alreadyInitialized = detached || sbkObj->d->cptr[idx] != nullptr;
        if (!alreadyInitialized) {
            sbkObj->d->cptr[idx] = cptr;
            sbkObj->d->cppObjectCreated = true;
        }
    } else
#endif
    {
        // The A/B side: the two steps as they were, with the same point
        // between them - where a second thread turns one winner into two.
        alreadyInitialized = sbkObj->d->cptr[idx] != nullptr;
        SBK_FAILPOINT("ctor-before-publish");
        if (!alreadyInitialized)
            sbkObj->d->cptr[idx] = cptr;
        sbkObj->d->cppObjectCreated = true;
    }

    // Raising is a Python call-out and happens after the transaction.
    if (detached) {
        PyErr_Format(PyExc_RuntimeError,
                     "libshiboken: The %s object in class %s was destroyed while it "
                     "was being initialized",
                     desiredType->tp_name, type->tp_name);
    } else if (alreadyInitialized) {
        PyErr_Format(PyExc_RuntimeError,
                     "libshiboken: You can't initialize an %s object in class %s twice!",
                     desiredType->tp_name, type->tp_name);
    }
    return !alreadyInitialized;
}

ConstructionGuard::ConstructionGuard([[maybe_unused]] SbkObject *sbkObj,
                                     [[maybe_unused]] PyTypeObject *desiredType)
{
#ifdef Py_GIL_DISABLED
    m_obj = sbkObj;
    if (!Shiboken::FreeThreading::optionEnabled(Shiboken::FreeThreading::ConstructorClaim)) {
        // The A/B side: nothing is reserved, and the race the reservation
        // closes is back - both threads build, one of the two objects is
        // left with nobody to delete it.
        m_claimed = true;
        return;
    }

    PyTypeObject *type = Shiboken::pyType(sbkObj);
    int idx = 0;
    if (PepType_SOTP(type)->is_multicpp)
        idx = getTypeIndexOnHierarchy(type, desiredType);
    // One bit per C++ base. No binding we generate comes near this many, and
    // a type that did would go unreserved rather than shift out of range.
    if (idx >= int(sizeof(unsigned int) * 8)) {
        m_claimed = true;
        return;
    }

    const unsigned int bit = 1u << unsigned(idx);
    bool detached = false;
    bool constructing = false;
    bool initialized = false;
    {
        StateLockGuard guard;
        auto *priv = sbkObj->d;
        // Shiboken.delete() from another thread may have detached the array
        // before this __init__ got here. Reported after the transaction, as
        // the refusals below are.
        detached = priv->cptr == nullptr;
        if (!detached) {
            initialized = priv->cptr[idx] != nullptr;
            constructing = (priv->constructingSlots & bit) != 0;
            if (!initialized && !constructing) {
                priv->constructingSlots |= bit;
                m_index = idx;
                m_claimed = true;
            }
        }
    }

    // Raising is a Python call-out and happens after the transaction.
    if (detached) {
        PyErr_Format(PyExc_RuntimeError,
                     "libshiboken: The %s object in class %s was destroyed while it "
                     "was being initialized",
                     desiredType->tp_name, type->tp_name);
    } else if (constructing) {
        PyErr_Format(PyExc_RuntimeError,
                     "libshiboken: The %s object in class %s is already being "
                     "initialized by another thread",
                     desiredType->tp_name, type->tp_name);
    } else if (initialized) {
        PyErr_Format(PyExc_RuntimeError,
                     "libshiboken: You can't initialize an %s object in class %s twice!",
                     desiredType->tp_name, type->tp_name);
    }
#else
    // With a GIL there is no second thread in here, and commitConstruction()
    // catches a second __init__ on its own.
    m_claimed = true;
#endif // Py_GIL_DISABLED
}

ConstructionGuard::~ConstructionGuard()
{
#ifdef Py_GIL_DISABLED
    if (m_index < 0)
        return;
    // Unconditional: the slot is given back whether this call published or
    // bailed out, and the object being published has its pointer by now, so
    // the next caller is refused by that instead.
    StateLockGuard guard;
    m_obj->d->constructingSlots &= ~(1u << unsigned(m_index));
#endif
}

bool commitConstruction(SbkObject *sbkObj, PyTypeObject *desiredType, void *cptr,
                        bool hasCppWrapper)
{
    // The map first, the flags after: the state lock is the leaf, so nothing
    // may be taken while it is held. Both are short, and between them the
    // object is registered but not yet marked valid - a lookup finds it and
    // a call on it refuses, which is the safe half of the window and the one
    // the "__init__ not called" error already covers.
    if (!setCppPointer(sbkObj, desiredType, cptr))
        return false;
    BindingManager::instance().registerWrapper(sbkObj, cptr);
    setValidCpp(sbkObj, true);
    if (hasCppWrapper)
        setHasCppWrapper(sbkObj, true);
    return true;
}

bool isValid(PyObject *pyObj)
{
    if (pyObj == nullptr || pyObj == Py_None || PyType_Check(pyObj) != 0)
        return true;

    PyTypeObject *type = Py_TYPE(pyObj);
    if (Py_TYPE(reinterpret_cast<PyObject *>(type)) != SbkObjectType_TypeF())
        return true;

#ifdef Py_GIL_DISABLED
    auto *self = reinterpret_cast<SbkObject *>(pyObj);
    auto *priv = self->d;
#else
    auto *priv = reinterpret_cast<SbkObject *>(pyObj)->d;
#endif

    if (!priv->cppObjectCreated && isUserType(pyObj)) {
        PyErr_Format(PyExc_RuntimeError,
                     "libshiboken: '__init__' method of object's base class (%s) not called.",
                     Py_TYPE(pyObj)->tp_name);
        return false;
    }

    if (!priv->validCppObject) {
        PyErr_Format(PyExc_RuntimeError,
                     "libshiboken: Internal C++ object (%s) already deleted.",
                     Py_TYPE(pyObj)->tp_name);
        return false;
    }

#ifdef Py_GIL_DISABLED
    // An object whose destruction is only waiting for a lease to end is gone
    // as far as callers are concerned: acquireCallLeaseLocked() refuses it,
    // so every method call on it raises. Answering "valid" here would let
    // Shiboken.isValid() disagree with what the next call does. A wrapper
    // subclass keeps validCppObject set through that, which is why the flag
    // above does not catch it.
    if (isClaimed(self)) {
        PyErr_Format(PyExc_RuntimeError,
                     "libshiboken: Internal C++ object (%s) already deleted.",
                     Py_TYPE(pyObj)->tp_name);
        return false;
    }
#endif // Py_GIL_DISABLED

    return true;
}

bool isValid(SbkObject *pyObj, bool throwPyError)
{
    if (!pyObj)
        return false;

    SbkObjectPrivate *priv = pyObj->d;
    auto *ob = reinterpret_cast<PyObject *>(pyObj);
    if (!priv->cppObjectCreated && isUserType(ob)) {
        if (throwPyError)
            PyErr_Format(PyExc_RuntimeError,
                         "libshiboken: Base constructor of the object (%s) not called.",
                         Py_TYPE(ob)->tp_name);
        return false;
    }

    if (!priv->validCppObject) {
        if (throwPyError)
            PyErr_Format(PyExc_RuntimeError,
                         "libshiboken: Internal C++ object (%s) already deleted.",
                         (Py_TYPE(ob))->tp_name);
        return false;
    }

#ifdef Py_GIL_DISABLED
    // See the overload above: a claimed object refuses every lease, so it is
    // deleted for every purpose a caller has.
    if (isClaimed(pyObj)) {
        if (throwPyError)
            PyErr_Format(PyExc_RuntimeError,
                         "libshiboken: Internal C++ object (%s) already deleted.",
                         (Py_TYPE(ob))->tp_name);
        return false;
    }
#endif

    return true;
}

bool isValid(PyObject *pyObj, bool throwPyError)
{
    if (!pyObj || pyObj == Py_None ||
        !PyType_IsSubtype(Py_TYPE(pyObj), SbkObject_TypeF())) {
        return true;
    }
    return isValid(reinterpret_cast<SbkObject *>(pyObj), throwPyError);
}

#ifndef Py_GIL_DISABLED
// Not compiled under free threading: it walks the parent/child graph and
// reads cptr without the state lock, and hands back a borrowed wrapper. It
// has no caller left; should one appear, it needs a transaction and an
// AcquiredWrapper, not this.
SbkObject *findColocatedChild(SbkObject *wrapper,
                              const PyTypeObject *instanceType)
{
    // Degenerate case, wrapper is the correct wrapper.
    if (reinterpret_cast<const void *>(Shiboken::pyType(wrapper)) == reinterpret_cast<const void *>(instanceType))
        return wrapper;

    if (!(wrapper->d && wrapper->d->cptr))
        return nullptr;

    ParentInfo *pInfo = wrapper->d->parentInfo;
    if (!pInfo)
        return nullptr;

    ChildrenList &children = pInfo->children;

    for (SbkObject *child : children) {
        if (!(child->d && child->d->cptr))
            continue;
        if (child->d->cptr[0] == wrapper->d->cptr[0]) {
            auto *childType = Shiboken::pyType(child);
            return reinterpret_cast<const void *>(childType) == reinterpret_cast<const void *>(instanceType)
                ? child : findColocatedChild(child, instanceType);
        }
    }
    return nullptr;
}
#endif // !Py_GIL_DISABLED

// Legacy, for compatibility only.
PyObject *newObject(PyTypeObject *instanceType,
                    void *cptr,
                    bool hasOwnership,
                    bool isExactType,
                    const char *typeName)
{
    return isExactType
        ? newObjectForType(instanceType, cptr, hasOwnership)
        : newObjectWithHeuristics(instanceType, cptr, hasOwnership, typeName);
}

static PyObject *newObjectWithHeuristicsHelper(PyTypeObject *instanceType,
                                               const char *cppTypeIdName,
                                               void *cptr,
                                               bool hasOwnership)
{
    // Try to find the exact type of cptr via the name obtained from "typeId(ptr).name()"
    // as registered with the shiboken converters.
    PyTypeObject *exactType = ObjectType::typeForTypeName(cppTypeIdName);

    // Nothing found or same name returned (in case of a hierarchy with non-virtual destructors
    // like QStyleOption). Try type discovery in these cases.
    if (exactType == nullptr || exactType == instanceType) {
        if (auto resolved = BindingManager::instance().findDerivedType(cptr, instanceType);
            resolved.first != nullptr) {
            return newObjectForType(resolved.first, resolved.second, hasOwnership);
        }
    } else {
        // Direct, single line inheritance: Use exactType
        if (Shiboken::ObjectType::canDowncastTo(instanceType, exactType))
            return newObjectForType(exactType, cptr, hasOwnership);
        // Multiple inheritance: Try to run type discovery on the type found to cast cptr
        if (auto *derivedCptr = BindingManager::runTypeDiscovery(cptr, exactType, instanceType))
            return newObjectForType(exactType, derivedCptr, hasOwnership);
    }

    // Fall back to base type
    return newObjectForType(instanceType, cptr, hasOwnership);
}

PyObject *newObjectForPointer(PyTypeObject *instanceType,
                              void *cptr,
                              bool hasOwnership,
                              const char *typeName)
{
    return newObjectWithHeuristicsHelper(instanceType, typeName, cptr, hasOwnership);
}


PyObject *newObjectWithHeuristics(PyTypeObject *instanceType,
                                  void *cptr,
                                  bool hasOwnership,
                                  const char *typeName)
{
    return newObjectWithHeuristicsHelper(instanceType, typeName,
                                         cptr, hasOwnership);
}

PyObject *newObjectForType(PyTypeObject *instanceType, void *cptr, bool hasOwnership)
{
    auto &bindingManager = BindingManager::instance();
#ifdef Py_GIL_DISABLED
    if (auto existing = bindingManager.acquireWrapper(cptr, instanceType))
        return reinterpret_cast<PyObject *>(existing.release());

    auto *self = reinterpret_cast<SbkObject *>(SbkObject_tp_new(instanceType, nullptr, nullptr));
    self->d->cptr[0] = cptr;
    self->d->hasOwnership = hasOwnership;
    self->d->validCppObject = true;

    // Creating the wrapper runs Python, so it cannot happen under the map
    // lock; another thread may have registered one for the same pointer
    // meanwhile. Registering asks and inserts in one hold, and hands back the
    // winner if it is not ours.
    if (auto reg = bindingManager.registerWrapperUnlessPresent(self, cptr, instanceType)) {
        // Detach ours before dropping it or handing it out: it never reached
        // the map, and with the pointer cleared its deallocation leaves the
        // C++ object alone. Ownership goes with the wrapper that won. If it
        // has none and we were given some, the C++ object outlives both - a
        // leak, where keeping ownership here would be the second delete.
        self->d->cptr[0] = nullptr;
        self->d->hasOwnership = false;
        self->d->validCppObject = false;
        if (reg.winner) {
            Py_DECREF(reinterpret_cast<PyObject *>(self));
            return reinterpret_cast<PyObject *>(reg.winner.release());
        }
        // Otherwise a tombstone: the identity is being destroyed. The caller
        // gets a wrapper it can hold, but not one that claims the C++ object
        // is there - every use of it raises instead of reading freed memory.
        // That is the policy for a conversion that meets a dying identity;
        // the QObject destroyed() argument is the case it is written for.
    }
    return reinterpret_cast<PyObject *>(self);
#else // Py_GIL_DISABLED
    SbkObject *self = bindingManager.retrieveWrapper(cptr, instanceType);
    if (self != nullptr) {
        Py_IncRef(reinterpret_cast<PyObject *>(self));
    } else {
        self = reinterpret_cast<SbkObject *>(SbkObject_tp_new(instanceType, nullptr, nullptr));
        self->d->cptr[0] = cptr;
        self->d->hasOwnership = hasOwnership;
        self->d->validCppObject = true;
        bindingManager.registerWrapper(self, cptr);
    }
    return reinterpret_cast<PyObject *>(self);
#endif // Py_GIL_DISABLED
}

#ifndef Py_GIL_DISABLED  // free-threaded twin: see the state-lock chapter below
void destroy(SbkObject *self, void *cppData)
{
    // Skip if this is called with NULL pointer this can happen in derived classes
    if (!self)
        return;

    // This can be called in c++ side
    Shiboken::GilState gil;

    // Remove all references attached to this object
    clearReferences(self);

    // Remove the object from parent control

    // Verify if this object has parent
    bool hasParent = (self->d->parentInfo && self->d->parentInfo->parent);

    if (self->d->parentInfo) {
        // Check for children information and make all invalid if they exists
        _destroyParentInfo(self, true);
        // If this object has parent then the pyobject can be invalid now, because we remove the last ref after remove from parent
    }

    //if !hasParent this object could still alive
    if (!hasParent && self->d->containsCppWrapper && !self->d->hasOwnership) {
        // Remove extra ref used by c++ object this will case the pyobject destruction
        // This can cause the object death
        Py_DECREF(reinterpret_cast<PyObject *>(self));
    }

    //Python Object is not destroyed yet
    if (cppData && Shiboken::BindingManager::instance().hasWrapper(cppData)) {
        // Remove from BindingManager
        Shiboken::BindingManager::instance().releaseWrapper(self);
        self->d->hasOwnership = false;

        // the cpp object instance was deleted
        delete[] self->d->cptr;
        self->d->cptr = nullptr;
    }

    // After this point the object can be death do not use the self pointer bellow
}
#endif // !Py_GIL_DISABLED

#ifndef Py_GIL_DISABLED  // free-threaded twin: see the state-lock chapter below
void removeParent(SbkObject *child, bool giveOwnershipBack, bool keepReference)
{
    ParentInfo *pInfo = child->d->parentInfo;
    if (!pInfo || !pInfo->parent) {
        if (pInfo && pInfo->hasWrapperRef) {
            pInfo->hasWrapperRef = false;
        }
        return;
    }

    ChildrenList &oldBrothers = pInfo->parent->d->parentInfo->children;
    // Verify if this child is part of parent list
    auto iChild = oldBrothers.find(child);
    if (iChild == oldBrothers.end())
        return;

    oldBrothers.erase(iChild);

    pInfo->parent = nullptr;

    // This will keep the wrapper reference, will wait for wrapper destruction to remove that
    if (keepReference &&
        child->d->containsCppWrapper) {
        //If have already a extra ref remove this one
        if (pInfo->hasWrapperRef)
            Py_DECREF(child);
        else
            pInfo->hasWrapperRef = true;
        return;
    }

    // Transfer ownership back to Python
    child->d->hasOwnership = giveOwnershipBack;

    // Remove parent ref
    Py_DECREF(child);
}
#endif // !Py_GIL_DISABLED

#ifndef Py_GIL_DISABLED  // free-threaded twin: see the state-lock chapter below
void setParent(PyObject *parent, PyObject *child)
{
    if (!child || child == Py_None || child == parent)
        return;

    /*
     * setParent is recursive when the child is a native Python sequence, i.e. objects not binded by Shiboken
     * like tuple and list.
     *
     * This "limitation" exists to fix the following problem: A class multiple inherits QObject and QString,
     * so if you pass this class to someone that takes the ownership, we CAN'T enter in this if, but hey! QString
     * follows the sequence protocol.
     */
    if (PySequence_Check(child) && !Object::checkType(child)) {
        // The sequence typically comes from a container conversion that may
        // have failed - a concurrent destruction of an element is enough.
        // Calling into Python with an exception set aborts the interpreter
        // ("succeeded with an exception set"), so check before and after
        // instead of walking on. The exception is left for the caller.
        if (PyErr_Occurred() != nullptr)
            return;
        Shiboken::AutoDecRef seq(PySequence_Fast(child, nullptr));
        if (seq.isNull())
            return;
        const Py_ssize_t max = PySequence_Size(seq);
        if (max < 0)
            return;
        for (Py_ssize_t i = 0; i < max; ++i) {
            Shiboken::AutoDecRef obj(PySequence_GetItem(seq.object(), i));
            if (obj.isNull())
                return;
            setParent(parent, obj);
        }
        return;
    }

    bool parentIsNull = !parent || parent == Py_None;
    auto *parent_ = reinterpret_cast<SbkObject *>(parent);
    auto *child_ = reinterpret_cast<SbkObject *>(child);

    if (!parentIsNull) {
        if (!parent_->d->parentInfo)
            parent_->d->parentInfo = new ParentInfo;

        // do not re-add a child
        if (child_->d->parentInfo && (child_->d->parentInfo->parent == parent_)) {
            if (Shiboken::pyVerbose()) {
                std::cerr << "Warning: Attempt to re-add child "
                          << child << '/' << Py_TYPE(child)->tp_name << " to parent "
                          << parent << '/' << Py_TYPE(parent)->tp_name << '\n';
            }
            return;
        }
    }

    ParentInfo *pInfo = child_->d->parentInfo;
    bool hasAnotherParent = pInfo && pInfo->parent && pInfo->parent != parent_;

    //Avoid destroy child during reparent operation
    Py_INCREF(child);

    // check if we need to remove this child from the old parent
    if (parentIsNull || hasAnotherParent)
        removeParent(child_);

    // Add the child to the new parent
    pInfo = child_->d->parentInfo;
    if (!parentIsNull) {
        if (!pInfo)
            pInfo = child_->d->parentInfo = new ParentInfo;

        pInfo->parent = parent_;
        parent_->d->parentInfo->children.insert(child_);

        // Add Parent ref
        Py_INCREF(child);

        // Remove ownership
        child_->d->hasOwnership = false;
    }

    // Remove previous safe ref
    Py_DECREF(child);
}
#endif // !Py_GIL_DISABLED

#ifndef Py_GIL_DISABLED  // free-threaded twin: see the state-lock chapter below
void deallocData(SbkObject *self, bool cleanup)
{
    // Make cleanup if this is not a wrapper otherwise this will be done on wrapper destructor
    if(cleanup) {
        removeParent(self);

        if (self->d->parentInfo)
            _destroyParentInfo(self, true);

        clearReferences(self);
    }

    if (self->d->cptr) {
        // Remove from BindingManager
        Shiboken::BindingManager::instance().releaseWrapper(self);
        delete[] self->d->cptr;
        self->d->cptr = nullptr;
        // delete self->d; PYSIDE-205: wrong!
    }
    delete self->d; // PYSIDE-205: always delete d.
    Py_XDECREF(self->ob_dict);
    PepExt_TypeCallFree(reinterpret_cast<PyObject *>(self));
}
#endif // !Py_GIL_DISABLED

void setTypeUserData(SbkObject *wrapper, void *userData, DeleteUserDataFunc d_func)
{
    auto *type = Shiboken::pyType(wrapper);
    auto *sotp = PepType_SOTP(type);
    if (sotp->user_data)
        sotp->d_func(sotp->user_data);

    sotp->d_func = d_func;
    sotp->user_data = userData;
}

void *getTypeUserData(SbkObject *wrapper)
{
    auto *type = Shiboken::pyType(wrapper);
    return PepType_SOTP(type)->user_data;
}

static inline bool isNone(const PyObject *o)
{
    return o == nullptr || o == Py_None;
}

#ifndef Py_GIL_DISABLED  // free-threaded twin: see the state-lock chapter below
static void removeRefCountKey(SbkObject *self, const std::string &key)
{
    if (self->d->referredObjects) {
        const auto iterPair = self->d->referredObjects->equal_range(key);
        if (iterPair.first != iterPair.second) {
            decRefPyObjectList(iterPair.first, iterPair.second);
            self->d->referredObjects->erase(iterPair.first, iterPair.second);
        }
    }
}

void keepReference(SbkObject *self, const char *keyC, PyObject *referredObject, bool append)
{
    std::string key(keyC);

    if (isNone(referredObject)) {
        removeRefCountKey(self, key);
        return;
    }

    if (!self->d->referredObjects) {
        self->d->referredObjects =
            new Shiboken::RefCountMap{RefCountMap::value_type{key, referredObject}};
        Py_INCREF(referredObject);
        return;
    }

    RefCountMap &refCountMap = *(self->d->referredObjects);
    const auto iterPair = refCountMap.equal_range(key);
    if (std::any_of(iterPair.first, iterPair.second,
                    [referredObject](const RefCountMap::value_type &v) { return v.second == referredObject; })) {
        return;
    }

    if (!append && iterPair.first != iterPair.second) {
        decRefPyObjectList(iterPair.first, iterPair.second);
        refCountMap.erase(iterPair.first, iterPair.second);
    }

    refCountMap.insert(RefCountMap::value_type{key, referredObject});
    Py_INCREF(referredObject);
}

void removeReference(SbkObject *self, const char *key, PyObject *referredObject)
{
    if (!isNone(referredObject))
        removeRefCountKey(self, std::string(key));
}

void clearReferences(SbkObject *self)
{
    if (!self->d->referredObjects)
        return;

    RefCountMap &refCountMap = *(self->d->referredObjects);
    for (auto it = refCountMap.begin(), end = refCountMap.end(); it != end; ++it)
        Py_DECREF(it->second);
    self->d->referredObjects->clear();
}
#endif // !Py_GIL_DISABLED

#ifdef Py_GIL_DISABLED
// ---- State-lock transactions ----------------------------------------------
//
// The free-threaded implementations of everything above that touches the
// shared binding state. They are collected here rather than placed next to
// their counterparts so that a build with a GIL compiles the original file,
// unmoved and unindented - what it gets is this chapter removed, nothing
// else. Read them as one unit: they share the contract in sbkstatelock.h.
//
// Anyone fixing a bug in one of the originals above has to fix its twin here.
//
// The "Locked" suffix means: the caller holds the state lock, and the function
// obeys the contract in sbkstatelock.h - no Python call-out, no decref, no
// destructor, no other lock. Anything of that kind goes into the
// DeferredActions list and runs after the unlock.

static void stampOwnedSetLocked(SbkObject *root);

static void **extractDestructionLocked(SbkObject *self, DeferredActions &deferred,
                                       const DestructorFunctions &dtors)
{
    SBK_ASSERT_STATE_LOCKED();
    auto *priv = self->d;
    auto *sotp = PepType_SOTP(Shiboken::pyType(self));
    // Room for the destructors before the stamp, which is one-way: a failure
    // after it would leave the owned set claimed and never destroyed.
    if (Shiboken::FreeThreading::optionEnabled(Shiboken::FreeThreading::TransactionPrepare))
        deferred.reserve(sotp->is_multicpp ? dtors.size() : 1);
    // The claim covers exactly what is about to be destroyed, and from here it
    // is no longer derived from edges that may still move.
    stampOwnedSetLocked(self);
    // The destructors were gathered before the lock; only the instance
    // pointers are read here. The type cannot have changed under a wrapper,
    // so the check is that the gathered list still fits what is being
    // destroyed.
    if (sotp->is_multicpp) {
        assert(!dtors.empty());
        for (size_t i = 0; i < dtors.size(); ++i)
            deferred.addDestructor(dtors[i], priv->cptr[i]);
    } else {
        deferred.addDestructor(sotp->cpp_dtor, priv->cptr[0]);
    }
    // Detach the pointers before unlocking: from here on no other thread can
    // reach the C++ objects that are about to be destroyed. Ownership of the
    // array passes to the caller, which still needs the values for
    // releaseWrapper() and deletes it in finishDestruction().
    void **cptrs = priv->cptr;
    priv->cptr = nullptr;
    priv->validCppObject = false;
    return cptrs;
}

// Everything a C++ destructor takes with it, as far as the binding knows it:
// the object and, transitively, its children. _detachChildren() treats the
// same set as "their C++ instances belong to obj's C++ instance and are
// deleted by it". A C++ destructor can of course delete more than that; what
// it does not model is not covered here either.
static void collectOwnedLocked(SbkObject *self, std::set<SbkObject *> &seen,
                               std::vector<SbkObject *> &owned)
{
    SBK_ASSERT_STATE_LOCKED();
    if (self == nullptr || !seen.insert(self).second)
        return;
    owned.push_back(self);
    if (auto *pInfo = self->d->parentInfo) {
        for (SbkObject *child : pInfo->children)
            collectOwnedLocked(child, seen, owned);
    }
}

static std::vector<SbkObject *> collectOwnedLocked(SbkObject *root)
{
    std::set<SbkObject *> seen;
    std::vector<SbkObject *> owned;
    collectOwnedLocked(root, seen, owned);
    return owned;
}

// A destruction covers the object, not what it owns. invalidate() hands the
// owned children back blank - their entries leave the map - and the parent's
// C++ destructor deletes them a line later: the same window the object itself
// has, one level down. The children that invalidate() releases get their own
// tombstone here, retired together with the parent's.
//
// Children that carry a C++ wrapper are not in this set on purpose: nothing
// releases their entry here. Their own C++ destructor calls Object::destroy()
// and that is what takes it out - with the window Object::destroy() has and
// cannot close, which the tombstone chapter of the free-threading notes
// declares.
//
// Two more things this does not cover, both stated rather than guessed at.
// It is a snapshot taken before the destructors run, so a child reparented
// into or out of the dying object by something those destructors call is
// tracked wrongly - the first gets no tombstone, the second keeps one until
// the parent is done. And a child that is already invalid gets none either:
// the binding has disclaimed that address, and refusing it would mean
// standing over memory that may belong to something else by now.
static std::vector<DyingChild> collectDyingChildren(SbkObject *root)
{
    SBK_ASSERT_STATE_UNLOCKED();
    // Two transactions with a walk between them, not one: counting the C++
    // bases of a type goes through tp_bases, and the state lock is a leaf.
    // Increments only inside them - a decref could run a destructor there.
    std::vector<SbkObject *> candidates;
    {
        StateLockGuard guard;
        for (SbkObject *child : collectOwnedLocked(root)) {
            auto *priv = child->d;
            if (child == root || priv->cptr == nullptr || !priv->validCppObject
                || priv->containsCppWrapper) {
                continue;
            }
            Py_INCREF(reinterpret_cast<PyObject *>(child));
            candidates.push_back(child);
        }
    }

    std::vector<DyingChild> children;
    children.reserve(candidates.size());
    for (SbkObject *child : candidates) {
        auto *type = Shiboken::pyType(child);
        auto *sotp = PepType_SOTP(type);
        const int numBases = ((sotp != nullptr && sotp->is_multicpp)
                              ? Shiboken::getNumberOfCppBaseClasses(type) : 1);
        std::vector<void *> cptrs;
        {
            StateLockGuard guard;
            auto *priv = child->d;
            // Asked again: the child may have been destroyed while the walk
            // above ran, and then there is nothing left to leave behind.
            if (priv->cptr != nullptr && priv->validCppObject)
                cptrs.assign(priv->cptr, priv->cptr + numBases);
        }
        if (cptrs.empty()) {
            Py_DECREF(reinterpret_cast<PyObject *>(child));
            continue;
        }
        Py_INCREF(reinterpret_cast<PyObject *>(type));
        children.push_back({child, type, std::move(cptrs)});
    }
    return children;
}

// Finish a destruction that extractDestructionLocked() has prepared. Runs with
// no state lock held: releaseWrapper() takes the wrapper map lock and
// invalidate() walks the object graph.
static void finishDestruction(SbkObject *pyObj, DeferredActions &deferred,
                              void **cptrs)
{
    SBK_ASSERT_STATE_UNLOCKED();
    SBK_ASSERT_NO_RAW_LOCK();
    // releaseWrapper() looks the C++ pointers up in the wrapper map, so it
    // gets the snapshot: the object no longer carries them. This runs for
    // every object, not just for those with a C++ wrapper: for the others
    // invalidate() used to do it, and it cannot any more - by the time it
    // runs, the pointers are detached.
    auto &bindingManager = BindingManager::instance();
    // The same window the deallocator has, and the same answer: between
    // taking the entry out and running the destructors a lookup would see
    // true absence and publish a wrapper for an address about to die. The
    // entry stays as a tombstone; releaseWrapper() steps over it.
    const bool tombstones =
        Shiboken::FreeThreading::optionEnabled(Shiboken::FreeThreading::Tombstones);
    auto *pyType = Py_TYPE(reinterpret_cast<PyObject *>(pyObj));
    std::vector<DyingChild> children;
    if (tombstones) {
        children = collectDyingChildren(pyObj);
        bindingManager.markWrapperDying(pyObj, cptrs);
        for (const auto &child : children)
            bindingManager.markWrapperDying(child.wrapper, child.cptrs.data());
    }
    bindingManager.releaseWrapper(pyObj, cptrs);
    invalidate(pyObj);
    // The children are blank now and the destructor that deletes them has not
    // run: the window a child tombstone has to cover.
    SBK_FAILPOINT("delete-before-owned-dtor");
    deferred.run();  // the C++ destructors
    if (tombstones) {
        bindingManager.retireWrapper(pyObj, cptrs, pyType);
        for (const auto &child : children)
            bindingManager.retireWrapper(child.wrapper, child.cptrs.data(), child.type);
    }
    // Last, and with no lock held: this can be the child's final reference,
    // and its deallocator re-enters the binding layer.
    for (const auto &child : children) {
        Py_DECREF(reinterpret_cast<PyObject *>(child.wrapper));
        Py_DECREF(reinterpret_cast<PyObject *>(child.type));
    }
    delete[] cptrs;
}

// Destruction roots whose owned set still has a lease open. Guarded by the
// state lock, and normally empty - the check on the lease-release path is one
// empty(). Each entry holds a reference, released when it is finished.
static std::vector<SbkObject *> &pendingRoots()
{
    static std::vector<SbkObject *> instance;
    return instance;
}

static bool ownedSetIsBusyLocked(SbkObject *root)
{
    SBK_ASSERT_STATE_LOCKED();
    // Collected again rather than remembered: a child may have been reparented
    // away since the destruction was requested.
    const auto owned = collectOwnedLocked(root);
    return std::any_of(owned.begin(), owned.end(),
                       [](SbkObject *o) { return o->d->activeCalls != 0; });
}

// Accept a destruction claim on root, so no new lease is handed out anywhere
// in what its destructor would take, and report whether one is still open.
//
// Recorded on root alone; the members derive it, see isClaimedLocked().
// Without ClaimByAncestry the whole set is marked here, root included.
static bool claimRootLocked(SbkObject *root)
{
    SBK_ASSERT_STATE_LOCKED();
    const bool byAncestry =
        Shiboken::FreeThreading::optionEnabled(Shiboken::FreeThreading::ClaimByAncestry);
    root->d->directDestruction = true;
    const auto owned = collectOwnedLocked(root);
    bool busy = false;
    for (SbkObject *o : owned) {
        if (!byAncestry)
            o->d->directDestruction = true;
        busy |= o->d->activeCalls != 0;
    }
    return busy;
}

// A claim stops waiting and its destructors are about to run: record it on
// every member of the set as it stands now. Invalidation hands the children
// back, so from here the claim cannot be derived from their edges any more.
// Without ClaimByAncestry, claimRootLocked() has already marked the set.
static void stampOwnedSetLocked(SbkObject *root)
{
    SBK_ASSERT_STATE_LOCKED();
    if (!Shiboken::FreeThreading::optionEnabled(Shiboken::FreeThreading::ClaimByAncestry))
        return;
    for (SbkObject *o : collectOwnedLocked(root))
        o->d->directDestruction = true;
}

// Take out the roots that have become free. Called on the lease-release path.
static std::vector<SbkObject *> takeReadyRootsLocked()
{
    SBK_ASSERT_STATE_LOCKED();
    auto &roots = pendingRoots();
    std::vector<SbkObject *> ready;
    for (auto it = roots.begin(); it != roots.end(); ) {
        if (ownedSetIsBusyLocked(*it)) {
            ++it;
        } else {
            ready.push_back(*it);
            it = roots.erase(it);
        }
    }
    return ready;
}

// Deallocations waiting for a lease, the deallocator's counterpart of
// pendingRoots(). Guarded by the state lock, and normally empty.
static std::vector<PendingDealloc> &pendingDeallocs()
{
    static std::vector<PendingDealloc> instance;
    return instance;
}

// The deallocator's claim on what self's destructor takes along. Stamped on
// the whole set at once: the teardown removes the edges a derived claim
// would need. A new lease is refused from here, so the members with a lease
// open now are the only ones that can hold the destructor back. If there are
// any, they are pinned and the destructor goes to the last of them.
//
// The graph says what the destructor should take, not what it does: an edge
// from the return value heuristic, QQmlComponent::create() for one, is not
// deleted by the parent. A member with a C++ wrapper can survive with a valid
// wrapper, so the ones stamped here are pinned, and releaseDeallocStamps()
// gives the survivors their leases back.
// See "The deallocator claims the owned set" in the free-threading notes.
static bool claimDeallocLocked(SbkObject *self, PendingDealloc &pending)
{
    SBK_ASSERT_STATE_LOCKED();
    auto *pInfo = self->d->parentInfo;
    if (pInfo == nullptr || pInfo->children.empty())
        return false; // the object alone, and it is at refcount zero
    // Prepare, then commit: every allocation before the first stamp.
    const auto owned = collectOwnedLocked(self);
    std::vector<SbkObject *> busy;
    for (SbkObject *o : owned) {
        if (o != self && o->d->activeCalls != 0)
            busy.push_back(o);
    }
    pending.stamped.reserve(owned.size());
    if (!busy.empty())
        pendingDeallocs().reserve(pendingDeallocs().size() + 1);
    for (SbkObject *o : owned) {
        // Only a stamp this claim makes is taken back; an earlier one stays.
        if (o != self && o->d->containsCppWrapper && !o->d->directDestruction) {
            Py_INCREF(reinterpret_cast<PyObject *>(o));
            pending.stamped.push_back(o);
        }
        o->d->directDestruction = true;
    }
    if (busy.empty())
        return false;
    for (SbkObject *o : busy)
        Py_INCREF(reinterpret_cast<PyObject *>(o));
    Py_INCREF(reinterpret_cast<PyObject *>(pending.type));
    pending.busy = std::move(busy);
    pendingDeallocs().push_back(std::move(pending));
    return true;
}

// Past the destructor. A member it deleted went through Object::destroy()
// and has no pointer left; one that still has it survived, and is callable
// again. Drops the pins.
static void releaseDeallocStamps(const std::vector<SbkObject *> &stamped)
{
    SBK_ASSERT_STATE_UNLOCKED();
    SBK_ASSERT_NO_RAW_LOCK();
    if (stamped.empty())
        return;
    {
        StateLockGuard guard;
        for (SbkObject *o : stamped) {
            if (o->d->validCppObject && o->d->cptr != nullptr)
                o->d->directDestruction = false;
        }
    }
    for (SbkObject *o : stamped)
        Py_DECREF(reinterpret_cast<PyObject *>(o));
}

static void runDeallocStampRelease(void *data)
{
    auto *stamped = static_cast<std::vector<SbkObject *> *>(data);
    releaseDeallocStamps(*stamped);
    delete stamped;
}

// Queued behind the destructors of a deallocation handed to the main thread.
static void releaseDeallocStampsInMainThread(std::vector<SbkObject *> &&stamped)
{
    BindingManager::instance().addToDeletionInMainThread(
        {runDeallocStampRelease, new std::vector<SbkObject *>(std::move(stamped))});
}

static std::vector<PendingDealloc> takeReadyDeallocsLocked()
{
    SBK_ASSERT_STATE_LOCKED();
    auto &pending = pendingDeallocs();
    std::vector<PendingDealloc> ready;
    if (pending.empty())
        return ready;
    ready.reserve(pending.size());
    for (auto it = pending.begin(); it != pending.end(); ) {
        const bool busy = std::any_of(it->busy.begin(), it->busy.end(),
                                      [](SbkObject *o) { return o->d->activeCalls != 0; });
        if (busy) {
            ++it;
        } else {
            ready.push_back(std::move(*it));
            it = pending.erase(it);
        }
    }
    return ready;
}

// The rest of SbkDeallocWrapperCommon() for a destructor that waited: the
// same steps in the same order, with no lock held.
static void finishDealloc(PendingDealloc &pending)
{
    SBK_ASSERT_STATE_UNLOCKED();
    SBK_ASSERT_NO_RAW_LOCK();
    auto &bindingManager = BindingManager::instance();
    if (pending.deleteInMainThread && currentThreadId() != mainThreadId()) {
        if (pending.multicpp) {
            for (const auto &e : pending.entries)
                bindingManager.addToDeletionInMainThread(e);
        } else {
            bindingManager.addToDeletionInMainThread(pending.entry);
        }
        if (!pending.retiredCptrs.empty()) {
            bindingManager.retireAfterDeletionInMainThread(pending.wrapper, pending.retiredCptrs,
                                                           pending.type);
        }
        for (const auto &child : pending.children) {
            bindingManager.retireAfterDeletionInMainThread(child.wrapper, child.cptrs,
                                                           child.type);
        }
        if (!pending.stamped.empty())
            releaseDeallocStampsInMainThread(std::move(pending.stamped));
        Py_AddPendingCall(mainThreadDeletionHandler, nullptr);
    } else {
        if (pending.multicpp) {
            callDestructor(pending.entries);
        } else {
            ThreadStateSaver threadSaver;
            if (Py_IsInitialized())
                threadSaver.save();
            pending.entry.destructor(pending.entry.cppInstance);
        }
        if (!pending.retiredCptrs.empty()) {
            bindingManager.retireWrapper(pending.wrapper, pending.retiredCptrs.data(),
                                         pending.type);
        }
        for (const auto &child : pending.children)
            bindingManager.retireWrapper(child.wrapper, child.cptrs.data(), child.type);
        releaseDeallocStamps(pending.stamped);
    }
    for (const auto &child : pending.children) {
        Py_DECREF(reinterpret_cast<PyObject *>(child.wrapper));
        Py_DECREF(reinterpret_cast<PyObject *>(child.type));
    }
    for (SbkObject *o : pending.busy)
        Py_DECREF(reinterpret_cast<PyObject *>(o));
    Py_DECREF(reinterpret_cast<PyObject *>(pending.type));
}

static void callCppDestructorsImpl(SbkObject *pyObj, bool onlyIfOwned)
{
    SBK_ASSERT_STATE_UNLOCKED();
    SBK_ASSERT_NO_RAW_LOCK();
    DeferredActions deferred;
    void **cptrs = nullptr;
    bool destroyQApp = false;
    bool leftToLease = false;
    // Gathered here, outside the lock: it walks tp_bases and calls
    // PyType_IsSubtype(), which reads Python-owned type state.
    const auto dtors = getDestructorFunctions(Shiboken::pyType(pyObj));

    {
        StateLockGuard guard;
        auto *priv = pyObj->d;
        // Idempotent: a concurrent Shiboken.delete() of the same object may
        // already have destroyed it or have destruction pending. Running the
        // destructor again would null-deref / double-free.
        if (priv->cptr == nullptr || !priv->validCppObject || isClaimedLocked(pyObj))
            return;
        if (onlyIfOwned && !priv->hasOwnership)
            return;
        if (priv->isQAppSingleton && DestroyQApplication) {
            destroyQApp = true;
        } else if (claimRootLocked(pyObj)) {
            // A call is in flight somewhere in what this destructor would take
            // with it. Pinned and put aside; the release that empties the set
            // finishes it.
            Py_INCREF(reinterpret_cast<PyObject *>(pyObj));
            pendingRoots().push_back(pyObj);
            waitingClaims().fetch_add(1, std::memory_order_relaxed);
            leftToLease = true;
        } else {
            cptrs = extractDestructionLocked(pyObj, deferred, dtors);
        }
        deferred.commit();
    }

    if (destroyQApp) {
        // PYSIDE-1470: Allow to destroy the application from Shiboken.
        DestroyQApplication();
        return;
    }
    if (leftToLease)
        return;

    // Note the order change against the coarse-lock version: the wrapper is
    // removed from the registry and invalidated *before* the C++ destructor
    // runs, so no thread can look it up while the destructor is in progress.
    finishDestruction(pyObj, deferred, cptrs);
}

void callCppDestructors(SbkObject *pyObj)
{
    callCppDestructorsImpl(pyObj, false);
}

void callCppDestructorsIfOwned(SbkObject *pyObj)
{
    callCppDestructorsImpl(pyObj, true);
}

// The C++ side gave up the object: the wrapper's C++ instance is gone or is
// about to be. Called from the generated wrapper destructor and from the
// qstandarditemmodel-clear snippet. Every caller holds a reference to the
// wrapper (an AcquiredWrapper on this build), so the decref below is never
// the last one and self stays valid to the end.
void destroy(SbkObject *self, void *cppData)
{
    SBK_ASSERT_STATE_UNLOCKED();
    SBK_ASSERT_NO_RAW_LOCK();
    // External destruction arriving while a call may be in flight.
    SBK_FAILPOINT("destroy-before-detach");
    // Skip if this is called with NULL pointer this can happen in derived classes
    if (!self)
        return;
    SBK_UNUSED(cppData);

    // This can be called in c++ side
    Shiboken::GilState gil;

    // Remove all references attached to this object
    clearReferences(self);

    // Remove the object from parent control

    // Verify if this object has parent
    bool hasParentInfo = false;
    bool hasParent = false;
    {
        StateLockGuard guard;
        auto *pInfo = self->d->parentInfo;
        hasParentInfo = pInfo != nullptr;
        hasParent = hasParentInfo && pInfo->parent != nullptr;
    }

    // No check-then-act on the flag read above: the helper reads parentInfo
    // under the lock itself.
    // See "Who may read parentInfo" in the free-threading notes.
    _destroyParentInfo(self, true);

    // Without a parent the object may still be alive.
    bool dropExtraRef = false;
    if (!hasParent) {
        StateLockGuard guard;
        auto *priv = self->d;
        dropExtraRef = priv->containsCppWrapper && !priv->hasOwnership;
    }
    if (dropExtraRef) {
        // Remove extra ref used by c++ object
        Py_DECREF(reinterpret_cast<PyObject *>(self));
    }

    // Python Object is not destroyed yet. The detach used to be gated on
    // hasWrapper(cppData), which no longer means "is this registered": it
    // steps over tombstones now. Read as the old question it would leave the
    // wrapper valid over a pointer whose C++ object is gone, which is the
    // state this block exists to prevent - so the pointers themselves decide.
    void **cptrs = nullptr;
    {
        StateLockGuard guard;
        auto *priv = self->d;
        // the cpp object instance was deleted
        cptrs = priv->cptr;
        priv->cptr = nullptr;
        priv->hasOwnership = false;
        priv->validCppObject = false;
    }
    // Like finishDestruction(): the registry entry goes after the unlock
    // and with the detached pointers, because the map lock must not be
    // taken inside a transaction.
    if (cptrs != nullptr) {
        auto &bindingManager = BindingManager::instance();
        if (Shiboken::FreeThreading::optionEnabled(
                Shiboken::FreeThreading::ExternalTombstones)) {
            // Removing the entry here would leave true absence for the rest
            // of the destruction - every base destructor still to come - and
            // a conversion in that stretch gets a valid wrapper over an
            // object that is being taken apart. A tombstone instead; it
            // takes the pointer array over and falls when the memory does.
            bindingManager.markExternallyDying(self, cptrs,
                                               Py_TYPE(reinterpret_cast<PyObject *>(self)));
        } else {
            bindingManager.unregisterWrapper(self, cptrs);
            delete[] cptrs;
        }
    }
    // The external tombstone stands from here until the memory goes back,
    // which is a stretch nothing in the binding runs through.
    SBK_FAILPOINT("destroy-after-tombstone");
}

// Free everything the wrapper owns and the wrapper itself. Reached only from
// the deallocation path, so the object is at refcount zero and already out of
// the wrapper map.
void deallocData(SbkObject *self, bool cleanup)
{
    SBK_ASSERT_STATE_UNLOCKED();
    SBK_ASSERT_NO_RAW_LOCK();
    // Make cleanup if this is not a wrapper otherwise this will be done on
    // wrapper destructor. All three take the state lock themselves.
    if (cleanup) {
        removeParent(self);
        _destroyParentInfo(self, true);
        clearReferences(self);
    }

    void **cptrs = nullptr;
    {
        StateLockGuard guard;
        auto *priv = self->d;
        // A lease does not hold a reference, so at refcount zero none can be
        // open.
        assert(priv->activeCalls == 0);
        cptrs = priv->cptr;
        priv->cptr = nullptr;
        priv->validCppObject = false;
    }

    if (cptrs != nullptr) {
        // Remove from BindingManager, with the detached pointers.
        BindingManager::instance().unregisterWrapper(self, cptrs);
        delete[] cptrs;
    }
    delete self->d; // PYSIDE-205: always delete d.
    Py_XDECREF(self->ob_dict);
    PepExt_TypeCallFree(reinterpret_cast<PyObject *>(self));
}

// ---- C++ call leases -------------------------------------------------------

enum class LeaseFailure
{
    None,
    NotInitialized, // Base constructor not called.
    Deleted         // C++ object gone, or destruction pending.
};

/// Takes the lease and hands out the C++ pointer it validated. The pointer
/// has to leave the transaction with the lease: Object::destroy() clears
/// cptr under the lock without consulting activeCalls, so re-reading it
/// after the unlock can find a null pointer the lease was granted against.
static LeaseFailure acquireCallLeaseLocked(SbkObject *self, int slot,
                                           void **canonical, void **adjusted)
{
    SBK_ASSERT_STATE_LOCKED();
    auto *priv = self->d;
    // Read the flag, do not walk the type. isUserType() would call
    // checkType() and so PyType_IsSubtype(), which reads Python-owned type
    // state under our lock; the state lock has to stay a leaf. CallLease has
    // already established that this is a wrapper instance, so the subtype
    // walk is redundant here anyway.
    if (!priv->cppObjectCreated
        && PepType_SOTP(Py_TYPE(reinterpret_cast<PyObject *>(self)))->is_user_type) {
        return LeaseFailure::NotInitialized;
    }
    if (!priv->validCppObject || priv->cptr == nullptr || isClaimedLocked(self))
        return LeaseFailure::Deleted;
    ++priv->activeCalls;
    // The canonical pointer keys the call guard, the adjusted one is what
    // the holder uses.
    *canonical = priv->cptr[0];
    *adjusted = priv->cptr[slot];
    return LeaseFailure::None;
}

/// Reads the pointer array again after the lease, as a holder without the
/// copy does; used only with LeaseSnapshot cleared. Tests for null, so the
/// window reads as zero instead of crashing.
static void *rereadPointerAfterLease(SbkObject *self, PyTypeObject *desiredType)
{
    if (desiredType == nullptr) { // what voidptr.cpp read
        auto *cptr = self->d->cptr;
        return cptr != nullptr ? cptr[0] : nullptr;
    }
    auto *sourceType = Py_TYPE(reinterpret_cast<PyObject *>(self));
    if (ObjectType::hasCast(sourceType)) // what Conversions::cppPointer() read
        return ObjectType::cast(sourceType, self, desiredType);
    return cppPointer(self, desiredType);
}

// A waiting root whose last lease came back: extract and destroy it, then
// drop the pin it was queued with.
static void finishReadyRoot(SbkObject *root)
{
    DeferredActions deferred;
    void **cptrs = nullptr;
    const auto dtors = getDestructorFunctions(Shiboken::pyType(root));
    {
        StateLockGuard guard;
        // A queued root can wait long: a child with an open lease may have
        // joined its set meanwhile. Then it waits again, pin and count kept.
        if (ownedSetIsBusyLocked(root)) {
            pendingRoots().push_back(root);
            return;
        }
        // The same test the immediate path makes: collectInvalidateLocked()
        // can have cleared validCppObject without detaching the pointers,
        // and destroying those again would be a double free.
        if (root->d->validCppObject && root->d->cptr != nullptr)
            cptrs = extractDestructionLocked(root, deferred, dtors);
        // The claim has stopped waiting either way. Counted down here and
        // not where takeReadyRootsLocked() took it off the queue: until
        // the extraction has stamped the members, they still inherit it
        // from this root.
        waitingClaims().fetch_sub(1, std::memory_order_relaxed);
        // Last, after every write, the count above included.
        deferred.commit();
    }
    if (cptrs != nullptr)
        finishDestruction(root, deferred, cptrs);
    // The pin. No lock held: this can run a destructor.
    Py_DECREF(reinterpret_cast<PyObject *>(root));
}

// Entries of the main thread's deletion queue. deferredDeleteQObject()
// drains that queue from other threads, detached: such a caller only puts
// the entry back, before touching anything Python.
static bool requeuedForMainThread(void (*run)(void *), void *data)
{
    if (currentThreadId() == mainThreadId())
        return false;
    BindingManager::instance().addToDeletionInMainThread({run, data});
    Py_AddPendingCall(mainThreadDeletionHandler, nullptr);
    return true;
}

static void runReadyRoot(void *root)
{
    if (requeuedForMainThread(runReadyRoot, root))
        return;
    Shiboken::Errors::Stash errorStash;
    finishReadyRoot(static_cast<SbkObject *>(root));
}

static void runReadyDealloc(void *data)
{
    if (requeuedForMainThread(runReadyDealloc, data))
        return;
    Shiboken::Errors::Stash errorStash;
    std::unique_ptr<PendingDealloc> pending(static_cast<PendingDealloc *>(data));
    finishDealloc(*pending);
}

static void releaseCallLease(SbkObject *self)
{
    SBK_ASSERT_STATE_UNLOCKED();
    SBK_ASSERT_NO_RAW_LOCK();
    // The window a lease exists for: another thread may reach the same
    // wrapper between the native call and the lease coming back.
    SBK_FAILPOINT("lease-before-release");
    std::vector<SbkObject *> ready;
    std::vector<PendingDealloc> readyDeallocs;

    {
        StateLockGuard guard;
        // Not filtered by whether this object is claimed: a lease taken before
        // the claim, or before the edge that brought it in, is what pins the
        // root and it has to be counted out here. The normal case stays two
        // empty().
        if (--self->d->activeCalls == 0) {
            if (!pendingRoots().empty())
                ready = takeReadyRootsLocked();
            if (!pendingDeallocs().empty())
                readyDeallocs = takeReadyDeallocsLocked();
        }
    }

    if (ready.empty() && readyDeallocs.empty())
        return;

    // A lease is released on every exit of a generated wrapper, a raised
    // exception included, and the destruction below calls into Python.
    Shiboken::Errors::Stash errorStash;

    // A type destroyed in the main thread waits in its queue, pinned and still
    // claimed, and takes what follows it along, so the order holds.
    // See "A deferred destruction keeps the main thread" in the free-threading notes.
    auto &bindingManager = BindingManager::instance();
    bool queued = false;
    for (SbkObject *root : ready) {
        queued |= PepType_SOTP(Shiboken::pyType(root))->delete_in_main_thread
                  && currentThreadId() != mainThreadId();
        if (queued)
            bindingManager.addToDeletionInMainThread({runReadyRoot, root});
        else
            finishReadyRoot(root);
    }
    // After the roots: a waiting root inside a deallocation's set goes first,
    // the order the two requests came in.
    for (auto &pending : readyDeallocs) {
        if (queued) {
            bindingManager.addToDeletionInMainThread(
                {runReadyDealloc, new PendingDealloc(std::move(pending))});
        } else {
            finishDealloc(pending);
        }
    }
    if (queued)
        Py_AddPendingCall(mainThreadDeletionHandler, nullptr);
}

/// Whether pyObj is a wrapper instance and needs a lease.
/// See "Which objects a lease accepts" in the free-threading notes;
/// MetatypeSubclassLease.
static bool needsCallLease(PyObject *pyObj)
{
    if (Shiboken::FreeThreading::optionEnabled(Shiboken::FreeThreading::MetatypeSubclassLease))
        return Object::checkType(pyObj);
    return Py_TYPE(reinterpret_cast<PyObject *>(Py_TYPE(pyObj))) == SbkObjectType_TypeF();
}

CallLease::CallLease(PyObject *pyObj, Guard guardMode)
{
    acquire(pyObj, nullptr, guardMode);
}

CallLease::CallLease(PyObject *pyObj, PyTypeObject *desiredType, Guard guardMode)
{
    acquire(pyObj, desiredType, guardMode);
}

void CallLease::acquire(PyObject *pyObj, PyTypeObject *desiredType, Guard guardMode)
{
    // Same acceptance as isValid(PyObject *, bool): anything that is not a
    // wrapper instance needs no lease. A type object is not a wrapper
    // instance, so it needs none either.
    if (pyObj == nullptr || pyObj == Py_None || !needsCallLease(pyObj)) {
        m_valid = true;
        return;
    }

    auto *self = reinterpret_cast<SbkObject *>(pyObj);
    auto *sourceType = Py_TYPE(pyObj);
    auto *sotp = PepType_SOTP(sourceType);

    // Before the lock: getTypeIndexOnHierarchy() calls PyType_IsSubtype(),
    // and the state lock has to stay a leaf.
    int slot = 0;
    if (desiredType != nullptr && sotp->is_multicpp)
        slot = getTypeIndexOnHierarchy(sourceType, desiredType);

    LeaseFailure failure = LeaseFailure::None;
    void *canonical = nullptr;
    void *adjusted = nullptr;
    {
        StateLockGuard guard;
        failure = acquireCallLeaseLocked(self, slot, &canonical, &adjusted);
    }

    if (failure == LeaseFailure::None) {
        m_self = self;
        m_pointer = adjusted;
        // The special cast depends on the pointer alone and runs on the copy.
        if (desiredType != nullptr && sotp->mi_specialcast != nullptr)
            m_pointer = sotp->mi_specialcast(m_pointer, desiredType);

        // Qt is not thread-safe per object, and without a GIL nothing else
        // serializes two threads that reach the same one. Taken outside the
        // state lock, because it spans the C++ call. Keyed on the canonical
        // pointer, so that two bases of one object share one guard.
        //
        // Only for the receiver: nesting critical sections does not lock two
        // objects, the inner one suspends the outer - see Guard in the header.
        if (guardMode == Guard::Take)
            m_guard.acquire(canonical);

        m_valid = true;
        // Lease and guard are in place, the native call has not run yet:
        // the point where a test lets destruction reach the same wrapper.
        SBK_FAILPOINT("lease-after-acquire");
        if (!Shiboken::FreeThreading::optionEnabled(Shiboken::FreeThreading::LeaseSnapshot))
            m_pointer = rereadPointerAfterLease(self, desiredType);
        return;
    }

    // Raising is a Python call-out and happens after the transaction.
    if (failure == LeaseFailure::NotInitialized) {
        PyErr_Format(PyExc_RuntimeError,
                     "libshiboken: '__init__' method of object's base class (%s) not called.",
                     Py_TYPE(pyObj)->tp_name);
    } else {
        PyErr_Format(PyExc_RuntimeError,
                     "libshiboken: Internal C++ object (%s) already deleted.",
                     Py_TYPE(pyObj)->tp_name);
    }
}

CallLease::~CallLease()
{
    // Let go before the release, which may run the C++ destructor.
    m_guard.release();
    if (m_self != nullptr)
        releaseCallLease(m_self);
}

struct ConversionLeases::Entry
{
    Entry(PyObject *pyObj, PyTypeObject *desiredType, Entry *following)
        : pin(Py_NewRef(pyObj)),
          lease(pyObj, desiredType, CallLease::Guard::Omit),
          next(following)
    {
    }

    // Declared before the lease, so it is released after it: ~CallLease
    // writes to the wrapper, and the container may have dropped the element.
    AutoDecRef pin;
    CallLease lease;
    Entry *next;
};

static thread_local ConversionLeases *collectingConversionLeases = nullptr;

ConversionLeases::ConversionLeases()
    : m_previous(collectingConversionLeases)
{
    collectingConversionLeases = this;
}

ConversionLeases::~ConversionLeases()
{
    endCollect();
    // With no lock held: the last lease may run a deferred C++ destructor.
    while (m_entries != nullptr) {
        auto *entry = m_entries;
        m_entries = entry->next;
        delete entry;
    }
}

void ConversionLeases::endCollect()
{
    if (!m_collecting)
        return;
    assert(collectingConversionLeases == this);
    collectingConversionLeases = m_previous;
    m_collecting = false;
}

ConversionLeases *ConversionLeases::collecting()
{
    // See "Leases taken inside a conversion" in the free-threading notes;
    // ConversionLeasesKept.
    if (!Shiboken::FreeThreading::optionEnabled(Shiboken::FreeThreading::ConversionLeasesKept))
        return nullptr;
    return collectingConversionLeases;
}

bool ConversionLeases::add(PyObject *pyObj, PyTypeObject *desiredType, void **cppOut)
{
    *cppOut = nullptr;
    auto *entry = new (std::nothrow) Entry(pyObj, desiredType, m_entries);
    if (entry == nullptr) {
        PyErr_NoMemory();
        return false;
    }
    if (!entry->lease) {
        delete entry;
        return false;
    }
    m_entries = entry;
    *cppOut = entry->lease.pointer();
    return true;
}

void getOwnership(SbkObject *sbkObj)
{
    SBK_ASSERT_STATE_UNLOCKED();
    DeferredActions deferred;
    bool revalidate = false;

    {
        StateLockGuard guard;
        auto *priv = sbkObj->d;
        // skip if already have the ownership
        if (priv->hasOwnership)
            return;
        // skip if this object has parent
        if (priv->parentInfo && priv->parentInfo->parent)
            return;

        // Room for the one action below, before the flag is written.
        // See "Prepare, then commit" in the free-threading notes.
        if (priv->containsCppWrapper
            && Shiboken::FreeThreading::optionEnabled(
                   Shiboken::FreeThreading::TransactionPrepare)) {
            deferred.reserve(1);
        }

        // Get back the ownership
        priv->hasOwnership = true;

        if (priv->containsCppWrapper)
            deferred.addDecref(sbkObj);  // Remove extra ref
        else
            revalidate = true;
        deferred.commit();
    }

    if (revalidate)
        makeValid(sbkObj);  // Make the object valid again; walks the graph
    deferred.run();
}

void releaseOwnership(SbkObject *sbkObj)
{
    SBK_ASSERT_STATE_UNLOCKED();
    auto *ob = reinterpret_cast<PyObject *>(sbkObj);
    auto *selfType = Py_TYPE(ob);
    const bool isValueType =
        Shiboken::Conversions::pythonTypeIsValueType(PepType_SOTP(selfType)->converter);
    bool needsInvalidate = false;

    {
        StateLockGuard guard;
        auto *priv = sbkObj->d;
        // skip if the ownership have already moved to c++
        if (!priv->hasOwnership || isValueType)
            return;

        // remove object ownership
        priv->hasOwnership = false;

        // If We have control over object life
        if (priv->containsCppWrapper) {
            // Pinning increment: an incref cannot run user code, so it is one
            // of the audited exceptions to the "no refcount work" rule. Keeps
            // the Python object alive until the wrapper destructor call.
            Py_INCREF(ob);
        } else {
            needsInvalidate = true;
        }
    }

    // If I do not know when this object will die We need to invalidate this to
    // avoid use after free. Walks the graph and touches the wrapper map, so it
    // runs outside the transaction.
    if (needsInvalidate)
        invalidate(sbkObj);
}

// What invalidation decides under the state lock but must not do there:
// releasing wrappers takes the wrapper map lock, and detaching children takes
// the state lock again (it is not recursive).
struct InvalidationPlan
{
    struct Detach
    {
        SbkObject *parent;
        SbkObject *child;
    };
    std::vector<SbkObject *> releaseWrappers;
    std::vector<Detach> detachChildren;
};

static void removeParentFrom(SbkObject *parent, SbkObject *child, bool giveOwnershipBack,
                             bool keepReference);

// Pin an object the walk has to survive the unlock. Running the plan decrefs
// (removeParent() hands the parent reference back), and that cascade can free
// an object a later step - or, in makeValid(), a later round - still has to
// touch. Increments are permitted inside the transaction, decrements are not,
// so the caller drops the pins with no lock held.
static void pinForPlan(PyObject *pyObj, std::vector<PyObject *> &pins)
{
    SBK_ASSERT_STATE_LOCKED();
    Py_INCREF(pyObj);
    pins.push_back(pyObj);
}

// The object and its children, and deliberately not what it refers to, for
// the reason the GIL twin recursive_invalidate() spells out.
static void collectInvalidateLocked(SbkObject *self, std::set<SbkObject *> &seen,
                                    InvalidationPlan &plan,
                                    std::vector<PyObject *> &pins)
{
    SBK_ASSERT_STATE_LOCKED();
    // Skip if this object not is a valid object or if it's already been seen
    if (!self || reinterpret_cast<PyObject *>(self) == Py_None || seen.find(self) != seen.end())
        return;
    seen.insert(self);

    if (!self->d->containsCppWrapper) {
        self->d->validCppObject = false; // Mark object as invalid only if this is not a wrapper class
        plan.releaseWrappers.push_back(self);
    }

    // If it is a parent invalidate all children.
    if (self->d->parentInfo) {
        // Create a copy because this list can be changed during the process
        ChildrenList copy = self->d->parentInfo->children;

        for (SbkObject *child : copy) {
            // invalidate the child
            collectInvalidateLocked(child, seen, plan, pins);

            // if the parent not is a wrapper class, then remove children from him, because We do not know when this object will be destroyed
            if (!self->d->validCppObject) {
                keepClaimThroughTeardownLocked(child);
                plan.detachChildren.push_back({self, child});
                pinForPlan(reinterpret_cast<PyObject *>(child), pins);
            }
        }
    }
}

// Run what the transaction collected, with no lock held.
static void runInvalidationPlan(const InvalidationPlan &plan)
{
    SBK_ASSERT_STATE_UNLOCKED();
    auto &bindingManager = BindingManager::instance();
    for (SbkObject *o : plan.releaseWrappers)
        bindingManager.releaseWrapper(o);
    // Collected in an earlier transaction: the child may have a new parent.
    for (const auto &edge : plan.detachChildren)
        removeParentFrom(edge.parent, edge.child, true, true);
}

// One transaction - the parent/child walk is plain recursion under the lock -
// then the part that may not run under it.
static void invalidateRoots(const std::vector<SbkObject *> &roots)
{
    SBK_ASSERT_STATE_UNLOCKED();
    // The pins are dropped at the end, and the last one can run a destructor.
    SBK_ASSERT_NO_RAW_LOCK();
    std::vector<PyObject *> pins;
    InvalidationPlan plan;
    {
        StateLockGuard guard;
        std::set<SbkObject *> seen;
        for (SbkObject *o : roots)
            collectInvalidateLocked(o, seen, plan, pins);
    }
    runInvalidationPlan(plan);
    // No lock held: these decrefs may run destructors that re-enter the
    // binding layer.
    for (PyObject *o : pins)
        Py_DECREF(o);
}

void invalidate(PyObject *pyobj)
{
    SBK_ASSERT_STATE_UNLOCKED();
    // splitPyObject() runs the sequence protocol: never under the lock.
    invalidateRoots(splitPyObject(pyobj));
}

void invalidate(SbkObject *self)
{
    SBK_ASSERT_STATE_UNLOCKED();
    invalidateRoots({self});
}

// A referred object waiting to be classified. Deciding whether it is a
// wrapper means PyType_IsSubtype(), which the state lock may not span, so
// the decision happens between two rounds - and the entry it came from can
// change while it does. Owner and key are what the next transaction checks
// it against; the object itself is pinned, so the pointer stays readable.
struct ReferredCandidate
{
    SbkObject *owner;
    std::string key;
    PyObject *object;
};

// Whether the entry this candidate came from is still there and still points
// at the same object. What it rejects is a reference dropped between two
// rounds - clearReferencesLocked() and removeRefCountKeyLocked() erase under
// the lock - so the walk does not follow a link that no longer exists.
//
// What it does not do is ask whether the object itself is still alive:
// invalidation and destruction leave the owner's entry in place, and marking
// a destroyed wrapper valid again is what makeValid() has always done, with
// a GIL as without one. That belongs to the destruction work, not here.
static bool referredEntryStillValid(const ReferredCandidate &candidate)
{
    SBK_ASSERT_STATE_LOCKED();
    const RefCountMap *map = candidate.owner->d->referredObjects;
    if (map == nullptr)
        return false;
    const auto range = map->equal_range(candidate.key);
    for (auto it = range.first; it != range.second; ++it) {
        if (it->second == candidate.object)
            return true;
    }
    return false;
}

// Counterpart of collectInvalidateLocked() for parentInfo->children, and it
// also follows referredObjects, which is what makes it run in rounds:
// deciding what a referred PyObject is runs the sequence protocol, which the
// state lock may not span. It qualifies as a transaction: it sets a flag,
// walks two plain containers and pins what the next round has to look at.
// No decref, no Python protocol, no second lock.
//
// `seen` and not validCppObject alone: the GIL twin can use the flag as its
// visited marker because nothing else runs, but here another thread clears
// it between two rounds, and the walk would find work again every time it
// did. `seen` only grows, so the round loop ends whatever the other thread
// does.
static void collectMakeValidLocked(SbkObject *self, std::set<SbkObject *> &seen,
                                   std::vector<ReferredCandidate> &referred,
                                   std::vector<PyObject *> &pins)
{
    SBK_ASSERT_STATE_LOCKED();
    // Skip if this object not is a valid object or if it's already been seen
    if (!self || reinterpret_cast<PyObject *>(self) == Py_None
        || self->d->validCppObject || seen.find(self) != seen.end()) {
        return;
    }
    seen.insert(self);

    // Mark object as invalid only if this is not a wrapper class
    self->d->validCppObject = true;
    // Every object visited here is an owner of the entries collected below,
    // and referredEntryStillValid() reads its map in a later round.
    pinForPlan(reinterpret_cast<PyObject *>(self), pins);

    // If it is a parent make  all children valid
    if (self->d->parentInfo) {
        for (SbkObject *child : self->d->parentInfo->children)
            collectMakeValidLocked(child, seen, referred, pins);
    }

    // If has ref to other objects make all valid again
    if (self->d->referredObjects) {
        const RefCountMap &refCountMap = *(self->d->referredObjects);
        for (const auto &p : refCountMap) {
            referred.push_back({self, p.first, p.second});
            pinForPlan(p.second, pins);
        }
    }
}

// Revive an object invalidation marked, and everything it reaches.
//
// No test in this tree drives the referred-object half of this walk, and none
// can: getOwnership() is the only caller, the generator emits it for a return
// value only (owner="target"; no typesystem in the tree puts it on an input
// argument), and a return value is a fresh conversion from a C++ pointer. An
// object can only be invalid if invalidate() marked it, which it does only
// for a wrapper it unregisters in the same transaction - so the conversion
// cannot find that wrapper again and hands out a new, valid one, which leaves
// here at the first line. The walk below is therefore correct by construction
// rather than by measurement, and it is written to match the pre-free-
// threading semantics exactly for that reason.
void makeValid(SbkObject *self)
{
    SBK_ASSERT_STATE_UNLOCKED();
    // The pins are dropped at the end, and the last one can run a destructor.
    SBK_ASSERT_NO_RAW_LOCK();
    // Walk the graph in rounds: a round marks under the lock and collects the
    // referred objects it found, they are classified outside it, and the next
    // round revalidates the entries they came from before it follows them.
    std::vector<SbkObject *> roots{self};
    std::set<SbkObject *> seen;
    std::vector<ReferredCandidate> pending;
    // Held to the end of the walk, not per round: the objects a round reaches
    // through the referred entries become the next round's roots, so dropping
    // the pins early would move the dangling pointer one round on.
    std::vector<PyObject *> pins;
    while (!roots.empty() || !pending.empty()) {
        std::vector<ReferredCandidate> referred;
        {
            StateLockGuard guard;
            for (const ReferredCandidate &candidate : pending) {
                if (referredEntryStillValid(candidate)) {
                    collectMakeValidLocked(reinterpret_cast<SbkObject *>(candidate.object),
                                           seen, referred, pins);
                }
            }
            for (SbkObject *o : roots)
                collectMakeValidLocked(o, seen, referred, pins);
        }

        // Classified with no lock held: checkType() walks the type
        // hierarchy, which the state lock may not span. It has to stay
        // checkType() - a metatype identity test answers "not a wrapper"
        // for class Meta(type(QObject), ABCMeta) and leaves the object
        // invalidated for good.
        roots.clear();
        pending.clear();
        for (const ReferredCandidate &candidate : referred) {
            if (Object::checkType(candidate.object))
                pending.push_back(candidate);
        }
    }
    // No lock held: the last reference can be here, and dropping it runs a
    // destructor that re-enters the binding layer.
    for (PyObject *o : pins)
        Py_DECREF(o);
}

static void removeParentLocked(SbkObject *child, bool giveOwnershipBack,
                               bool keepReference, DeferredActions &deferred)
{
    SBK_ASSERT_STATE_LOCKED();
    ParentInfo *pInfo = child->d->parentInfo;
    if (!pInfo || !pInfo->parent) {
        if (pInfo && pInfo->hasWrapperRef) {
            pInfo->hasWrapperRef = false;
        }
        return;
    }

    ChildrenList &oldBrothers = pInfo->parent->d->parentInfo->children;
    // Verify if this child is part of parent list
    auto iChild = oldBrothers.find(child);
    if (iChild == oldBrothers.end())
        return;

    // Prepare, then commit: room for the one deferred action below, the edge
    // reference in either branch, before anything is written.
    if (Shiboken::FreeThreading::optionEnabled(Shiboken::FreeThreading::TransactionPrepare))
        deferred.reserve(1);

    oldBrothers.erase(iChild);

    pInfo->parent = nullptr;

    // This will keep the wrapper reference, will wait for wrapper destruction to remove that
    if (keepReference &&
        child->d->containsCppWrapper) {
        //If have already a extra ref remove this one
        if (pInfo->hasWrapperRef)
            deferred.addDecref(child);
        else
            pInfo->hasWrapperRef = true;
        return;
    }

    // Transfer ownership back to Python
    child->d->hasOwnership = giveOwnershipBack;

    // Remove parent ref. This can be the last one: it must not run while the
    // graph is locked, because deallocation re-enters the binding layer.
    deferred.addDecref(child);
}

void removeParent(SbkObject *child, bool giveOwnershipBack, bool keepReference)
{
    SBK_ASSERT_STATE_UNLOCKED();
    DeferredActions deferred;
    {
        StateLockGuard guard;
        removeParentLocked(child, giveOwnershipBack, keepReference, deferred);
        deferred.commit();
    }
    deferred.run();
}

// removeParent() for a teardown that read the edge in an earlier transaction:
// only the edge from \a parent goes. A child reparented in between keeps its
// new one.
// See "A teardown detaches the edge it read" in the free-threading notes.
static void removeParentFrom(SbkObject *parent, SbkObject *child, bool giveOwnershipBack,
                             bool keepReference)
{
    SBK_ASSERT_STATE_UNLOCKED();
    if (!Shiboken::FreeThreading::optionEnabled(Shiboken::FreeThreading::DetachCheckedParent)) {
        removeParent(child, giveOwnershipBack, keepReference);
        return;
    }
    DeferredActions deferred;
    {
        StateLockGuard guard;
        auto *pInfo = child->d->parentInfo;
        if (pInfo == nullptr || pInfo->parent != parent)
            return;
        removeParentLocked(child, giveOwnershipBack, keepReference, deferred);
        deferred.commit();
    }
    deferred.run();
}

// One round of _detachChildren(): the child is invalidated and its edge
// removed in the transaction that picked it, so no reparent can come in
// between. Returns false once parent has no child left.
// See "A teardown detaches the edge it read" in the free-threading notes.
static bool detachFirstChild(SbkObject *parent, bool keepReference)
{
    SBK_ASSERT_STATE_UNLOCKED();
    // The pins are dropped at the end, and the last one can run a destructor.
    SBK_ASSERT_NO_RAW_LOCK();
    InvalidationPlan plan;
    std::vector<PyObject *> pins;
    DeferredActions deferred;
    {
        StateLockGuard guard;
        ParentInfo *pInfo = parent->d->parentInfo;
        if (pInfo == nullptr || pInfo->children.empty())
            return false;
        SbkObject *first = *pInfo->children.begin();
        // Room for removeParentLocked()'s decref before the first write.
        // See "Prepare, then commit" in the free-threading notes.
        if (Shiboken::FreeThreading::optionEnabled(Shiboken::FreeThreading::TransactionPrepare))
            deferred.reserve(1);
        // Nothing else keeps the child alive once the edge reference is back.
        pinForPlan(reinterpret_cast<PyObject *>(first), pins);
        keepClaimThroughTeardownLocked(first);
        std::set<SbkObject *> seen;
        collectInvalidateLocked(first, seen, plan, pins);
        removeParentLocked(first, false, keepReference, deferred);
        deferred.commit();
    }
    // Where the cleared path stands between picking and removing; here the
    // edge is already gone.
    SBK_FAILPOINT("detach-mid-round");
    runInvalidationPlan(plan);
    deferred.run();
    for (PyObject *o : pins)
        Py_DECREF(o);
    return true;
}

// Result of the setParent() transaction, for the diagnostics that must not be
// printed while the state lock is held.
enum class SetParentResult
{
    Done,
    ReAddedChild
};

static SetParentResult setParentLocked(SbkObject *parent, SbkObject *child,
                                       DeferredActions &deferred)
{
    SBK_ASSERT_STATE_LOCKED();
    const bool parentIsNull = parent == nullptr;

    if (!parentIsNull) {
        // Plain operator new, not a Python allocation: permitted under the
        // state lock.
        if (!parent->d->parentInfo)
            parent->d->parentInfo = new ParentInfo;

        // do not re-add a child
        if (child->d->parentInfo && child->d->parentInfo->parent == parent)
            return SetParentResult::ReAddedChild;
    }

    ParentInfo *pInfo = child->d->parentInfo;
    const bool hasAnotherParent = pInfo && pInfo->parent && pInfo->parent != parent;
    const bool prepareFirst =
        Shiboken::FreeThreading::optionEnabled(Shiboken::FreeThreading::TransactionPrepare);

    // Prepare, then commit: every allocation (deferred slot, ParentInfo, set
    // insert) before the old edge is touched.
    // See "Prepare, then commit" in the free-threading notes.
    if (!parentIsNull && prepareFirst) {
        // Covers removeParentLocked()'s add below; its own reserve(1) then
        // finds the room and cannot throw.
        deferred.reserve(1);
        if (!pInfo)
            pInfo = child->d->parentInfo = new ParentInfo;
        parent->d->parentInfo->children.insert(child);
    }

    // check if we need to remove this child from the old parent.
    // giveOwnershipBack must stay true: this is what removeParent()'s default
    // argument did before the transaction was made explicit. Without it,
    // setParent(None) leaves the object owned by C++, it is never destroyed
    // and destroyed() never fires (bug_576).
    if (parentIsNull || hasAnotherParent)
        removeParentLocked(child, true, false, deferred);

    // Add the child to the new parent. removeParentLocked() keeps
    // parentInfo, so the re-read is harmless.
    pInfo = child->d->parentInfo;
    if (!parentIsNull) {
        if (!pInfo)
            pInfo = child->d->parentInfo = new ParentInfo;

        pInfo->parent = parent;
        if (!prepareFirst) {
            // TransactionPrepare cleared: the insert after the pointer write,
            // where a failure leaves a one-sided edge.
            parent->d->parentInfo->children.insert(child);
        }

        // Add Parent ref (pinning increment, see releaseOwnership())
        Py_INCREF(reinterpret_cast<PyObject *>(child));

        // Remove ownership
        child->d->hasOwnership = false;
    }

    return SetParentResult::Done;
}

void setParent(PyObject *parent, PyObject *child)
{
    SBK_ASSERT_STATE_UNLOCKED();
    if (!child || child == Py_None || child == parent)
        return;

    /*
     * setParent is recursive when the child is a native Python sequence, i.e. objects not binded by Shiboken
     * like tuple and list.
     *
     * This "limitation" exists to fix the following problem: A class multiple inherits QObject and QString,
     * so if you pass this class to someone that takes the ownership, we CAN'T enter in this if, but hey! QString
     * follows the sequence protocol.
     */
    if (PySequence_Check(child) && !Object::checkType(child)) {
        // The sequence typically comes from a container conversion that may
        // have failed - a concurrent destruction of an element is enough.
        // Calling into Python with an exception set aborts the interpreter
        // ("succeeded with an exception set"), so check before and after
        // instead of walking on. The exception is left for the caller.
        if (PyErr_Occurred() != nullptr)
            return;
        Shiboken::AutoDecRef seq(PySequence_Fast(child, nullptr));
        if (seq.isNull())
            return;
        const Py_ssize_t max = PySequence_Size(seq);
        if (max < 0)
            return;
        for (Py_ssize_t i = 0; i < max; ++i) {
            Shiboken::AutoDecRef obj(PySequence_GetItem(seq.object(), i));
            if (obj.isNull())
                return;
            setParent(parent, obj);
        }
        return;
    }

    const bool parentIsNull = !parent || parent == Py_None;
    auto *parent_ = parentIsNull ? nullptr : reinterpret_cast<SbkObject *>(parent);
    auto *child_ = reinterpret_cast<SbkObject *>(child);

    // Keep the child alive through the reparent; RAII, as the out-of-memory
    // path returns early.
    Shiboken::AutoDecRef pin(Py_NewRef(child));

    // Leases held, native parent changed, the binding graph still shows the
    // old edge. No test arms this yet (B6-2).
    // See the failpoint test README.
    SBK_FAILPOINT("parent-before-commit");

    DeferredActions deferred;
    SetParentResult result{};
    bool outOfMemory = false;
    try {
        StateLockGuard guard;
        result = setParentLocked(parent_, child_, deferred);
        deferred.commit();
    } catch (const std::bad_alloc &) {
        // Only a flag: reporting it calls CPython, after the unlock.
        outOfMemory = true;
    }
    if (outOfMemory) {
        // Nothing was run or written (unless TransactionPrepare is cleared).
        // See "Prepare, then commit" in the free-threading notes.
        PyErr_NoMemory();
        return;
    }
    deferred.run();

    if (result == SetParentResult::ReAddedChild && Shiboken::pyVerbose()) {
        // I/O: never under the state lock.
        std::cerr << "Warning: Attempt to re-add child "
                  << child << '/' << Py_TYPE(child)->tp_name << " to parent "
                  << parent << '/' << Py_TYPE(parent)->tp_name << '\n';
    }
}

static void removeRefCountKeyLocked(SbkObject *self, const std::string &key,
                                    DeferredActions &deferred)
{
    SBK_ASSERT_STATE_LOCKED();
    if (self->d->referredObjects) {
        const auto iterPair = self->d->referredObjects->equal_range(key);
        deferred.reserve(std::distance(iterPair.first, iterPair.second));
        for (auto it = iterPair.first; it != iterPair.second; ++it)
            deferred.addDecref(it->second);
        self->d->referredObjects->erase(iterPair.first, iterPair.second);
    }
}

static void keepReferenceLocked(SbkObject *self, const std::string &key,
                                PyObject *referredObject, bool append,
                                DeferredActions &deferred)
{
    SBK_ASSERT_STATE_LOCKED();
    if (!self->d->referredObjects) {
        self->d->referredObjects =
            new Shiboken::RefCountMap{RefCountMap::value_type{key, referredObject}};
        Py_INCREF(referredObject);  // pinning increment
        return;
    }

    RefCountMap &refCountMap = *(self->d->referredObjects);
    const auto iterPair = refCountMap.equal_range(key);
    if (std::any_of(iterPair.first, iterPair.second,
                    [referredObject](const RefCountMap::value_type &v) { return v.second == referredObject; })) {
        return;
    }

    if (!append && iterPair.first != iterPair.second) {
        deferred.reserve(std::distance(iterPair.first, iterPair.second));
        for (auto it = iterPair.first; it != iterPair.second; ++it)
            deferred.addDecref(it->second);
        refCountMap.erase(iterPair.first, iterPair.second);
        // Committed here: the map has given these references up, and the
        // insert below can still throw, which would drop an uncommitted list.
        deferred.commit();
    }

    refCountMap.insert(RefCountMap::value_type{key, referredObject});
    Py_INCREF(referredObject);  // pinning increment
}

void keepReference(SbkObject *self, const char *keyC, PyObject *referredObject, bool append)
{
    SBK_ASSERT_STATE_UNLOCKED();
    std::string key(keyC);  // allocate the key before the transaction

    DeferredActions deferred;
    {
        StateLockGuard guard;
        if (isNone(referredObject))
            removeRefCountKeyLocked(self, key, deferred);
        else
            keepReferenceLocked(self, key, referredObject, append, deferred);
        deferred.commit();
    }
    deferred.run();
}

void removeReference(SbkObject *self, const char *key, PyObject *referredObject)
{
    SBK_ASSERT_STATE_UNLOCKED();
    if (isNone(referredObject))
        return;

    const std::string keyString(key);
    DeferredActions deferred;
    {
        StateLockGuard guard;
        removeRefCountKeyLocked(self, keyString, deferred);
        deferred.commit();
    }
    deferred.run();
}

static void clearReferencesLocked(SbkObject *self, DeferredActions &deferred)
{
    SBK_ASSERT_STATE_LOCKED();
    if (!self->d->referredObjects)
        return;

    RefCountMap &refCountMap = *(self->d->referredObjects);
    deferred.reserve(refCountMap.size());
    for (const auto &p : refCountMap)
        deferred.addDecref(p.second);
    refCountMap.clear();
}

void clearReferences(SbkObject *self)
{
    SBK_ASSERT_STATE_UNLOCKED();
    DeferredActions deferred;
    {
        StateLockGuard guard;
        clearReferencesLocked(self, deferred);
        deferred.commit();
    }
    deferred.run();
}

#endif // Py_GIL_DISABLED

size_t activeCalls(SbkObject *pyObj)
{
#ifdef Py_GIL_DISABLED
    StateLockGuard guard;
    return pyObj->d->activeCalls;
#else
    SBK_UNUSED(pyObj);
    return 0;
#endif
}

SbkConverter *getConverter(PyTypeObject *type)
{
    return PepType_SOTP(type)->converter;
}

} // namespace Object

} // namespace Shiboken
