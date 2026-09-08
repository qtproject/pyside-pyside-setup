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

## Where the `Bn-m` and `FTn` names come from

A few passages here, and a few comments in the sources, name a finding as
`B9-1` or a work package as `FT8`. They come from an external free-threading
review of this branch: `Bn-m` is finding *m* of its review step *n*, `FTn` is
the work package those findings were grouped into, and an `FT8 invariant`,
`design` or `validation row` is a numbered item inside that package's
handoff. The names this change uses:

| Name | What it is |
|---|---|
| B9-1 | Python type and MRO access under the state mutex |
| B13-5 | the lazy-type lock spanning type creation and import work |
| FT8 | restoring the short raw-lock contract - this series |

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

An earlier design took one coarse lock at the entry of every generated wrapper
and held it until the wrapper returned. That put arbitrary Python, Qt and
third-party code underneath it and made the lock part of the lock order of the
whole process. It is gone: no lock over the *bookkeeping* is held across code
the binding does not control.

One lock still spans a call, and deliberately so - the per-object call guard
below. It is a `PyCriticalSection`, so a thread that has to wait underneath it
detaches and the guard is suspended; that is what keeps it out of the lock
order the coarse lock joined.

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

The guard is bit `0x4` of `PYSIDE6_OPTION_FT`.

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
  Both the update and the methods added by `addMetaMethod()` take one
  recursive lock, again entered detached.

`dynamicslot.cpp`, the connection hash
: A plain mutex over a global container. Entries are taken out under it and
  the Qt disconnects run after it, because `QObject::disconnect` takes Qt's
  own signal-slot locks and can come back through a `destroyed()` delivery.

`BindingManager`, the wrapper map
: Its own recursive mutex, because C++ reaches the map without a thread state:
  `releaseWrapper()` runs from destructors, and a Qt thread deleting a wrapped
  object is enough.

Qt's own connect, disconnect and emit are thread-safe and are left to Qt.

### The complete inventory

Every raw lock the binding owns, what it may do while held, and whether a
receiver guard can be active at the same time. Qt's and the application's
locks are not in here: they are not ours, and no order over them is claimed.

| Lock | Rank | Type | Taken in | May be held across | Guard active? |
|---|---|---|---|---|---|
| State | 7 | `std::mutex`, non-recursive | `sbkstatelock.cpp` | binding state only: validity, ownership, the parent and referred graph, `activeCalls` | yes, a lease takes the guard after the transaction |
| Wrapper map | 5 | `std::recursive_mutex` | `bindingmanager.cpp`, 16 sites in the file, 11 of them in a free-threaded build | map operations; visitors and destructors run outside. Still inside: `PyType_IsSubtype()` in the type-narrowing lookup, an identity question that waits on the immutable class hierarchy. `mi_init()` also runs there and is not an exception: it computes offsets from the C++ pointer and calls nothing | yes |
| Main-thread deletion | 6 | `std::mutex` | `bindingmanager.cpp`, 2 sites | one vector push or swap | no |
| Lazy type | 1 | `std::recursive_mutex`, waiter detaches | `sbkmodule.cpp` | type creation, which calls Python - the exception, owned by the lazy protocol | no |
| `ModuleData` static | 2 | C++ function-local static guard | `sbkmodule.cpp` | Python during first initialization - to be replaced by native-only storage | no |
| Connection hash | 4 | `std::mutex` | `dynamicslot.cpp`, 5 sites | container operations only: the key is built before the lock, and `QObject::disconnect()` runs after it | no |
| Meta-object builder | 3 | `std::recursive_mutex`, waiter detaches | `signalmanager.cpp` | builder construction, which reaches Python - to be narrowed to a generation commit | yes |

The `ModuleData` guard is the one row the tracking cannot see: a
compiler-generated guard has no acquisition site to wrap, so it is ranked
with the rest for the inventory's sake and `holdsLock()` always answers false
for it. Every other row is noted where it is acquired.

The rank is the order they may be taken in: a thread may only take a lock
that ranks above every one it already holds, so any two of them are always
taken the same way round and no pair of threads can hold them crosswise. The
state lock ranks highest because it is the leaf - nothing may be acquired
while it is held, which is what lets a transaction end without waiting for
anything. The lazy-type lock ranks lowest because it is the one that
legitimately spans other work.

A rank is a claim, so it is checked and not merely written here:
`checkLockRank()` asserts it before every acquisition, and `lockNestings()`
reports which pairs a run actually produced. Measured over the whole pyside6
suite - 484 processes that used the bindings - there are two:

| Nesting | Processes |
|---|---|
| `lazy type -> wrapper map` | 483 |
| `lazy type -> state` | 1 |

Both have the lazy-type lock on the outside, which is why it ranks lowest.
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
lazy protocol's replacement.

The second is `PyType_IsSubtype()` under the wrapper-map lock, in the three
lookups that narrow a pointer to a type - `acquireWrapper()` in the
free-threaded build, `findByType()` in both. It reads Python-owned type
state, which is the same class of thing as the locked paths this change
took out of the state lock (B9-1), and it waits on the immutable class
hierarchy for the same reason. Unlike the first it is not
rare: a suite run takes it a few hundred thousand times, in almost every
process, because it sits in the lookup every wrapper conversion makes.

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
to wrap.

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

### Function-local statics whose initializer calls Python

A C++ function-local static has a compiler-generated guard, and a second
thread blocks in it while the first initializes. Where that initialization
calls Python, the guard is a raw lock across Python by another name. The
audit found these classes:

- **Interned strings**, the large majority. Counted rather than estimated,
  with the commands that produce the number, because the previous figure in
  this file was neither: `grep -rn "static .*createStaticString" sources/
  --include=*.cpp --include=*.h` gives 46 lines, one of them commented out,
  so 45 function-local statics; `grep -rn "STATIC_STRING_IMPL("` gives 74
  uses on top of that, in `sbkstaticstrings.cpp` and
  `pysidestaticstrings.cpp`. One more interns without the helper
  (`pysideproperty.cpp`, `getDataFromKwArgs()`), so "all of them go through
  `createStaticString()`" is not true. Each interns one string once.
  Bounded, no user code, no callback; kept.
- **Type objects**, `createVoidPtrType()`, `createSignalType()`,
  `createMetaSignalType()`, `createSignalInstanceType()`. These build types
  through Python while holding the guard. Each is reached from its module's
  own init function - `VoidPtr::init()` and `Signal::init()` call the
  accessors themselves - so the guard is taken and released during module
  initialization, before another thread can call in.
- **Converter and type lookups**, `getConverter()`,
  `getPythonTypeObject("QQmlEngine*")` in `pysideqmlregistertype.cpp`. Table
  lookups, no Python execution.
- **`PyTuple_New(0)`** in `pysidesignal.cpp`, one allocation.

None of them is reached with another binding lock held, which is what makes
them acceptable rather than the absence of a callback today. A new
Python-calling static needs the same check.

### The guard's reach in generated code

Checked against the generated wrappers rather than the templates, because
that is where a missing lease would sit. Over all 1872 of them:

| Entry kind | with `cppSelf` | without a lease |
|---|---|---|
| methods | 36673 | 0 |
| rich comparison | 287 | 0 |
| number, sequence and mapping slots | 539 | 0 |
| property getters and setters | 574 | 0 |
| entries with an `allow-thread` detach | 249 | 0 |

The table counts generated entry points, and that is also its limit. It is
not a statement about every way a C++ pointer is dereferenced: hand-written
snippets are outside it, and so is the buffer protocol -
`qbytearray-bufferprotocol` in `qtcore.cpp` reads `cppSelf` with no lease and
hands out a pointer into the object's memory. That is older than any of this
and belongs to the lease work; it is named here so the table is not read as a
completeness argument it does not make.

`CallLease{self}` takes the guard, arguments are constructed with
`Guard::Omit`. That is deliberate: a contended inner guard would run the
native call with the receiver's own guard suspended, so two nested guards are
never a two-object transaction. Where the generator emits
`Py_BEGIN_ALLOW_THREADS` or `ThreadStateSaver`, the lease is always
constructed before the detach region and outlives it - the guard is suspended
there, the lease is not.

### What the lock contract does not promise

No general freedom from deadlock. The contract covers the locks listed above:
none of them is held across Python, Qt, a decref, a destructor or an
unbounded wait, except where this document names the exception. It says
nothing about locks the application or a third-party library holds while
calling in, and nothing about Qt's own locks. A native lock taken in the
opposite order to a binding lock can still deadlock - that was true with the
GIL and stays true.

Nor is the type hierarchy promised to hold still. CPython accepts
`__bases__` assignment on wrapper types, and even across layouts - a QObject
subclass can be given a QTimer subclass as its base while instances of it
exist. What keeps destruction correct is the shape of the transaction rather
than any refusal by CPython: the destructor list is taken once, before the
state lock, and the locked part only zips it with `cptr`. An immutable
per-type list published when the type is readied would make this an
invariant instead of a property of the code as written; that belongs with
the identity and hierarchy snapshots.

Nor is QML construction promised to survive every nesting. QML allocates
the memory for a registered type and the generated constructor places the
object into it; a second QObject built inside `__init__` before that happens
would take the address instead, so only the type QML asked for may consume
it. A second object of the *same* type built there still passes that test
and still takes the address. Telling those apart needs the address to travel
with the object being constructed rather than with the thread, which belongs
to the wrapper-identity work.

`abi3t` is not supported, and behaviour after `fork()` is undefined for a
process that has used the bindings; use `spawn`, or `fork` followed by
`exec`.

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

`PYSIDE6_OPTION_FT` is a bit per lock, and clearing one takes that lock away:

```
PYSIDE6_OPTION_FT=0b111   all of them (the default, and what an unset
                          variable means)
PYSIDE6_OPTION_FT=0b101   without the state lock
PYSIDE6_OPTION_FT=0b011   without the per-object call guard
PYSIDE6_OPTION_FT=off     without any of them
```

`LazyTypeLock` is `0x1`, `StateLock` is `0x2`, `CallGuard` is `0x4`. This
exists for stress testing
and is not a supported production setting: the modules still declare that they
do not need the GIL while the synchronization backing that declaration is
gone. Taking the declaration back at runtime is not possible, because the GIL
slot is evaluated when the module object is created, before any binding code
runs, so clearing `StateLock` warns instead.

A mechanism that no scenario can take away does not get a bit. The readiness
flag on lazily created types is one such: it is covered by the suites, not by
the A/B harness.

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
scenario a proof when it crashes without it. Six of the eight are proofs at
the moment; `signal_race` became one when the coarse lock went, because the
signal machinery reaches the wrapper lookups, the parent/child graph and
destruction, and the coarse lock had been covering that.

Run it with the free-threaded interpreter; `REPEATS`, `STRESS_THREADS` and
`STRESS_ITERS` size the run, and naming scenarios restricts it. Never run a
single scenario alone to judge a lock: rare races show up only over the whole
set, and a scenario on its own can stay clean hundreds of times.

