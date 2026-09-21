# Free Threading: Wrapper Lifecycle

How a wrapper is found, published and destroyed while other threads hold
it: the wrapper map and its tombstones, destruction claims, the deallocator,
and the instance dictionary and weakref list.

Part of the free-threading notes. [The overview](freethreading.md) has the
state lock, the call guard and the leases these sections build on.

## The preflight in front of a virtual call

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

`NativePreflight` is the bit; cleared, `proof-native-preflight` discriminates
through that assertion - which means it says nothing in a release build, where
the unsafe read would simply happen. The measure is real either way; what is
debug-only is the ability to show it.

## A retired identity leaves a tombstone

The wrapper map answers "which Python object stands for this C++ address".
Removing an entry when a wrapper dies is not enough: the destructor has not
run yet, and a lookup in between sees an empty map, decides the address is
free, and publishes a second wrapper for an object about to be destroyed
(B4-1), marked valid with a pointer that goes stale a moment later.

An entry therefore does not leave the map when the wrapper dies. It is marked
dying and stays until the destruction that retires it can no longer reach the
address: past the C++ destructor for a destruction the binding drives, past
the `operator delete` for one C++ drives. A conversion that meets a tombstone
gets a wrapper with
no C++ pointer and no validity, so every use of it raises rather than reading
freed memory - unless the dying type invalidates such wrappers itself.

The deallocator lays one down, and so does `Shiboken.delete()`: both run the
C++ destructor themselves and know when it is past. A destruction handed to
the main thread queues its tombstone directly behind the destructor it waits
for, not behind `deallocData()`: that runs Python, the main thread can drain
the queue while it does, and the tombstone would stand over an address whose
destructor has run and refuse it until a second drain.

Bit `Tombstones`; cleared, the entry is removed when the wrapper dies, and
`proof-tombstones` sees a second wrapper published over the dying one.

## Reading a dying entry, and retiring it

The wrapper an entry points at is not readable once it is dying, and that is
what the entry's type reference is for: a lookup can tell whether a dying
identity is the one it asks about without touching a wrapper that may
already be freed. The reference is taken under the map lock, which an
increment may span, and dropped when the tombstone falls, which a decref may
not span.

`acquire()` is the only place that may turn the map's borrowed pointer into
a reference, and it asks `PyUnstable_TryIncRef()`, which reads the object.
On a tombstone that is freed memory, and where the allocator had recycled the
block the increment succeeded and handed out a stranger. The guard belongs in
`acquire()` and nowhere else.

A tombstone has to fall while anything can still observe it, because what it
holds - the entry, and the wrapper the exception two sections on lets through
- is released when it does. It does fall: the deallocator retires it after the C++ destructor, and
a deferred destruction retires it from the same queue. Both go through
`retireWrapper()`, which
takes the strays out under the map lock and invalidates them outside it -
invalidation walks the object graph and takes the state lock, which the map
lock may not span.

## A dying QObject still hands out its argument

The exception is `destroyed(QObject *)`, and it is not a convenience: Qt
emits the signal from `~QObject`, the argument is meant to be used there, and
PySide invalidates whatever wrapper the conversion produced right after the
signal. A tombstone that refused would hand the
handler an argument it cannot touch, which
`signals/signal2signal_connect_test` measures. A plain C++ class has no such
mechanism - `QRecursiveMutex` would keep the stray valid forever - so it
keeps the tombstone.

libshiboken does not know what a QObject is. PySide installs a predicate
with `setDyingConversionPredicate()` when QtCore is initialized, and the map
asks it about the *dying* type, not about the one being looked up: what
decides is whether the destruction that is running will invalidate what the
conversion hands out. The question is asked per type, not per moment, so for
a QObject the whole destruction is open, not just the stretch around the
emit.

Bit `DyingConversionException`; cleared, the tombstone refuses every dying
identity, and `proof-dying-qobject` finds the handler holding an argument it
cannot use.

## A stray wrapper belongs to its tombstone

What closes the window the exception opens is not a narrower question - the
moment PySide's invalidation runs is not something the binding is told - but
the other end of the same transaction: a wrapper the exception lets through
belongs to the tombstone that let it through. It is not entered in the map,
so no later lookup can find it and no invalidation path outside libshiboken
can be expected to reach it; the tombstone holds a reference to it and
invalidates it when it falls. Usable exactly as long as the destruction it
was made for is running.

That the map does not carry it is the load-bearing half. An entry would
outlive the tombstone and become the canonical wrapper for whatever the
allocator puts at that address next - the worst of the three damages, after
"says valid over freed memory" and "says valid over a stranger". Two
conversions inside one window still get the same wrapper: the tombstone is
asked first and hands its stray back the way the map would have.

Bit `DyingStrays`; cleared, such a wrapper is registered like any other, and
`proof-dying-strays` finds it still valid after the destruction is past.

## Static destruction abandons the map

What is left when `~BindingManager` runs is abandoned, tombstones included. A
static destructor runs on whichever thread unloads the image, possibly after
finalization has begun, so it must not run Python. Nothing is lost:
`Object::destroy()` only detaches a wrapper from its C++ object and never
runs the destructor.

## A destruction C++ drives has no second moment

`Object::destroy()` is called from the C++ side, normally from the destructor
of a wrapper C++ owns: the binding hears a destruction begin and is never
called again to say it is over, so there is no moment to retire the tombstone
at, and removing the entry leaves true absence for the base destructors.

The tombstone is laid anyway, keeping what retirement needs - the pointer
array the object no longer carries, and a reference on the type - and waits
for one of the two moments that do come back:

  * **the generated wrapper's `operator delete`**, the ordinary ending where
    the class has a virtual destructor: the point the language guarantees
    after the last one, found through the vtable even when foreign code
    deletes through a base pointer.
  * **a construction publishing at the same address**, through
    `registerWrapper()` and only that: an allocator cannot reuse an address
    before the previous destruction is over, so a new object there is proof.
    It covers what the first misses, a placement-constructed object ended by
    an explicit destructor call with no `operator delete` to follow.

A second destruction at the same address retires the first one's tombstone
as well; that is the recovery path, not an ending. A conversion is no proof
at all and does not come through `registerWrapper()`: meeting a tombstone is
what it is refused for.

Bit `ExternalTombstones`; cleared, the entry is removed as before, and
`proof-external-tombstones` finds a valid wrapper over a dying object.

## A destruction takes its children's identities too

`invalidate()` releases the owned children plainly and the parent's
destructor - one line later - is what deletes them, so each child had the
same window its parent no longer has. The owned set is collected before the
children are released, every child in it gets its own tombstone, and they
are retired with the parent's, after the destructor.

Children that carry a C++ wrapper are not in that set on purpose: nothing
releases their entry here, their own destructor calls `Object::destroy()`, and
that keeps the window `Object::destroy()` has and cannot close.
`delete-before-owned-dtor` is the failpoint in it.

Both paths do this, `finishDestruction()` and the deallocator, which carries
its own copy of the sequence and decides whether it will destroy anything
before it touches the map, because a tombstone stands for a destruction that
is going to happen: a wrapper that owns nothing destroys nothing, and its
entry is removed as before. Both halves are the same `Tombstones` bit, with
`replacement-of-child-in-dealloc` and `proof-tombstones-children` and
`proof-tombstones-dealloc-children` on them. Of the two failpoints either
side of the deallocator's window only `dealloc-before-cpp-dtor` - after the
wrapper is taken apart, before the destructor - sees it;
`dealloc-before-destroy` sits where removing the entry early already held.

## Claiming a native slot is one transaction

A generated constructor writes the C++ pointer into the slot of the wrapper
it belongs to. Reading and writing it used to be two steps, and a Python
subclass can put `self` where another thread finds it before it calls the
base initializer: both saw an empty slot, both built a C++ object, both
reported success (B5-3), one was left with nobody to delete it, and validity
and ownership described whichever write landed last.

The claim happens in one state-lock transaction now, so exactly one thread
takes the slot and the other is told the object is already initialized - the
error a second `__init__` from one thread already raised. The loser destroys
its candidate and nothing else; raising happens after the transaction,
because it is a Python call-out.

Bit `ConstructorCommit`; cleared, the check and the write are two steps
again, and `proof-ctor-commit` gets two winners for one object.

## The slot is reserved before the object is built

One transaction is only the second half: the slot used to be claimed *after*
the C++ constructor, so the loser had built its object - and, for a QObject,
hung it in Qt's tree - before it heard that it lost. The generated
constructor reserves the slot first, through
`Shiboken::Object::ConstructionGuard`, whose destructor gives it back, which
is what makes it usable in code that bails out of a dozen places.

The slot in `cptr` stays null while it is reserved. A sentinel would have to
mean something to the forty-odd places that read `cptr`, one of which
compares two objects through `cptr[0]`, where two objects under construction
would be the same object. The reservation is a bit beside it, in
`SbkObjectPrivate::constructingSlots`, and only the construction path asks
about it.

`ConstructorClaim` is the bit; cleared, the slot is claimed after the
constructor as it was, and `proof-constructor-claim` sees two C++ objects
built for one wrapper: it parks the first thread where it is about to
publish and counts the parent's children while it is there.

## Publishing an object is one call

What the constructor publishes used to be four calls - claim the slot, mark
valid, mark wrapper, register - and every other thread could meet the object
between two of them. `Shiboken::Object::commitConstruction()` does the three
that matter in the one order the lock contract allows: the state lock is the
leaf, so the map may not be taken while it is held, which puts the
registration first. What is visible in between is an object that is
registered and not yet valid, on which a call refuses - the safe half, and
the one the "`__init__` not called" error already covers. The reverse order
would leave a valid object that is not in the map, and a conversion of the
same pointer would publish a second wrapper for it. The generator emits that
one call, so `setCppPointer()` and `registerWrapper()` no longer appear in
generated code.

## A constructor holds a lease past the commit

Publishing is where the reservation stops protecting anything:
`Shiboken.delete()` does not ask about it, so from the commit on another
thread can destroy the object - while the constructor still uses it. The
QObject setup reads `cptr->metaObject()` and fills properties, and injected
code at the end works on `cptr`.

A generated constructor with a QObject setup, or with injected code at the
end, therefore takes a lease on `self` right after the commit and holds it
to the end of the body. A delete in between is deferred to that lease's
release; one that got in before the lease makes it refuse, and `__init__`
raises instead of running on a destroyed object.

Bit `ConstructorTailLease`; cleared, the setup runs with no lease, and
`proof-constructor-tail-lease` sees the object destroyed while its
constructor is parked at `ctor-after-publish`.

## Destruction claims follow the parent graph

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
a child that moved out stays refused, one that moved in is admitted, which
`proof-claim-ancestry` measures. B6-2 has no failpoint test yet; the test
README says what the harness lacks.

## A teardown keeps the claim

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

Bit `ClaimThroughTeardown`; cleared, the claim goes with the edge, and
`proof-claim-teardown` finds the torn-down child admitted again.

## A teardown detaches the edge it read

`removeParentLocked()` removes the *current* parent, and `_detachChildren()`
picked a child in one transaction and removed its parent in another. A
thread holding a lease on an unclaimed child could reparent it in between;
the teardown then erased the new edge, and a later `Shiboken.delete()` of
the new parent no longer saw the child's leases.

`_detachChildren()` now invalidates and detaches in the transaction that
picks the child. The invalidation plan cannot, because releasing wrappers
takes the map lock, so it remembers the parent and detaches only from that
one.

Bit `DetachCheckedParent`; cleared, the removal takes the current parent
again, and `proof-detach-checked-parent` sees the reparented child's new
edge erased.

## The deallocator claims the owned set

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
looking, and `proof-dealloc-claim` sees `destroyed` fire under an open
lease.

## The deallocator's stamp is taken back

Unlike the stamp of `Shiboken.delete()`, this one is taken back where it was
wrong. The binding graph says what the destructor should take, not what it
does: `QQmlComponent.create()` makes the component the parent of the object
through the return value heuristic, and the component's destructor leaves
that object alone. A member with a C++ wrapper can outlive the destructor
with a valid wrapper, so the claim pins the ones that could.

Once the destructor is past - inline, after the last lease, or behind it in
the main thread's queue - a member that still has its pointer gets its leases
back; one the destructor deleted went through `Object::destroy()` and has
none. Until then a survivor is refused like a dying member, and a lease open
on it holds the destructor back.

There is no bit for the take-back; `dealloc-claim-survivor` guards it.

## Teardown claims what Python owns

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

## A deferred destruction keeps the main thread

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

## The instance dictionary is published once

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

## The weakref list head is CPython's

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
