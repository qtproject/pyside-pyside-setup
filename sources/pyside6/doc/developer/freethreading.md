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

The bit is `LeaseSnapshot`; cleared, holders read the array again.

### Which objects a lease accepts

The lease asks the instance whether it is a wrapper (`Object::checkType()`),
not whether its metatype is `SbkObjectType` itself. A class may bring its
own metaclass as long as it derives from ours - an abstract base class over
`QObject` does, `class Meta(type(QObject), ABCMeta)` - and an identity test
does not recognize such objects, so their calls would take no lease.

The bit is `MetatypeSubclassLease`; cleared, the identity test is back.

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

The bit is `ConversionLeasesKept`; cleared, each lease ends with its
converter, and `container-element-lease` sees its element freed mid-call.

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
  `PyObject_SetAttr()` could not stay there: it reaches `SelectFeatureSet()`,
  which compiles a class statement and clears a live type dictionary, and a
  finalizer running under a raw lock that defines a QObject subtype arrives
  back in `parsePythonType()` and trips the contract assertion.
  `__METAOBJECT__` is an internal key no feature set has anything to say
  about, so the attribute machinery was a detour - the lookup beside it read
  the dictionary directly all along.

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
| State | 8 | `std::mutex`, non-recursive | `sbkstatelock.cpp` | binding state only: validity, ownership, the parent and referred graph, `activeCalls` | yes, a lease takes the guard after the transaction |
| Wrapper map | 6 | `std::recursive_mutex` | `bindingmanager.cpp`, 18 sites in the file, 11 of them also in a build with a GIL | map operations; visitors and destructors run outside. Still inside: `PyType_IsSubtype()` in the type-narrowing lookup, an identity question that waits on the immutable hierarchy snapshots. `mi_init()` also runs there and is not an exception: it computes offsets from the C++ pointer and calls nothing | yes |
| Main-thread deletion | 7 | `std::mutex` | `bindingmanager.cpp`, 2 sites | one vector push or swap | no |
| Lazy type | 1 | `std::recursive_mutex`, waiter detaches | `sbkmodule.cpp` | type creation, which calls Python - the exception, owned by the lazy protocol | no |
| Class hierarchy | 2 | `std::mutex` | `bindingmanager.cpp`, 2 sites | taking or publishing the edge snapshot. A traversal walks its snapshot with the lock released, because it creates types and calls discovery functions | no |
| `ModuleData` static | 3 | C++ function-local static guard | `sbkmodule.cpp` | Python during first initialization - to be replaced by native-only storage | no |
| Connection hash | 5 | `std::mutex` | `dynamicslot.cpp`, 5 sites | container operations only: the key is built before the lock, and `QObject::disconnect()` runs after it | no |
| Meta-object builder | 4 | `std::recursive_mutex`, waiter detaches | `signalmanager.cpp` | `PyErr_WarnEx()`, reached from the method signature check - the parse and the publication are both outside now, and what is left is B15-3 | yes |

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

### The preflight in front of a virtual call

A virtual reaching Python starts with one question: is this C++ address
wrapped at all? It has to be answerable from a thread that has no Python
thread state, because that is what a Qt worker thread entering a virtual
looks like, and it has to stay cheap for the common case of a C++ object
Python never saw.

It used to narrow by type at the same time, and narrowing by type reads
`Py_TYPE` and walks `tp_mro` - Python-owned state, read with no thread state
to read it under (B4-2). The untyped overload is an address comparison and
needs none, so that is what runs first; narrowing happens after the attach,
in `acquireWrapper()`. Both typed lookups now assert that the thread is
attached, so the next caller that gets this wrong aborts in a debug build
instead of being found by the next review.

`NativePreflight` is the bit, and `proof-native-preflight` discriminates
through that assertion - which means it says nothing in a release build,
where the unsafe read would simply happen. The measure is real either way;
what is debug-only is the ability to show it.

### A retired identity leaves a tombstone

The wrapper map answers "which Python object stands for this C++ address".
Removing an entry when a wrapper dies is not enough to keep that answer
right: the destructor has not run yet, and a lookup in between sees an empty
map, decides the address is free, and publishes a second wrapper for an
object that is about to be destroyed (B4-1). That wrapper is marked valid
and its pointer goes stale a moment later.

An entry therefore does not leave the map when the wrapper dies. It is
marked dying and stays until the destruction that retires it can no longer
reach the address - past the C++ destructor for an owning wrapper, past the
deallocation for a non-owning one. Until then the entry carries a reference
to the type it was registered for, so a lookup can tell whether a dying
identity is the one it is asking about without touching a wrapper that may
already be freed. The reference is taken under the map lock, which an
increment may span, and dropped when the tombstone falls, which a decref
may not span.

The wrapper the entry points at is *not* readable any more, and that is the
whole point of the type reference. `acquire()` is the only place that may
turn the map's borrowed pointer into a reference, and it asks
`PyUnstable_TryIncRef()` - which reads the object. On a tombstone that is
freed memory, and where the allocator had already recycled the block the
increment succeeded and handed out a stranger. The guard belongs in
`acquire()` and nowhere else: two of the five readers carried their own and
three did not.

A conversion that meets a tombstone gets a wrapper with no C++ pointer and
no validity, so every use of it raises rather than reading freed memory -
unless the dying type invalidates such wrappers itself.

That exception is `destroyed(QObject *)`, and it is not a convenience. Qt
emits the signal from `~QObject`, the argument is meant to be used there, and
PySide invalidates whatever wrapper the conversion produced right after the
signal. A tombstone that refused the conversion would hand the handler an
argument it cannot touch, which `signals/signal2signal_connect_test`
measures. A plain C++ class has no such mechanism - `QRecursiveMutex`, the
type this whole finding was made on, would keep the stray wrapper valid
forever - so it keeps the tombstone.

libshiboken does not know what a QObject is. PySide installs a predicate
(`setDyingConversionPredicate`) when QtCore is initialized, and the map asks
it about the *dying* type, not about the one being looked up: what decides is
whether the destruction that is running will invalidate what the conversion
hands out. `PYSIDE6_OPTION_FT` with `Tombstones` cleared removes the entry
the way it was removed before, which is what `failpoints.py
proof-tombstones` requires in order to see the window return.

The exception is a measure like any other and carries its own bit,
`DyingConversionException`. Cleared, the tombstone refuses every dying
identity, and `dying-qobject-argument` fails in its first half: the handler
is handed an argument it cannot use. That is `proof-dying-qobject`.

The question is asked per type, not per moment, so for a QObject the whole
destruction is open, not just the stretch around the `destroyed()` emit. What
closes that is not a narrower question - the moment PySide's invalidation runs
is not something the binding is told - but the other end of the same
transaction: **a wrapper the exception lets through belongs to the tombstone
that let it through.** It is not entered in the map, so no later lookup can
find it and no invalidation path outside libshiboken can be expected to reach
it; the tombstone holds a reference to it, and invalidates it when it falls.
Usable exactly as long as the destruction it was made for is running.

That the map does not carry it is the load-bearing half. An entry would
outlive the tombstone and become the canonical wrapper for whatever the
allocator puts at that address next - the third and worst of the three
damages, after "says valid over freed memory" and "says valid over a
stranger". Two conversions inside one window still get the same wrapper: the
tombstone is asked first, and hands its stray back the way the map would
have.

Which means the tombstone has to fall while anything can still observe it.
It does: the deallocator retires it after the C++ destructor, and a deferred
destruction retires it from the same queue. Both go through
`retireWrapper()`, which takes the strays out under the map lock and
invalidates them outside it - invalidation walks the object graph and takes
the state lock, which the map lock may not span.

What is left when `~BindingManager` runs is abandoned, tombstones included.
Static destruction runs on whichever thread unloads the image, possibly
after finalization has begun, so it must not run Python. Nothing is lost:
`Object::destroy()` only detaches a wrapper from its C++ object and never
runs the destructor.

The bit is `DyingStrays`; cleared, such a wrapper is registered like any
other, and `stray-outlives-tombstone` sees it still valid after the
destruction is past. That is `proof-dying-strays`.

Which paths lay one down is part of the claim, and it is not all of them.
The deallocator does, and so does `Shiboken.delete()`, because both run the
C++ destructor themselves and know when it is past; a destruction handed to
the main thread carries its tombstone in the same queue, so it falls after
the destructor rather than after the hand-off. That ordering is not
cosmetic: the retirement used to be posted behind `deallocData()`, which
runs Python, and the main thread could drain the queue in that window - the
tombstone then stayed for good, and the address with it.

`Object::destroy()` is the hard one and it does too, differently. It is
called *from* the C++ destructor of a wrapper the C++ side owns, so the
binding hears a destruction begin and is never called again to say it is
over - there is no moment to take the tombstone away at. Removing the entry
there, which is what used to happen, leaves true absence for every base
destructor still to come.

So the tombstone is laid anyway, and what retirement needs is kept with it:
the pointer array, which the object no longer carries, and a reference on the
type. It then waits for one of the two moments that do come back:

  * **the generated wrapper's `operator delete`.** That is the point the
    language guarantees after the last destructor - the memory is going back
    - and because the wrapper's destructor is virtual it is found through the
    vtable even when foreign code deletes through a base pointer. This is the
    ordinary ending.
  * **a construction publishing at the same address.** `registerWrapper()`,
    the constructor path, and only that one: the allocator cannot hand an
    address out again before the previous destruction is over, so a *newly
    built* object there is proof. It exists for the case the first ending
    misses - a placement-constructed object, destroyed by an explicit
    destructor call with no `operator delete` to follow.

A conversion is deliberately not such a proof and does not come through
`registerWrapper()`: meeting a tombstone is what a conversion has to be
refused for. The bit is `ExternalTombstones`; cleared, the entry is removed
the way it always was, and `external-destruction` sees a valid wrapper
published over an object C++ is taking apart.

What a destruction takes with it is covered too. `invalidate()` releases the
owned children plainly and the parent's destructor - one line later - is what
deletes them, so each child had the same window its parent no longer has. The
owned set is collected before the children are released, every child in it
gets its own tombstone, and they are retired with the parent's, after the
destructor. Children that carry a C++ wrapper are not in that set on purpose:
nothing releases their entry here - their own C++ destructor calls
`Object::destroy()`, and that keeps the window `Object::destroy()` has and
cannot close, which the paragraph above declares.
`delete-before-owned-dtor` is the failpoint in that window and
`replacement-of-owned-child` the test that walks into it.

Both destruction paths do it, and that took a second pass to get right: the
deallocator carries its own copy of this sequence, and the first version of
the child tombstones was only in `finishDestruction()`, so dropping the last
reference to a parent still handed the children back blank. The deallocator
also decides differently now: it works out whether it is going to destroy
anything *before* it touches the map, because a tombstone stands for a
destruction that is going to happen. A wrapper that owns nothing destroys
nothing, and its entry is removed the way it always was.
`replacement-of-child-in-dealloc` is that half.

Two failpoints stand either side of the deallocator's window, because one is
not enough: `dealloc-before-destroy` is before the wrapper is taken apart,
`dealloc-before-cpp-dtor` after it and before the destructor. Only the second
one sees the window this section is about - the first is inside a stretch
where removing the entry early already held.

### Claiming a native slot is one transaction

A generated constructor writes the C++ pointer into the slot of the wrapper
it belongs to. Reading the slot and writing it used to be two steps, and a
Python subclass can put `self` where another thread finds it before it calls
the base initializer - both threads then saw an empty slot, both constructed
a C++ object, and both reported success (B5-3). One of the two objects was
left with nobody to delete it, and validity, ownership and registry identity
described whichever write landed last.

The claim happens in one state-lock transaction now, so exactly one thread
takes the slot and the other is told that the object is already initialized -
the error that already existed for a second `__init__` from one thread. The
loser destroys the candidate it built and nothing else. Raising happens
after the transaction, because it is a Python call-out.

One transaction is still only the second half. The slot was claimed *after*
the C++ constructor, so the thread that loses has built its object anyway -
and, for a QObject, hung it in Qt's tree - before it hears that it lost. The
generated constructor now reserves the slot before it builds anything:
`Shiboken::Object::ConstructionGuard` takes it, `claimed()` says whether this
thread has it, and the destructor gives it back, which is what makes it
usable in code that bails out of a dozen places.

The slot in `cptr` stays null while it is reserved. A sentinel value there
would have to mean something to the forty-odd places that read `cptr` - one
of them compares two objects through `cptr[0]`, where two objects under
construction would be the same object. The reservation is a bit beside it,
in `SbkObjectPrivate::constructingSlots`, and only the construction path asks
about it.

What the constructor then publishes used to be four calls - claim the slot,
mark valid, mark wrapper, register - and every other thread could meet the
object between two of them. `Shiboken::Object::commitConstruction()` does
the three that matter in the one order the lock contract allows: the state
lock is the leaf, so the map may not be taken while it is held, which puts
the registration first. What is visible in between is an object that is
registered and not yet valid, on which a call refuses - the safe half, and
the one the "`__init__` not called" error already covers. The reverse order
would leave a valid object that is not in the map, and a conversion of the
same pointer would publish a second wrapper for it. The generator emits that
one call, so `setCppPointer()` and `registerWrapper()` no longer appear in
generated code.

`ConstructorClaim` is the bit. Cleared, the slot is claimed after the
constructor as it was, and `constructor-claim` sees two C++ objects built for
one wrapper: it parks the first thread where it is about to publish and
counts the parent's children while it is there. That is
`proof-constructor-claim`.

### Destruction claims follow the parent graph

`Shiboken.delete()` claims the object it names and everything its C++
destructor takes along, and a claimed object gets no new lease. The claim is
recorded on the named object only. Every other member derives it from the
parent chain it hangs in when asked:

    claimed(x) = x->d->directDestruction || claimed(parent(x))

That lets a waiting claim follow the graph. A child that moves out of a
claimed parent is free again once the edge is gone (B6-1), one that moves in
is claimed once the edge is published (B6-2), and both happen in the
transaction that changes the edge. When the destruction is extracted, the
claim is stamped onto every member of the set as it stands then, because
invalidation hands the children back and their edges no longer say it.

A process-wide count of waiting claims is read without the lock. While it is
zero, an object's own flag is the whole answer and no chain is walked. That
is only correct because every stamp is transitive: except for the claim on
a waiting root, whatever sets `directDestruction` on a node sets it on the
whole owned set below it, since the count drops to zero exactly when those
C++ instances are about to go.

Generated code cannot add a member behind the stamp: `setParent()` is
emitted while the receiver and argument leases are held, and the claim
refuses them. Hand-written glue that sets a parent without a lease, such as
the layout ownership in `qtwidgets.cpp`, can still publish an edge there.

Bit `ClaimByAncestry`; cleared, the request marks the whole owned set once:
a child that moved out stays refused, one that moved in is admitted. B6-2
has no failpoint test yet; the test README says what the harness lacks.

### A teardown keeps the claim

A child detached *because* its parent is torn down is not reparented: the
parent's C++ destructor is about to take it along. If the claim went with the
edge, a child that keeps `validCppObject`, as a wrapper subclass does, would
be callable over memory that destructor frees. `invalidate()` is where it
shows, because the lease release then finds the root invalid, skips the
extraction, and the stamp never runs.

The two sites that detach for a teardown, `_detachChildren()` and
`collectInvalidateLocked()`, therefore stamp the claim the child derives onto
its owned set while the edge still exists. `removeParentLocked()` does not:
`giveOwnershipBack` is false in the first site but true in the second and in
a reparent, so it cannot tell them apart. That also keeps B6-1 safe, since a
reparent has no way to keep the claim.

Bit `ClaimThroughTeardown`; cleared, the claim goes with the edge.

### The deallocator claims the owned set

Dropping the last reference to a Python-owned parent runs its C++ destructor
from the deallocator, children and all. The binding performs that destruction
but never asked about leases, so a call in flight on a child lost its object.

In one transaction before `deallocData()` the deallocator now stamps the
claim on the whole owned set and looks for a lease open in it; a derived
claim would not do, since the teardown removes the edges it derives from.
With none open the stamp alone refuses the lease a wrapper-subclass child
could still take between the teardown and the destructor. With one, the
destructor goes to the last of them, and since the stamp refuses new ones
those are the only leases that can hold it back. The wrapper is at refcount
zero and freed a moment later, so it cannot be pinned the way a waiting root
is: the record carries what the deallocator would have used, the destructors,
the tombstones and a reference per leased member. The release runs it after
the waiting roots, on the main thread's queue where the type asks for that.

Bit `DeallocClaim`; cleared, the deallocator destroys the owned set without
looking, and `dealloc-waits-for-lease` sees `destroyed` fire under a lease.

### The deallocator's stamp is taken back

Unlike the stamp of `Shiboken.delete()`, this one is taken back where it was
wrong. The binding graph says what the destructor should take, not what it
does: `QQmlComponent.create()` makes the component the parent of the object
through the return value heuristic, and the component's destructor leaves
that object alone. A member with a C++ wrapper can outlive the destructor
with a valid wrapper, so the claim pins the ones it stamps.

Once the destructor is past - inline, after the last lease, or behind it in
the main thread's queue - a member that still has its pointer gets its leases
back; one the destructor deleted went through `Object::destroy()` and has
none. Until then a survivor is refused like a dying member, and a lease open
on it holds the destructor back.

There is no bit for the take-back; `dealloc-claim-survivor` guards it.

### Teardown claims what Python owns

Deleting the application walks every wrapper and destroys the QObjects
Python owns. That walk took a call lease on each and then tested ownership
and validity without the lock - but a lease does not refuse a call in
flight, it joins it. Another thread inside a call on the same object then
had the destructor run under it.

Under free threading the walk asks for the same claim `Shiboken.delete()`
takes, with the ownership test inside the transaction:
`callCppDestructorsIfOwned()`. An object nobody is calling is destroyed at
once; one with a call in flight is claimed, refuses new leases, and its
destructor runs when the last lease comes back - on that thread, as a
deferred `Shiboken.delete()` does. An object C++ owns is left alone, as
before.

There is no bit: the lease was not a measure, it was the defect.
`teardown-vs-call` guards it.

### A deferred destruction keeps the main thread

A destruction that waits for a lease runs when the last lease comes back, on
the thread that returns it. `QWidget`, `QWindow` and `QQuickItem` are
destroyed in the main thread (`delete-in-main-thread`), and the deallocator
already sends them there; the lease release did not. A `Shiboken.delete()`
of a widget from the main thread then destroyed it on a worker.

Under free threading a ready root of such a type goes into the same queue the
deallocator uses, pinned and still claimed, and takes the roots and
deallocations released after it along, so their order holds. The main
thread finishes it from a pending call. `deferredDeleteQObject()` used to
drain the whole queue on its own thread, detached; it now deletes only its
own object, and an entry that still meets another thread puts itself back.
A child with an open lease can join the set while the root waits, so the
set is tested again before the extraction. Finalization drains pending calls
before the exit handlers run. Any other QObject is still destroyed where the
lease comes back, as the deallocator destroys it where the last reference
goes.

There is no bit: the queue is not a trade-off. `deferred-widget-dtor` guards
it.

### The instance dictionary is published once

A wrapper's `ob_dict` sits at `tp_dictoffset`, so CPython's generic
attribute code creates and reads it as well. Shiboken's helper created it
with a plain test and store, and a first access racing a `setattr` could
overwrite the dict CPython had just published, attribute and all. The
collector runs `tp_clear` with the world running again, and our map can hand
the object out in between: `tp_clear` released the dict under whoever read
it, CPython's own lock-free read included.

Under free threading the helper creates the dict the way CPython does, under
the object's critical section and published with a release store, and
nothing replaces it afterwards: `tp_clear` empties it, which breaks the
cycle, and the dict goes with the wrapper. A borrowed dict therefore lives as
long as the wrapper its caller holds. An object taken out of the map during
that window survives with its children, references and dict cleared.

Bit `DictPublishOnce`; cleared, the plain store and release come back.
`proof-dict-first-access` then loses an attribute set meanwhile, and
`proof-dict-survives-clear` sees `tp_clear` replace the dict a reader holds.

### The weakref list head is CPython's

The deallocator tested `sbkObj->weakreflist` before calling
`PyObject_ClearWeakRefs()`. That head is the one piece of a dying object's
state another thread may still touch: a weakref operation reaches the
referent's list under CPython's own hashed weakref lock, and the plain load
races it. What the load sees can also be stale enough to skip the call, and
with it the synchronized clearing and the callbacks.

The test is gone under free threading. `PyObject_ClearWeakRefs()` makes the
empty check itself, atomically and under that lock, so the precheck bought
nothing but the race. The call stays behind `Py_IsInitialized()`, which is
about static destruction and not about weakrefs.

There is no bit: the precheck was an optimization, not a measure, and taking
it back is the race itself. `weakrefs` is the guard that parks a thread
between the last reference and the clearing.

### Who may read parentInfo

`setParentLocked()` publishes a freshly allocated `ParentInfo` with a plain
store under the state lock, and several readers used the field without it.
`SbkObject_tp_clear()`, `_destroyParentInfo()` and `deallocData()` tested it
before calling a helper; `destroy()` read it under the lock and acted on the
answer after. A clear runs with the world restarted, so a native callback can
install a first parent under it - the load races the store, and a null read
skips a child that is attached by the time the detaching would have happened.

Under free threading the prechecks are gone and the helper is called
unconditionally. Every helper below reads the field inside a transaction and
does nothing when it is null: `_detachChildren()` and `detachFirstChild()`
break on it, `removeParentLocked()` returns. The diagnostics, `Object::info()`
behind `shiboken6.dump()` and `_debugFormat()` behind `debugSbkObject`, walk
the children and the referred objects under the lock, so neither may be
called while holding it. `shiboken6.dumpTree()` raises `NotImplementedError`
instead: it formats each child with the lock released, which is not safe
against the child set changing under it.

`tp_traverse()` keeps its plain reads, because the collector stops the world
around them.

There is no bit: the readers were saving a lock acquisition, not trading a
guarantee. No failpoint test carries this - the defect is a data race with no
divergent outcome to observe, so TSan is what shows it.

### The class hierarchy publishes snapshots

`addClassInheritance()` mutated the graph under no lock while
`findDerivedType()` and `dumpTypeGraph()` were walking it (B4-4). A lock
around both ends is not available here: the traversal creates types through
`Module::get()` and calls generated discovery functions in the middle of
itself, so it runs arbitrary Python and cannot hold one.

The edges are immutable instead. A writer copies the map and publishes the
copy; a reader takes the current snapshot under a short lock and walks it
with none held. What a traversal sees is therefore one graph from beginning
to end, even when a module publishes hundreds of edges underneath it. The
lock is `ClassHierarchy`, rank 2, and the inventory above says what may be
held across it.

A module hands its edges over as one table for the same reason the snapshot
exists: publishing copies the map, so one call per edge copied it once per
edge, and a full build has 436 of them. The generated `initInheritance()`
calls `addClassInheritance()` once.

There is no counterproof. `failpoints.py hierarchy-snapshot` parks a
traversal with one iterator alive and imports fourteen modules under it,
which makes the race deterministic - but with the snapshot taken away it
still passes four runs out of five, because libc++ keeps `unordered_map`
nodes alive across a rehash. A one-in-five crash is not a proof, and the
test says so rather than claiming to be one.

### MI offsets are computed once, and not cached

A type with more than one C++ base is registered under one address per base,
and the generated `mi_init()` computes those offsets. It used to fill a
static array behind a sentinel check: two threads reaching it together both
saw the sentinel, and both sorted, uniqued and `memmove`d the same array
(B4-3). The
initializer of a function-local static does that exactly once, whoever
arrives, and that is what the generator emits now.

The offsets were also cached in the type, filled by whichever registration
came first and copied into every Python subclass on every constructor call -
three writers to type state that readers walk without a lock. There is
nothing to cache: `mi_init()` computes on its first call and hands out the
same array afterwards, so the aliases are asked of it where they are used.
`SbkObjectTypePrivate::mi_offsets` is gone.

The offsets are a property of the layout, not of an instance. Virtual
inheritance is not modelled by them and is not supported.

The class graph is published the same way and for the same reason. It is
immutable, so a writer copies it, and a module used to add its edges one call
at a time - one copy of the whole map per edge, 436 of them in a full build.
A module's generated `initInheritance()` now hands over a table and the map
is copied once.

There is no deterministic test for this one, and there cannot be: the race is
inside generated code, where a failpoint cannot be placed, and the threads
that lose it all write the same offsets, so nothing crashes either way. What
carries it instead is a sanitizer, and for that both sides have to exist. The
generator emits the sentinel version as well, behind `MiOffsetsOnce`, and
`stress.py mi_first_instance` builds the first instance of every
multiple-inheritance type in the sample binding from eight threads at once.
With the bit cleared TSan has a race to report there; with it set it has
none. That is the whole evidence for this measure, and it is a weaker kind
than a counterproof - it is what the shape of the defect allows.

Measured, on the sanitizer tree: nothing with every measure on, and two to
six reports with `MiOffsetsOnce` cleared, in `Sbk_MDerived1_mi_init` and its
siblings - the sentinel read against the write of the offsets, reached
through `miOffsets()` from `registerWrapper()`.

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

### The two caches on a virtual call

A generated virtual override caches two things: the name of the Python method
to look for, in a function-local `nameCache[2]`, and the override it found, in
`m_PyMethodCache[i]` on the wrapper instance. Both were plain pointers written
by whichever thread reached the virtual first, and read by all the others.

The value is never wrong. Every thread computes the same name and finds the
same override, so a lost race costs a reference and not correctness: only the
pointer that ends up in the slot is ever owned by anybody, and the names come
from `PyUnicode_InternFromString()`, which hands out a new reference on every
call. What it also costs is a data race that a sanitizer reports on every
single run - seven of them out of the `signal_race` scenario alone on
03.09., which is the kind of noise a real finding hides in.

`Shiboken::CacheSlot` is the replacement: one pointer, `get()`, `publish()`
and `reset()`. Under free threading it is a `std::atomic<PyObject *>` with a
compare-exchange, and `publish()` returns what the slot holds afterwards and
drops the reference that lost. With a GIL it is the plain pointer it always
was. It is the size and alignment of the pointer it replaces, and a
`static_assert` says so.

There is no bit and no counterproof for this one, and there should not be: it
takes nothing away and adds no window. What it fixes is a reference leak that
no test can see and sanitizer noise that only a sanitizer can - so a
sanitizer is what says whether it worked.

Measured, same machine and same scenarios: `signal_race` reported **seven**
races on 04.09. and **six** as late as 09.09., in `overrideMethodName()`,
`Sbk_GetPyOverride()` and the two generated cache slots they are handed. It
now reports **none**. Across all fourteen scenarios twelve reports remain,
every one of them in the feature system - `sbkfeature_base`,
`initSelectableFeature()` around the subtype walk, `class_property` - which
is the finding this work package does not own. Not one report names either
cache any more.

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

Not every reader takes its pointer from the lease yet (see "What a lease
hands out"):

- `tp_getattro` and `tp_setattro` take a lease and then read the pointer
  again. They do not dereference it on the spot.
- `Object::cppPointers()`, `PySide::convertToQObject()` and the property
  setter of QtRemoteObjects' dynamic classes take no lease at all.

`CallLease{self, <type>}` takes the guard, arguments are constructed with
`Guard::Omit`. That is deliberate: a contended inner guard would run the
native call with the receiver's own guard suspended, so two nested guards are
never a two-object transaction. Where the generator emits
`Py_BEGIN_ALLOW_THREADS` or `ThreadStateSaver`, the lease is always
constructed before the detach region and outlives it - the guard is suspended
there, the lease is not.

### How far the guard actually reaches

The guard is a CPython critical section, and a critical section ends at every
detach. That is not a caveat to work around, it is what makes the guard
usable at all, and it is measurable from Python:

| While one thread is here | A second call on the same receiver |
|---|---|
| in a Python override called back from C++, busy-waiting | waits |
| in a native call that blocks with the thread attached | waits, for as long as the call takes |
| waiting for a `threading.Lock` | goes through |
| waiting in `QRecursiveMutex::lock()`, which is `allow-thread` | goes through |
| waiting in any wait that detaches | goes through |

So the lock inversion "guard first, then a lock" against "lock first, then the
guard" resolves by itself whenever the wait detaches - the receiver's section
is suspended for the duration and the other thread gets in. It does not
resolve when the wait keeps the thread attached, and that is the boundary
below. `sources/pyside6/tests/manually/freethreading/failpoints.py` measures
both halves rather than asserting them: `guard-vs-python-lock` and
`guard-vs-annotated-lock` for the resolving case, `guard-spans-native-wait`
for the other.

Two consequences worth stating. A blocking Qt method needs its `allow-thread`
annotation more under free-threading than it did with the GIL: without it the
call blocks every other thread that reaches the same receiver, and it blocks
stop-the-world for everyone. And nothing may be built on the guard being
continuously held across a Python C API call, because it is not.

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

`PYSIDE6_OPTION_FT` is a bit per measure, and clearing one puts back what was
there before it:

```
PYSIDE6_OPTION_FT             unset, and that is the only supported setting:
                              it means every bit there is, including the ones
                              added after whatever is reading this
PYSIDE6_OPTION_FT=0b011       the two locks only
PYSIDE6_OPTION_FT=off         without any of them
```

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
  - `MiOffsetsOnce` has a sanitizer A/B and can have nothing else; the
    section above says why.
  - `MetaObjectParseOutsideLock` has both: a `proof-*` for the race the
    split opens, and a `run.py` scenario for the contract assertion the
    cleared bit trips. That scenario needs a build with the assertions in
    it, and `run.py` skips it where they are absent rather than reading
    the silence as a result.

A mechanism that no scenario can take away does not get a bit. The readiness
flag on lazily created types is one such, and so is `Shiboken::CacheSlot`:
they are covered by the suites, not by the A/B harness.

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
scenario a proof when it crashes without it. Ten of the sixteen are proofs
at the moment; `signal_race` became one when the coarse lock went, because the
signal machinery reaches the wrapper lookups, the parent/child graph and
destruction, and the coarse lock had been covering that.

Run it with the free-threaded interpreter; `REPEATS`, `STRESS_THREADS` and
`STRESS_ITERS` size the run, and naming scenarios restricts it. Never run a
single scenario alone to judge a lock: rare races show up only over the whole
set, and a scenario on its own can stay clean hundreds of times.

### Deterministic races: failpoints

Repetition is a poor way to reach a window of a few instructions. A failpoint
is a named place where a test stops one thread, so the second one arrives in
the order the test wants, every time - a test that fails on an unfixed
revision rather than in one run out of fourteen. They sit either side of the
windows that matter, for example:
before weakrefs are cleared, before the C++ destructor runs, once the wrapper
is gone and only that destructor is left, once the destructor is past and the
tombstone is still standing, before a parent's destructor deletes the children
it has just handed back, after a lease is taken and before it is handed back,
before `destroy()` detaches `cptr` and again where `destroy()` is past but
the memory is not, between the check and the write in `setCppPointer()`,
inside a traversal of the class-inheritance graph with one iterator alive,
between the lookup that misses an instance meta object and the commit that
publishes one, and before `setParent()` publishes a new edge.
`Shiboken.failpointNames()` lists what a build has; a release build has none
and the tests skip.

The registry and the call sites are held together by
`libshiboken/check_failpoint_names.py`, which ctest runs. A name a test arms
but no `SBK_FAILPOINT()` carries lets that test run into its timeout; a name
in the code but not in `KnownFailpoints` cannot be armed at all, and the test
that wants it reports a skip - which is green. Both directions have cost a
day, which is why this is a check and not a convention.

Two properties are what make them usable rather than merely present. A parked
thread waits **detached**, so it blocks neither stop-the-world nor, on a
build running with the GIL, everyone else. And an armed point stops exactly
one thread: the arming goes with the first one through, so a test can park a
call and then drive the same code path from another thread to reach the
object the parked one holds.

`sources/pyside6/tests/manually/freethreading/failpoints.py` holds the tests.
They are not run directly for evidence, because a test that only ever ran
free-threaded shows that the code works there, not that the synchronization
is what makes it work. `failpoint_matrix.py` next to it runs each one in its
own subprocess, with a hard timeout and its own process group, on every
interpreter the argument needs:

| Row | Interpreter |
|---|---|
| `classic` | traditional CPython, its own debug build |
| `ft-gil-on` | free-threaded binary, `PYTHON_GIL=1` |
| `ft-gil-off` | the same binary, `PYTHON_GIL=0` |

Each child verifies the GIL state it was asked for **after** importing
PySide, because that import is what can turn the GIL back on; a row that
silently ran in the wrong mode would be a second measurement of the first.
A build directory carries the Python version but not whether that Python was
free-threaded - `qfpdp-py3.15-...` is the same name for 3.15.0b3 and
3.15.0b3t - so each row names its interpreter and its build and the two are
checked against each other through the extension suffix. A row without a
build is reported as missing and the run ends as partial, never as green.

    FT_PYTHON, FT_BUILD_DIR      the free-threaded row, defaults to the
                                 interpreter running the script
    GIL_PYTHON, GIL_BUILD_DIR    the traditional row, no default

A test may declare that its expected outcome is not "ok":
`lazy-lock-spans-destruction` is listed as failing while B13-5 is open, and
the runner can treat a deliberate deadlock's timeout as the pass. Both mean
the same thing - the day the cell changes, the entry comes out.
