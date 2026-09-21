# Free Threading: Generated Code, Signals and QML

What reaches generated entry points, signals and slots, QtRemoteObjects and
QML, and what the lock contract leaves to the application.

Part of the free-threading notes. [The overview](freethreading.md) has the
state lock, the call guard and the leases these sections build on.

## A signal instance remembers its type weakly

A signal instance keeps the type of its source to find the homonymous method
later, stored as a raw pointer. Every read sits behind a check that the
source is alive, and with a GIL a live source keeps its type. Under free
threading the check and the read race: another thread can finish the last
wrapper and release the type in between, and the walk over it now takes a
`PepMroRef`, which asks the type for its `__mro__`.

A strong reference is not the answer: a signal instance is not tracked by the
collector, and a class that keeps one of its own bound signals would close a
cycle through that edge and never be freed. Under free threading the record
holds a weak reference instead, and each reader resolves it to a strong one
for as long as it uses the type. A type that is gone has no homonymous
method, and a wrapper built for the sender then gets its type from the QObject
heuristics. Every type takes weak references; should one refuse, the record
reads as if the type were gone.

There is no bit: a reference is not a measure that can be switched off.
`signal-type-collectable` guards the cycle; the race has no failpoint.

## A capsule method owns its instance

QtRemoteObjects gives a dynamic class its slots and properties through a
descriptor that binds a builtin function to a capsule. The capsule records
the instance and the descriptor's own capsule as raw pointers, and the handler
reads the instance as `self`. A bound method that outlives its object reads
a freed wrapper, and every access leaks: the method's capsule takes one
reference too many, and a property access never releases its function.

Under free threading the function's `__self__` is a tuple of the instance
and the capsule: nobody can write it, and the collector traverses both. The
capsule's context holds the descriptor, which owns the method definition and
the capsule the handler reads. Neither a capsule nor `__module__` can hold
the instance: a capsule shows the collector no edges, and `__module__` can
be assigned. A bound `PyMethod` is no way out either: `connect()` expects a
Python function behind every method. The method stays a builtin whose
`__self__` is that tuple instead of the capsule.

There is no bit: a reference is not a measure that can be switched off.
`capsule-method-owns-instance` and `capsule-access-no-leak` guard it. The
build with a GIL keeps the borrowed pointer and the leak.

## A source's property is read as a copy

A QtRemoteObjects source keeps its property values in a `QVariantList` of
its own, in a capsule in the instance dictionary, and one handler reads and
sets them. The getter held a reference into the list while it converted the
value, and the setter replaced the element in place. With a GIL the two never
overlap; under free threading a setter in another thread rewrites the variant
under the reader, and two setters write the same variant at once.

Under free threading every access to the list holds the capsule's critical
section. A read takes a copy and converts it after the section, and a set
swaps the new value in and releases the old one after the section, where its
destructor may run Python. The setter compares against its own read, so a
set that races another is ordered at that read. A source whose list is gone
raises a `RuntimeError` instead of locking a null capsule.

Bit `SourcePropertyCopy`; cleared, the getter holds the reference again and
`proof-source-property-copy` returns the value a setter wrote after the read.

## The guard's reach in generated code

Every generated entry that has a `cppSelf` takes a lease: methods, rich
comparison, the number, sequence and mapping slots, property getters and
setters, and the entries with an `allow-thread` detach. Checked against the
generated wrappers rather than the templates, because that is where a missing
one would sit.

That covers generated entry points and nothing else. Hand-written snippets
are outside it, and so is the buffer protocol -
`qbytearray-bufferprotocol` in `qtcore.cpp` reads `cppSelf` with no lease and
hands out a pointer into the object's memory. That is older than any of this
and belongs to the lease work; it is named here so the claim is not read as a
completeness argument it does not make.

Not every reader takes its pointer from the lease yet (see
[What a lease hands out](freethreading.md#what-a-lease-hands-out)):

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

## How far the guard actually reaches

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

## A failed conversion stops the entry

Under free threading a Python to C++ conversion can fail at any time: a
concurrent `Shiboken.delete()` makes the converter's own lease refuse, and
the converter leaves null or its untouched output behind, with an exception
set. Generated calls check for that before the native call. Without a check
a direct entry runs on that output (B10-3): rich comparison and the default
`__setitem__` use it, and a field setter writes it into the live field,
hands it to `keepReference()` and returns success with the exception
pending.

These entries, and the value converter of opaque containers, call
`Shiboken::Errors::conversionFailed()` before their first native statement.
A pointer field is converted into a local and written only after that check;
so is a container field, whose converter clears the target and inserts every
element, the failed ones as null or default-constructed items, so the live
field would be lost before the check could refuse. A value field stays the
conversion target, since a failed copy conversion writes nothing.
`returnFromRichCompare()` keeps the conversion's exception instead of
reporting that no operator matched.

Bit `ConversionGate`; cleared, the entries run on the conversion's output,
and so does the check in the QProperty setter, which
`proof-conversion-gate` measures.

## Method slots own their receiver for the call

A slot for a bound method keeps a reference on the function and a weak
reference on the receiver, so that the connection does not keep the
receiver alive. Delivering through a raw receiver pointer beside it binds a
receiver the slot does not own (B12-4, B14-4). The weakref callback that
disconnects is cleanup after the fact: a delivery already running keeps
going while another thread drops the receiver's last reference.

The weak reference is now the slot's only authority over the receiver.
Each delivery upgrades it with `WeakRef::deref()` and owns the receiver
until the Python call returns. A receiver being destroyed has its weak
references cleared before any callback runs, so the upgrade answers a live
object or nothing, and nothing means no call.

Bit `MethodReceiverUpgrade`; cleared, a delivery binds the raw receiver
pointer without touching its refcount and a receiver without weak reference
support is held raw, which `proof-method-receiver-upgrade` measures.

## A receiver without weak references is held whole

A receiver whose type has no weak reference support - `__slots__` without
`__weakref__` - gets a strong reference on the whole bound method instead,
which keeps the receiver alive as long as the connection. The cost is a
cycle: a receiver that owns its sender is held through `PySideQSlotObject`,
which the collector cannot walk, and is never freed.
`slot_weakrefless_receiver_test.py` measures that cycle and has to be turned
around when it goes. Any other failure to create the weak reference, a
`MemoryError` for one, takes the same fallback and is reported as
unraisable.

Not repaired: connecting the same bound method twice still leaves one
registry row for two Qt connections (B14-5), so the weakref callback
disconnects only one of them - the surviving connection does not deliver to
the dead receiver. Representing equal connections needs the record model of
the FT5 handoff.

`WeakRef::deref()` exists in the free-threaded build only, where
`PyWeakref_GetRef()` is always available; a build with a GIL has no caller.

## Only the type QML asked for takes the address

QML constructs a registered type into memory it allocated itself, and the
generated constructor places the object there. The address used to sit in one
thread-local slot, and a registered type that creates another QObject before
its own construction finishes has two of them live at once (B15-4).

The placement context nests, and an address carries the type QML asked for,
so the inner object - of a different type - is turned away and gets ordinary
memory. What the type test cannot turn away is a second object of the *same*
type built there first; telling those apart needs the address to travel with
the object rather than with the thread, which belongs to the wrapper-identity
work.

Bit `QmlPlacementType`; cleared, the first constructor to run takes the
address whoever it is, and `proof-qml-type` segfaults because QML then holds
the inner object.

## QML construction holds no process-wide lock

The placement address used to be published behind a process-wide `QMutex`
held across `PyObject_CallObject()`. It protected nothing another thread
could read, since the slot was thread-local, and it deadlocked a same-thread
nested creation outright. The context is per thread now and needs no lock, so
nothing binding-wide spans the Python call that constructs a QML type.

Bit `QmlPlacementFree`; cleared, that mutex is back across the call, and
`proof-qml-scope` hangs until the runner kills it - the second thread cannot
enter `createInto()` while the first is in Python.

## What the lock contract does not promise

No general freedom from deadlock. The contract covers the locks listed in
[the inventory](freethreading.md#the-complete-inventory):
none of them is held across Python, Qt, a decref, a destructor or an
unbounded wait, except where these notes name the exception. It says
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

Nor is QML construction promised to survive every nesting: a second object of
the same type built inside `__init__` still takes the placement address, as
the section on it says.

`abi3t` is not supported, and behaviour after `fork()` is undefined for a
process that has used the bindings; use `spawn`, or `fork` followed by
`exec`.
