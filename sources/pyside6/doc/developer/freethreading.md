# Free-Threaded Python (PEP 703)

On a free-threaded build (`Py_GIL_DISABLED`) the interpreter no longer
serializes Python execution, so several threads can enter the bindings at the
same time. The binding layer keeps per-object bookkeeping - ownership and
validity flags, the parent/child graph, the referred-object map, the wrapper
lifecycle - which was previously protected by the GIL and by nothing else.

Shiboken replaces that protection with a short-lived lock over that
bookkeeping, plus a lease that defers destruction until a call has finished.
The lease covers the destructions the binding performs itself: a
`Shiboken.delete()`, and a parent taking its children with it. It cannot cover a
`delete` issued by C++ or by Qt: by the time the wrapper hears about that,
the object is already gone. A build with a GIL has a smaller window there,
not the same one - the destructor has to take the GIL and therefore cannot
run between the lease and the pointer read the way it can here. This
document describes both, the locks that are deliberately separate from them,
and what it all means for application code.

## The notes in four files

This file has the state lock, the call guard, the leases, the lock
inventory, and how to switch the measures off and test them. The sections
per measure are in three further files:
[Wrapper Lifecycle](freethreading-lifecycle.md) for the wrapper map,
destruction and the deallocator,
[Types and Shared State](freethreading-types.md) for type walks, lookups and
process-wide state, and
[Generated Code, Signals and QML](freethreading-bindings.md) for what
reaches the bindings' entry points.

## Where the `Bn-m` and `FTn` names come from

A few passages here, and a few comments in the sources, name a finding as
`B9-1` or a work package as `FT8`. They come from Neil Schemenauer's
free-threading review of this branch: `Bn-m` is finding *m* of its review
step *n*, `FTn` is the work package those findings were grouped into, and an
`FT8 invariant`, `design` or `validation row` is a numbered item inside that
package's handoff. The names this change uses:

| Name | What it is |
|---|---|
| B9-1 | Python type and MRO access under the state mutex |
| B13-5 | the lazy-type lock spanning type creation and import work |
| B7-2 | the deallocator clearing weakrefs while another thread has references |
| B15-1 | two threads building one object's instance meta object |
| B15-2 | the Python type parsed with the meta-object lock held |
| B15-3 | the builder's lifetime authority living in `__dict__` |
| B15-4 | arbitrary Python construction under the QML placement mutex |
| B4-1 | a lookup publishing a replacement for an identity being destroyed |
| B4-2 | the virtual-call preflight reading type state with no thread state |
| B4-3 | the multiple-inheritance offsets filled behind a sentinel check |
| B4-4 | the class hierarchy mutated while another thread walks it |
| B5-3 | a generated constructor publishing itself in separate steps |
| FT4 | carrying leases and pointer snapshots to their final use |
| FT8 | restoring the short raw-lock contract - this series |
| B5-1 | a lease holder reading the pointer array after its transaction |
| B6-1 | a child moved out of a pending parent refused for good |
| B6-2 | a child moved into a pending parent left unclaimed |
| FT7 | pending destruction that stays right while the graph changes |
| B6-4 | a failed allocation leaving a transaction half written |
| B10-3 | direct entries running on the output of a failed conversion |
| FT2 | disabling `__feature__` on free-threaded builds |
| FT3 | owning Python references and synchronized mutable layout |
| FT10 | dynamic meta-object publication and lifetime |
| FT12 | GC, shutdown, finalization and fork boundaries |
| B16-1 | the signature and converter bootstrap publishing process globals |
| B16-2 | the `qAddPostRoutine` callback queue, unsynchronized |
| B16-3 | the QObject-pointer metatype registration and its global hash |
| B16-5 | the process-global `__doc__` recursion counter |
| FT9 | synchronizing the converter and runtime global registries |
| B12-4 | a method slot delivering through a receiver pointer it does not own |
| B14-4 | method delivery to a dead weak receiver |
| B14-5 | a single-value hash losing earlier equal connections |
| FT5 | virtual callback and signal/slot ownership |

Every statement stands without them. They are here so that a reader who has
the review can find the passage a sentence came from.

## The state lock

One process-wide, *non-recursive* lock that serializes the shared binding
state. Its defining property is not what it protects but how briefly it is
held: a transaction reads and writes plain C++ containers and returns. The
contract is in `sbkstatelock.h`, and code holding the lock must not

* invoke Python or any Python protocol, or decref an object;
* call Qt, emit a signal, invoke a virtual method or run a destructor;
* block, perform I/O, or attach or detach the thread state;
* acquire any other lock.

Whatever does not fit goes into a `DeferredActions` list and runs after the
unlock. A holder can therefore neither block nor need a stop-the-world pause,
which is what makes a plain mutex the right primitive: it always reaches its
own unlock.

No lock over the *bookkeeping* is held across code the binding does not
control. One lock still spans a call, and deliberately so - the per-object
call guard below. It is a `PyCriticalSection`, so a thread that has to wait
underneath it detaches and the guard is suspended, which keeps it out of the
process-wide lock order.

Bit `StateLock`; cleared, the bookkeeping runs unlocked, which the A/B in
`run.py`'s scenario table measures.

### Prepare, then commit

A transaction can fail while it holds the state lock: a container insert or
the growth of the `DeferredActions` list may throw `std::bad_alloc`, and
whatever it has written by then stays written (B6-4). It therefore makes
every allocation it needs - room for its deferred actions, a set insert -
before its first semantic write; what follows are pointer and flag writes
into room that exists, and `DeferredActions::commit()` marks the end.

The commit also decides what the list does when it is destroyed. A committed
list owns its references and runs them, even where `run()` was not reached.
An uncommitted list is dropped: the transaction unwound before the transfer,
the protected state still owns those references, and releasing them would
release them twice - a leak is the side an unwind has to fall on.
`keepReferenceLocked()` commits early, once the map has given its references
up, since the insert after that can still throw.

`setParentLocked()` takes `removeParentLocked()`'s slot before it inserts the
child into the new parent's set; in the other order a failed reserve would
leave the child in both sets and `_detachChildren()` on the new parent would
never finish. `setParent()` turns `std::bad_alloc` into `MemoryError` after
the unlock, since the generated caller has no handler for a C++ exception.

Bit `TransactionPrepare`; cleared, the room is taken after the edge is
gone, and `proof-transaction-prepare` sees ownership moved although the
call raised.

## The call guard

Qt is not thread-safe per object: two threads calling into one `QObject` is
undefined, with a GIL as without one. The GIL used to serialize those calls as
a side effect. Nothing else does, so the binding takes a per-object guard for
the duration of the call - `sbkcallguard.h`, a `PyCriticalSection` over a
striped table of mutexes chosen by the C++ address.

It is taken for the **receiver only**. Arguments take a lease, which keeps
them alive across the call, but no guard: nesting critical sections does not
lock two objects, because the inner one suspends the outer, and an argument's
guard would silently drop the receiver's. Where a call genuinely touches two
objects at once, Qt's own rules apply as they always did.

`CallGuard` is the bit; cleared, a call runs with no guard on its receiver,
which the A/B in `run.py` measures. It is `0x4` of `PYSIDE6_OPTION_FT`.

## Call leases

The state lock protects the bookkeeping, not the C++ object a call is about to
dereference. That is what a lease does: it validates the wrapper and raises
the object's active-call count in one transaction, and the generated code
holds it for the duration of the call.

Destruction requested while a lease is open is marked and deferred rather than
waited for - waiting would deadlock whenever the in-flight call needs the
deleting thread. The last lease released runs the C++ destructor, with no lock
held. The mark covers the whole set the destructor takes with it, the object
and its children, so a child cannot be freed under a call in flight.

The mark is one-way. A wrapper whose C++ side is being destroyed is refused
for good, where a build with a GIL would let the call through into freed
memory.

### What a lease hands out

A lease copies the C++ pointer in the transaction that validates the
wrapper, and the holder uses that copy. Reading the wrapper's pointer array
again after the transaction would be a read with no lock, and
`Object::destroy()` may detach the array in between. Generated receivers,
copy and implicit converters, smart-pointer receivers, `VoidPtr` and
`pythonToCppPointer()` all take `lease.pointer()`.

A caller that asks for a particular base gets that base's pointer: the
multiple-inheritance slot is read in the transaction, the special cast is
applied to the copy afterwards. The slot index is computed before the lock,
because `getTypeIndexOnHierarchy()` calls `PyType_IsSubtype()` and the state
lock has to stay a leaf. The call guard stays keyed on the canonical
pointer, so two bases of one object share one guard.

The limit: a lease defers only the destruction the binding drives. A delete
issued by C++ reaches `Object::destroy(SbkObject *, void *)`, which does not
consult `activeCalls`. There the lease guarantees the pointer, not the
object - no holder reads the array while another thread detaches it, but
the object behind the copy may already be gone.

Bit `LeaseSnapshot`; cleared, holders read the array again, which
`proof-lease-snapshot` and `proof-leased-receiver` walk into.

### Which objects a lease accepts

The lease asks the instance whether it is a wrapper (`Object::checkType()`),
not whether its metatype is `SbkObjectType` itself. A class may bring its
own metaclass as long as it derives from ours - an abstract base class over
`QObject` does, `class Meta(type(QObject), ABCMeta)` - and an identity test
does not recognize such objects, so their calls would take no lease.

Bit `MetatypeSubclassLease`; cleared, the identity test is back and
`proof-metatype-subclass` finds such a call unleased.

### Leases taken inside a conversion

Generated code leases an argument that is a wrapper, but not the wrappers an
argument only carries: the elements of a `QList<QAction *>`, or a wrapper
passed as `void *`. Their converters lease each one and hand out a pointer,
so the lease ends inside the converter, and a concurrent `Shiboken.delete()`
frees the object before the native call reads it.

Such an argument now gets a `Shiboken::Object::ConversionLeases` holder next
to it: while it is converted the holder collects on its thread - each
converter's lease, plus a reference on the wrapper, since the container may
drop the element - and releases them after the native call has returned.
Collecting nests per thread: an iterator's `__next__` fills a holder of its
own, while every other lease it takes joins the outer one and waits for it.

Not covered: a pointer converted in an injected snippet, and a container of
pointers a Python override returns, which the native side keeps.

Bit `ConversionLeasesKept`; cleared, each lease ends with its converter,
and `proof-conversion-leases` sees the element freed mid-call.

## Locks that are deliberately separate

State that is built lazily, or that has its own lifetime, does not belong
under the state lock - building it calls into Python, which the contract
forbids. Four places have a lock of their own:

`Module::get()`, lazy type creation
: A type is incarnated on first attribute access, from whichever thread needs
  it first, and building it creates enum types through Python. A recursive
  lock, entered with the thread detached so a waiter holds nothing. The type
  is published to its struct early, as the re-entrancy guard for an
  initialization that nests on one thread, and a readiness flag says when it
  may be handed to anyone else.

`SignalManager::retrieveMetaObject()`, the dynamic meta object
: `QMetaObjectBuilder` is not thread-safe and its builder is shared per type.
  The update and the methods added by `addMetaMethod()` take one recursive
  lock, again entered detached. Building an instance's first builder does
  not: the parse runs application code, so the candidate is built with no
  lock held and published with `PyDict_SetDefaultRef()` - one atomic step
  that is the whole transaction, which is why no lock is taken around it.
  `PyObject_SetAttr()` may not be used there: it reaches `SelectFeatureSet()`,
  which compiles a class statement and clears a live type dictionary, so a
  finalizer defining a QObject subtype under a raw lock arrives back in
  `parsePythonType()` and trips the contract assertion. `__METAOBJECT__` is
  an internal key no feature set has anything to say about.

`dynamicslot.cpp`, the connection hash
: A plain mutex over a global container. Entries are taken out under it and
  the Qt disconnects run after it, because `QObject::disconnect` takes Qt's
  own signal-slot locks and can come back through a `destroyed()` delivery.

`BindingManager`, the wrapper map
: Its own recursive mutex, because C++ reaches the map without a thread state:
  `releaseWrapper()` runs from destructors, and a Qt thread deleting a wrapped
  object is enough.

Qt's own connect, disconnect and emit are thread-safe and are left to Qt.

Bit `LazyTypeLock`; cleared, lazy type creation runs unlocked, which the A/B
in `run.py` measures.

### The complete inventory

Every raw lock the binding owns, what it may do while held, and whether a
receiver guard can be active at the same time. Qt's and the application's
locks are not in here: they are not ours, and no order over them is claimed.

| Lock | Rank | Type | Taken in | May be held across | Guard active? |
|---|---|---|---|---|---|
| State | 8 | `std::mutex`, non-recursive | `sbkstatelock.cpp` | binding state only: validity, ownership, the parent and referred graph, `activeCalls` | yes, a lease takes the guard after the transaction |
| Wrapper map | 6 | `std::recursive_mutex` | `bindingmanager.cpp`, map operations throughout, a good half of them also in a build with a GIL | map operations; visitors and destructors run outside. Still inside: `PyType_IsSubtype()` in the type-narrowing lookup, an identity question that waits on the immutable hierarchy snapshots. `mi_init()` also runs there and is not an exception: it computes offsets from the C++ pointer and calls nothing | yes |
| Main-thread deletion | 7 | `std::mutex` | `bindingmanager.cpp`, 2 sites | one vector push or swap | no |
| Lazy type | 1 | `std::recursive_mutex`, waiter detaches | `sbkmodule.cpp` | type creation, which calls Python - the exception, owned by the lazy protocol | no |
| Class hierarchy | 2 | `std::mutex` | `bindingmanager.cpp`, 2 sites | taking or publishing the edge snapshot. A traversal walks its snapshot with the lock released, because it creates types and calls discovery functions | no |
| `ModuleData` static | 3 | C++ function-local static guard | `sbkmodule.cpp` | Python during first initialization - to be replaced by native-only storage | no |
| Connection hash | 5 | `std::mutex` | `dynamicslot.cpp`, 5 sites | container operations only: the key is built before the lock, and `QObject::disconnect()` runs after it | no |
| Meta-object builder | 4 | `std::recursive_mutex`, waiter detaches | `signalmanager.cpp` | `PyErr_WarnEx()`, reached from the method signature check - the parse and the publication are both outside now, and what is left is B15-3 | yes |
| Post-routine queue | 8 | `std::mutex` | `core_snippets.cpp`, 2 sites | container operations only: the reference is taken after the append, and the batch runs after the lock | no |
| QObject-pointer metatype | 8 | `std::mutex` | `pyside.cpp`, 1 site | `QMetaType::fromName()` and `QMetaType::id()`, Qt's registration; as a leaf, a lock of ours reached from there trips rather than deadlocks | no |

The `ModuleData` guard is the one row the tracking cannot see: a
compiler-generated guard has no acquisition site to wrap, so it is ranked
with the rest for the inventory's sake and `holdsLock()` always answers false
for it. Every other row is noted where it is acquired.

The rank is the order they may be taken in: a thread may only take a lock
that ranks above every one it already holds, so any two of them are always
taken the same way round and no pair of threads can hold them crosswise. The
leaves share the highest rank - nothing may be acquired while one is held,
which is what lets a transaction end without waiting for anything. They share
it rather than queue above one another on purpose: the check is a strict
"<", so equal ranks refuse to nest in either direction, while distinct ones
would quietly permit the lower leaf under the higher. The lazy-type lock
ranks lowest because it is the one that legitimately spans other work.

A rank is a claim, so it is checked and not merely written here:
`checkLockRank()` asserts it before every acquisition, and `lockNestings()`
reports which pairs a run actually produced. Measured over the whole pyside6
suite - 518 processes that used the bindings, the same numbers on two
machines - there are three:

| Nesting | Processes |
|---|---|
| `lazy type -> wrapper map` | 483 |
| `lazy type -> state` | 1 |
| `lazy type -> class hierarchy` | 518 |

All three have the lazy-type lock on the outside, which is why it ranks
lowest.
Note what such a measurement cannot see: a process that aborts never
reports, so a nesting that occurs only on a path which trips an assertion is
missing from the table and shows up in the assertion instead. That is how
`connection hash -> meta-object` was found, and it is gone now - the key is
built before the lock.

Two places take something the contract otherwise forbids, and both are
counted rather than asserted, so `Shiboken.contractExceptions()` reports how
often each was taken and neither can grow unnoticed.

The first is the lazy-type lock held where none may be: `Module::get()` holds
it across `PyObject_GetAttr()`, so a refcount can reach zero underneath and a
deferred C++ destructor can run inside it. That is the same finding as "the
lazy lock spans Python", seen from the destruction end, and it belongs to the
lazy protocol's replacement. `failpoints.py lazy-lock-spans-destruction`
holds it as a test that is expected to fail.

The second is `PyType_IsSubtype()` under the wrapper-map lock, in the three
lookups that narrow a pointer to a type - `acquireWrapper()` in the
free-threaded build, `findByType()` in both. It reads Python-owned type
state, which is the same class of thing as the locked paths FT8 took out of
the state lock (B9-1), and it waits on the immutable hierarchy snapshots for
the same reason. Unlike the first it is not rare: a suite run takes it about
3600 times across 218 of those 518 processes, because it sits in every
wrapper lookup that has to narrow by type. Only that case is counted: a
lookup whose candidate is already the exact type asks nothing of the
hierarchy. It used to be about 6400, and the difference is the virtual-call
preflight, which asked the typed question before it attached and now asks
the untyped one.

Debug builds track which of these the current thread holds
(`sbkheldlocks.h`). `SBK_ASSERT_NO_RAW_LOCK()` states the other end of the
contract at a place that runs Python, a decref, a destructor or an unbounded
wait; `SBK_ASSERT_LOCK_NOT_HELD(State)` sits on the CPython type helpers, so
a path that reaches `PyType_IsSubtype()` from a transaction aborts instead of
being found again by the next review; `SBK_ASSERT_STATE_LOCKED()` says the
other half in every `...Locked()` helper. In a release build the tracking
compiles away completely, as the state lock's own flag always did.

Every acquisition of a lock in the table above notes itself - through
`TrackedGuard`, or by hand in the three places that cannot use it because
they detach while waiting or switch the mutex off for an A/B run
(`sbkstatelock.cpp`, `sbkmodule.cpp`, `signalmanager.cpp`). The one row that
is not covered is the `ModuleData` guard above, which has no acquisition site
to wrap. It is not a claim about every mutex in the sources: the failpoint
machinery in `sbkfailpoint.cpp` has one of its own, which is deliberately
untracked and deliberately spans a timed wait. It is test scaffolding, exists
only in a debug build, protects no binding state, and a thread that parks
under it holds nothing else - the failpoint asserts that before it waits.

The written form of the same rule is checked without running anything:
`sources/shiboken6/libshiboken/check_state_lock_scope.py` reads the direct
body of every locked region - a `StateLockGuard` scope and every `...Locked()`
function - and refuses any CPython call in it. Its allowlist is short and each
entry carries its reason; a pinning increment is in it because an increment
cannot run a destructor, block, or need a safe point, and `Py_DECREF` is
deliberately not. It follows calls as well as reading the direct body, so a
helper that calls a helper that reaches `PyObject_GetAttr()` is reported with
the path that leads to it. What it cannot see is a call through a function
pointer or a virtual - `cpp_dtor`, `mi_init` and the type-discovery hooks are
exactly that - and anything outside the files it is given. `ctest -R
state_lock_scope` runs it.

## What this does not give you

Qt itself does not become thread-safe. The call guard serializes two threads
that reach the *same* object through the binding - it restores what the GIL
did by accident, no more. It does not make an object usable from two threads:
Qt's thread affinity rules and the per-class thread-safety documentation
continue to apply unchanged. A QWidget still belongs to the GUI thread, and a
QObject touched from the wrong thread is still undefined, guard or no guard.

The intended shape of a free-threaded application is therefore the same one
that worked before: keep the GUI on one thread, do the parallel work in
threads that do not touch Qt objects, and hand results over at a controlled
point.

Some of what the bindings hold is a `QPointer` that Qt clears from the thread
the object dies on. No binding lock covers that write, and none ever did.

## Declaring modules GIL-free

A module tells the interpreter whether it needs the GIL. One module that says
it does switches the GIL back on for the whole process, silently undoing free
threading for every other module.

Shiboken defaults to declaring that the GIL *is* needed. A binding that has
been reviewed for free-threaded execution opts out in its type system:

```xml
<typesystem package="Mybinding" module-uses-gil="false">
```

The PySide modules do this; a binding generated with shiboken does not inherit
the claim.

## Switching the locks off

`PYSIDE6_OPTION_FT` is a bit per measure, and clearing one puts back what was
there before it. Each bit is documented where its measure is; this section
claims no bit of its own and is only the manual for the switch.

```
PYSIDE6_OPTION_FT             unset, and that is the only supported setting:
                              it means every bit there is, including the ones
                              added after whatever is reading this
PYSIDE6_OPTION_FT="~0x1000"   all of them except ConstructorClaim
PYSIDE6_OPTION_FT=0b011       the two locks only
PYSIDE6_OPTION_FT=off         without any of them
```

A leading `~` means "all of them except these", so a counter-proof names
only the measure it takes away. The quotes are for zsh, which rejects a bare
`~0x1000` as a user name.

The inventory lives in `sbkftoptions.h` and nowhere else - a copy of it goes
stale, and a stale copy is invisible in a result, because the run simply
describes different code than the one it names. `ftoptions.py` in the test
directory reads the enum out of the header at runtime for the same reason.

This exists for stress testing and is not a supported production setting: the
modules still declare that they do not need the GIL while the synchronization
backing that declaration is gone. Taking the declaration back at runtime is
not possible, because the GIL slot is evaluated when the module object is
created, before any binding code runs, so clearing `StateLock` warns instead.

How each measure is demonstrated is not uniform, and saying so is part of the
claim:

  - Most of them have a `proof-*` in `failpoints.py`: the subject runs in a
    child process with the bit cleared and has to fail there.
  - The three locks - `LazyTypeLock`, `StateLock`, `CallGuard` - have their
    A/B in `run.py`'s scenario table instead, one lock switched off per
    column, five rounds each. Their subjects are stress scenarios, not
    deterministic ones.
  - `MiOffsetsOnce` has a sanitizer A/B and can have nothing else;
    [its section](freethreading-types.md#mi-offsets-have-one-owner)
    says why.
  - `MetaObjectParseOutsideLock` has both: a `proof-*` for the race the
    split opens, and a `run.py` scenario for the contract assertion the
    cleared bit trips. That scenario needs a build with the assertions in
    it, and `run.py` skips it where they are absent rather than reading
    the silence as a result.
  - `PostRoutineBatch` has two `run.py` scenarios and no `proof-*`:
    `post_routine_batch` for the live-queue walk, `post_routine_raises` for
    the pending exception, which CPython's own assertion reports. Both need
    the assertions compiled in, and `run.py` skips them otherwise.

A mechanism that no scenario can take away does not get a bit. The readiness
flag on lazily created types is one such, and so is `Shiboken::CacheSlot`:
they are covered by the suites, not by the A/B harness.

`check_bit_coverage.py` in the failpoint test directory checks the list above
against the tree: a bit with neither a `proof-*` nor an exemption fails it.

## Testing

Free-threading specific tests skip themselves unless the GIL is actually
disabled. Two are worth knowing about:

`sources/shiboken6/tests/samplebinding/free_threading_stress_test.py`
: hammers wrapper deletion and the parent graph from several threads.

`sources/pyside6/tests/pysidetest/signal_slot_lock_inversion_test.py`
: drives the classic AB-BA shape: a thread holding a Python lock enters a
  wrapper while another enters through `setParent()` and delivers a child
  event to a Python override that wants the same lock. It runs in a
  subprocess with a hard timeout, so a regression fails the test instead of
  hanging the suite.

Deadlock tests belong in subprocesses for that reason. Passing race stress
tests shows protection against the races they exercise; it does not show
deadlock freedom, which needs targeted tests and an argument about lock scope.

A passing test also only shows one half of the argument: that the code
survives, not that the synchronization is what makes it survive. The other
half needs the locks switched off, which produces crashing processes and
therefore cannot be part of the automatic suite. It lives in
`sources/pyside6/tests/manually/freethreading/run.py`, which runs each
scenario twice, with and without the lock it depends on, and only calls a
scenario a proof when it fails without it.

Run it with the free-threaded interpreter; `REPEATS`, `STRESS_THREADS` and
`STRESS_ITERS` size the run, and naming scenarios restricts it. Never run a
single scenario alone to judge a lock: rare races show up only over the whole
set, and a scenario on its own can stay clean hundreds of times.

### Deterministic races: failpoints

Repetition is a poor way to reach a window of a few instructions. A failpoint
is a named place where a test stops one thread, so the second arrives in the
order the test wants, every time - a test that fails on an unfixed revision
rather than in one run out of fourteen. They sit either side of the windows
that matter: before the C++ destructor runs, once it is past and the
tombstone still stands, between the check and the write in `setCppPointer()`,
before `setParent()` publishes an edge. `Shiboken.failpointNames()` lists
what a build has; a release build has none and the tests skip.

Two properties make them usable rather than merely present. A parked thread
waits **detached**, so it blocks neither stop-the-world nor, on a build
running with the GIL, everyone else. And an armed point stops exactly one
thread: the arming goes with the first one through, so a test can park a call
and then drive the same code path from another thread to reach the object the
parked one holds.

The registry and the call sites are held together by
`libshiboken/check_failpoint_names.py`, which ctest runs. A name a test arms
but no `SBK_FAILPOINT()` carries lets that test run into its timeout; a name
in the code but not in `KnownFailpoints` cannot be armed at all, and the test
that wants it reports a skip - which is green.

### A failpoint that throws

`SBK_FAILPOINT_THROW()` stands where a transaction allocates under the state
lock - `deferred-slot-alloc`, for one - and, once armed, throws
`std::bad_alloc` a single time, so a test can see what a failed transaction
leaves behind. It cannot park, because the thread holds the lock. The two
kinds are armed separately and have separate inventories, `KnownFailpoints`
and `KnownThrowFailpoints`, which the name check keeps apart.

### The failpoint matrix

`failpoints.py` holds the tests. They are not run directly for evidence,
because a test that only ever ran free-threaded shows that the code works
there, not that the synchronization is what makes it work.
`failpoint_matrix.py` next to it runs each one in its own subprocess, with a
hard timeout and its own process group, on every interpreter the argument
needs:

| Row | Interpreter |
|---|---|
| `classic` | traditional CPython, its own debug build |
| `ft-gil-on` | free-threaded binary, `PYTHON_GIL=1` |
| `ft-gil-off` | the same binary, `PYTHON_GIL=0` |

Each child verifies the GIL state it was asked for **after** importing
PySide, because that import is what can turn the GIL back on. A build
directory names the Python version but not whether that Python was
free-threaded, so each row names its interpreter and its build and the two
are checked against each other through the extension suffix. A row without a
build is reported as missing and the run ends as partial, never as green.
`FT_PYTHON` and `FT_BUILD_DIR` name the free-threaded row and default to the
interpreter running the script; `GIL_PYTHON` and `GIL_BUILD_DIR` name the
traditional one and have no default.

A test may declare that its expected outcome is not "ok":
`lazy-lock-spans-destruction` is listed as failing while B13-5 is open, and
the runner can treat a deliberate deadlock's timeout as the pass. The day the
cell changes, the entry comes out.

