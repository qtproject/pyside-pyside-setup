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
run between the lease and the pointer read the way it can here. This document
describes
both, the locks that are deliberately separate from them, and what it all
means for application code.

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
