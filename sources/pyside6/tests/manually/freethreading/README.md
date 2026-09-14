# Deterministic lifetime races

The A/B harness in this directory reaches a race by repetition: it starts
threads and hopes they collide, which takes tens of runs to hit a window of a
few instructions once. `failpoints.py` arms a named point in the runtime
libraries instead, so the two threads meet in the order the test wants, every
time. That
is what makes a test fail on an unfixed revision rather than one run in
fourteen.

A failpoint is compiled into debug builds only. Against a release build every
test skips - `Shiboken.failpointNames()` comes back empty.

Names like `B7-2` or `FT8 invariant 2` below are the review's; what they
stand for is in `sources/pyside6/doc/developer/freethreading.md`.

    BUILD_DIR=<build> python failpoints.py
    BUILD_DIR=<build> python failpoints.py weakrefs

`failpoint_matrix.py` is the other way in. It runs each test in its own
subprocess on the three interpreters the validation plan names - traditional
CPython, a free-threaded binary with `PYTHON_GIL=1`, and the same binary with
`PYTHON_GIL=0` - which is what makes a passing test evidence rather than an
observation.

Exit codes, which the matrix reads: 0 clean, 1 a test failed, 2 the setup is
wrong, 77 nothing to test because this build has no failpoints.

`fpharness.py` holds the machinery; this file holds the reasoning.

## What a test here has to earn

A test that passes with and without the code it is named after proves
nothing, and two of the tests in this directory were exactly that until a
review found them. So each measure FT8 added can be switched off at runtime
through `PYSIDE6_OPTION_FT` (`sbkftoptions.h`), and the tests named
`proof-*` run their subject in a child process with one bit cleared and
require it to fail there. If it still passes, the test is not testing what
its name says and the `proof-*` cell is what says so.

One test is expected to FAIL. It holds a finding that belongs to another
work package, and the line comes out of the registry the day that package is
done. A run that does not reach the defect reports *skipped*, not ok.

## The tests

Two sections below have no test, and say why. That is deliberate: a finding
whose code path nothing can reach, or a race that is inside generated code
where no failpoint can be placed, is worth writing down and worth repairing,
but inventing a test for it would only look like evidence.

### weakrefs

B7-2: the deallocator clears weakrefs while another thread holds references.
One thread drops the last strong reference and parks inside deallocation,
just before the weakrefs are cleared. A second thread then operates on every
kind of reference to the dying object. Every callback must run at most once,
and the referent must be dead when it does. The list head is no longer read
before the call.
See "The weakref list head is CPython's" in the free-threading notes.

The object is created in the worker, not in the test body: CPython's biased
reference counting makes the creating thread the owner, and a `del` in
another thread only decrements the shared count, so the deallocation would
not run where the test waits for it.

### replacement-while-dying, proof-tombstones

B4-1: a lookup between unregistering the entry and the C++ destructor. One
thread drops the last reference and parks in the deallocator, past the point
where the map entry used to be removed and before the destructor runs. The
test then converts the same address, which is what `destroyed(QObject *)`
delivery and a parent conversion do in an application.

Removing the entry early - which the lock-scope work did - closes only half
of the window. In the other half a lookup sees true absence and publishes a
second wrapper, and that one is marked valid while the destructor is about
to run underneath it. The entry now stays as a tombstone until the
destruction can no longer reach the address, and a conversion that meets one
gets a wrapper that is not marked valid instead of one that points at freed
memory.

`QRecursiveMutex` and not `QObject`: a QObject's `destroyed()` signal
invalidates a stray wrapper afterwards, which hides the window. That is why
this went unnoticed - it only bites the object types that have no such
signal.

`proof-tombstones` clears `Tombstones` in a child and requires the failure
to come back.

### replacement-before-cpp-dtor, proof-tombstones-late

The half the test above cannot see. It parks at `dealloc-before-destroy`,
which is before `deallocData()` - and `deallocData()` goes through the
wrapper map on its way out, so until this test existed it took the tombstone
with it. Between that point and the C++ destructor a lookup saw true absence
again, which is the very thing the tombstone was introduced to end.

The new failpoint `dealloc-before-cpp-dtor` sits after the wrapper is taken
apart and before the destructor, which is the window B4-1 is about. Two
failpoints, because one of them stands in a stretch where removing the entry
early already held: a test parked there passes either way.

`proof-tombstones-late` clears `Tombstones` and requires the failure back.

### replacement-of-owned-child, proof-tombstones-children

The same window one level down. A tombstone covers the object being
destroyed; it did not cover what that object owns. `invalidate()` hands the
owned children back blank, their entries leave the map, and the parent's C++
destructor deletes them a line later - and in between a lookup on a child
address saw true absence.

The test parks at `delete-before-owned-dtor`, which is exactly that gap, and
asks for a wrapper on the child. `sample.ObjectType` rather than a QObject on
purpose: a QObject is the one type the tombstone makes an exception for, so
it cannot show this.

`proof-tombstones-children` clears `Tombstones` and requires the failure back.

### replacement-of-child-in-dealloc, proof-tombstones-dealloc-children

The same window, reached the other way. The test above drives it with
`Shiboken.delete()`, which goes through `finishDestruction()`; dropping the
last reference goes through the deallocator instead, which carries its own
copy of the same sequence and did not have the child tombstones - a review
found that after the first half was written and green.

The failpoint parks in the *child's* deallocation, which runs inside the
parent's: both wrappers are gone and neither C++ destructor has run.

`proof-tombstones-dealloc-children` clears `Tombstones` and requires the
failure back.

### dying-qobject-argument, proof-dying-qobject

The exception the tombstone makes for QObject, from both sides. A tombstone
refuses to hand out a wrapper for an address being destroyed;
`destroyed(QObject *)` is emitted from inside that destruction and its
argument is meant to be used. PySide invalidates that wrapper right after the
signal, so the refusal does not apply to a type that does this - libshiboken
asks a predicate PySide installs with QtCore.

Both halves are the claim: usable in the handler, dead afterwards. The second
half is the load-bearing one. If it stopped holding, the exception would hand
out a wrapper nobody ever invalidates, which is the defect the tombstone
exists for - and `signals/signal2signal_connect_test` in the ordinary suite
only measures the first half.

`proof-dying-qobject` clears `DyingConversionException`: the tombstone then
refuses every dying identity, and the handler is handed an argument it cannot
use. The exception is a measure, so it has a switch like the rest of them.

The predicate is asked about the type, not about the moment, so for a QObject
the whole destruction is open and not just the stretch around the signal. What
follows from that is the next test.

### stray-outlives-tombstone, proof-dying-strays

The other end of the exception. Since it is asked per type, a conversion may
also land *after* the signal - past the C++ destructor, before the tombstone
falls. Such a wrapper used to be registered like any other: it said "valid",
it pointed at freed memory, and when the tombstone fell it stayed behind as
the wrapper for whatever the allocator put at that address next. Nothing
invalidated it, because the path that invalidates the handler's argument -
PySide's `_PySideInvalidatePtr` property - runs earlier, with the property
data.

The failpoint `dealloc-before-retire` parks the deallocating thread in exactly
that stretch, and the test converts the address from another thread. What it
gets back is usable, and has to be dead once the parked thread is released:
the wrapper now stays out of the map and belongs to the tombstone, which
invalidates it on the way out.

That makes the second half of `dying-qobject-argument` ours rather than
PySide's. Both are checked, because the two paths are independent and either
one holding is not the other one holding.

`proof-dying-strays` clears `DyingStrays`: the wrapper is registered as any
other and is still valid when the test looks again.

### external-destruction, proof-external-tombstones

The destruction the binding does not drive. The deallocator and
`Shiboken.delete()` run the C++ destructor themselves and know when it is
past; here foreign C++ deletes an object Python knows, the generated wrapper
destructor reports it through `Object::destroy()`, and nothing calls the
binding again.

`sample.ObjectType` built **from Python**, so it is an `ObjectTypeWrapper`
whose destructor reports at all - `ObjectType.create()` hands out a plain C++
instance with no wrapper, and deleting one of those is a window nothing can
see. The parent's `killChild()` is a plain `delete`, and the failpoint
`destroy-after-tombstone` parks the thread there, past the tombstone and
before the memory goes back.

Both halves, and the second is what keeps the first from being a leak: a
conversion in that stretch has to be refused, and the address has to be free
again once `operator delete` has run. A tombstone that never fell would
refuse that address for the rest of the process.

`proof-external-tombstones` clears `ExternalTombstones` and requires the
failure back.

### constructor-claim, proof-constructor-claim

B5-3 again, the half `two-thread-ctor` cannot reach. That one shows the slot
being claimed by exactly one thread - but the claim happens *after* the C++
constructor, so the loser has built its object anyway and, for a QObject,
hung it in Qt's tree before it hears that it lost.

The first thread parks at `ctor-before-publish`, where it has built its
object and is about to publish it. The second runs the same base `__init__`
right then, and the parent's children are counted while the first thread is
still parked - once it is released it finds the slot taken and deletes what it
built, and both outcomes look alike again.

`proof-constructor-claim` clears `ConstructorClaim` and requires the second
object back.

### metaobject-lifetime

Every QObject answers `metaObject()` with the same `&QObject::staticMetaObject`,
so the wrapper map holds one wrapper for it and hands that one to everybody.
Destroying any single QObject invalidated it and hit every other holder,
although the C++ object behind it is static and never dies.

Five lines, with a GIL, no threads. The third one is the whole test - leave it
out and the shared wrapper is not among `b`'s referred objects, nothing
touches it, and the remaining four pass on a broken build:

    a, b = QObject(), QObject()
    ma = a.metaObject()
    mb = b.metaObject()         # the SAME wrapper, fetched through b
    Shiboken.delete(b)          # a stranger
    ma.className()              # RuntimeError: already deleted

Bisected to `4c1d56fb6` (29.07.2026, "Add a coarse lock for free-threaded
builds"), which moved the bookkeeping in `callCppDestructors()` ahead of the
C++ destructors. Before that, `~Wrapper() -> Object::destroy() ->
clearReferences()` had already taken the referred objects out by the time
`invalidate()` ran, so it found nothing to mark dead.

That commit only exposed it. The defect is in the walk: `invalidate()` had
marked referred objects invalid since 2011, and a referred object is the one
case where the holder is *not* the owner - the `reference-count` tag exists
because a parent link would be wrong there. The walk is gone from both twins;
`ownership_invalidate_referred_test.py` in the sample binding is the
regression test, and it runs under ctest with the GIL as without it.

### lease-vs-destroy

The lease window: destruction arriving while a call holds a lease. A thread
takes a lease and parks; another destroys the same object. The destruction
has to be deferred until the lease comes back, and the call must not see a
detached pointer. It passes, and the reason it did not is worth keeping.

It was written as `obj.objectName()` and stood as an expected FAIL for days,
with the explanation that the generated code re-reads `cppSelf` after the
lease was granted. That explanation was wrong, and a stack at the raise says
so: the failing lease is the *first* one that call ever takes.

`obj.objectName()` is two leases. `tp_getattro` takes one to hand out the
bound method, the call takes another, and Python bytecode runs in between.
The thread parked in the first, the destruction landed in the gap, and the
second lease was refused - which is correct, because in that gap no call is
in flight. A GIL build divides the expression in exactly the same place.

The method is therefore bound before the failpoint is armed, and then the
test parks where it always meant to: inside the call, with the lease held.
The destruction is deferred, the call returns its value.

### teardown-vs-call - a guard, no proof row

Application teardown against a call in flight. A thread holds a lease inside
`objectName()` on a QObject Python owns and parks; the main thread deletes
the application, which walks every wrapper. The object must not be destroyed
while the call runs, the call must return its value, and the destructor must
run once the lease is back. `destroyed` is connected directly: the deferred
destructor runs on the thread that releases the last lease, and nothing
would deliver a queued call.

Deleting the application ends it for the rest of the process, so the test
runs itself in a child process. Without the claim it dies with SIGSEGV.
See "Teardown claims what Python owns" in the free-threading notes.

### deferred-widget-dtor - a guard, no proof row

A `Shiboken.delete()` of a `QWidget` deferred behind a lease. A worker holds
a lease inside `objectName()` and parks, the main thread deletes the widget,
the worker returns. `destroyed`, connected directly, must fire on the main
thread; without the queue it fires on the worker. A child process with an
offscreen `QApplication`; skipped where the build has no QtWidgets.
See "A deferred destruction keeps the main thread" in the free-threading notes.

### dict-first-access, proof-dict-first-access

Two first accesses to an instance dict. One thread asks for `__dict__` and
parks after finding none; the main thread sets an attribute, which makes
CPython create the dict. The reader must come back with that dict, attribute
included. A QObject wrapper cannot race here - its constructor creates the
dict before the object is published - so the test uses `QByteArray` and a
Python subclass of it.

### dict-survives-clear, proof-dict-survives-clear

`tp_clear` against a reader. A wrapper in a cycle of its own is collected on
a worker, which parks in `tp_clear` before the dict; the main thread takes
the wrapper out of the map with `wrapInstance()` and holds its dict. After
the clear that dict must still be the object's, and empty. Run for a plain
QObject wrapper and for a Python subclass, whose `tp_clear` is CPython's
`subtype_clear()` handing on to ours.
See "The instance dictionary is published once" in the free-threading notes.

### mi-pointer - an equivalence, and no proof row

A lease asked for a base type computes that base's pointer itself: the
multiple-inheritance slot, then the special cast. Single inheritance never
reaches either. `sample.MDerived1` has two C++ bases and a cast function,
and the test converts and calls it as each base.

There is no `proof-*` row. Clearing `LeaseSnapshot` puts back
`Conversions::cppPointer()`, the function this arithmetic has to
reproduce, so both must answer the same. The row guards the arithmetic
against drift; it is not a measure.

### signal-type-collectable - a guard, no proof row

A signal instance remembers the type of its source, and a signal instance is
not tracked by the collector. A class that keeps one of its own bound
signals, `Holder.saved = Holder().fired`, is then a cycle whose last edge,
signal to class, only the record knows about: held strongly, the class is
never freed. The test drops the class, collects, and expects its weak
reference dead. A strong reference fails it; so does nothing on a build with
a GIL, where the pointer is raw. There is no `proof-*` row: a reference is
not a bit that can be cleared.

The use-after-free the weak reference also closes has no test here. Every
read of the type sits behind a check that the source is alive, so one thread
cannot reach a dead type; the race is between that check and the read, and
there is no failpoint in that gap.
See "A signal instance remembers its type weakly" in the free-threading notes.

### capsule-method-owns-instance, capsule-access-no-leak - guards, no proof row

G80: a QtRemoteObjects source keeps a bound slot, `method = source.reset`,
and drops the object. The first test expects the object alive under the
method and gone with it, then keeps the method in the instance dictionary
and expects the cycle collected, then assigns `method.__module__` and
expects the object still alive. The second checks a slot, two properties and
a POD field once, then reads and sets them 10000 times each and expects less
than 50 kB left in `tracemalloc`.

Without the fix the first test finds the object freed and the second 80
bytes per slot access. A capsule that holds the instance fails the cycle, a
function that holds it as `__module__` the assignment. Both skip on a build
with a GIL, which keeps the old code, and on a build without QtRemoteObjects.
See "A capsule method owns its instance" in the free-threading notes.

### source-property-copy, proof-source-property-copy

G84: a QtRemoteObjects source's getter parks at `source-property-after-read`,
the value read but not yet converted, and the main thread sets the property.
The getter must return the value it read. The test sets the property once
first, so the instance's list no longer shares its data with the type's and
the setter writes into the element the getter reads. `proof-source-property-copy`
clears `SourcePropertyCopy` and expects the getter to return the later value.
Skips on a build with a GIL and on one without QtRemoteObjects.
See "A source's property is read as a copy" in the free-threading notes.

### source-property-missing - a guard, no proof row

G85: a source whose `__PROPERTIES__` was deleted, or replaced by an integer,
is read and set. Both must raise `RuntimeError`; before the fix they locked
or dereferenced a null list. It runs in a child process, since a regression
crashes. Skips like the one above.
See "A source's property is read as a copy" in the free-threading notes.

### lease-snapshot, proof-lease-snapshot

B5-1: C++ deletes an object while a lease on it is out, and
`Object::destroy()` detaches the pointer array without consulting
`activeCalls`. The lease cannot defer that, but its holder must not read
the array a second time.

`Shiboken.VoidPtr(obj)` takes a lease, parks at `lease-after-acquire` and
copies the pointer out; the parent's `killChild()` runs in between. The
test expects the address the lease validated.

`proof-lease-snapshot` clears `LeaseSnapshot` and expects zero: the holder
reads the detached array again. The re-read tests for null, so the window
shows as a value rather than a crash.

### leased-receiver, proof-leased-receiver

The same window for the receiver of a generated call. `hash()` on
`sample.ObjectType` returns the receiver pointer without dereferencing it,
so the test can report the pointer of an object that is already gone
without touching freed memory. It expects the address the lease validated;
`proof-leased-receiver` clears `LeaseSnapshot` and expects the null that
`Conversions::cppPointer()` reads.

### metatype-subclass, proof-metatype-subclass

A class with a metaclass derived from the binding's, as in
`class Meta(type(QObject), ABCMeta)`. The test needs two answers: reaching
`lease-after-acquire` shows that a lease was taken at all, and the address
from `Shiboken.VoidPtr()` shows it is the right one.
`proof-metatype-subclass` clears `MetatypeSubclassLease`; the object then
takes no lease and never reaches the failpoint.

The object is kept alive until the process ends. Destroying a wrapper type
with its own metaclass crashes the interpreter, with a GIL and with every
bit cleared - a separate defect that would otherwise end the run before it
reports.

### claim-moves-out, proof-claim-ancestry

B6-1: a child that leaves a claimed parent leaves the claim behind.

A thread parks in `child.setParent(None)` with its lease taken, while the
binding graph still reads `parent -> child`. `Shiboken.delete(parent)` finds
that call open in the owned set and puts the destruction aside. Released, the
thread removes the edge, and its lease release runs the destruction without
the child. The test expects the child to be callable and deletable.

`proof-claim-ancestry` clears `ClaimByAncestry`: the request marks the whole
owned set once, the child keeps the mark of a parent it has left, and every
call on it raises.

### claim-survives-teardown, proof-claim-teardown

B6-1 from the other side: a child detached *because* its parent is torn down
has to keep the claim, since the parent's C++ destructor takes it along.

The root is `sample.ObjectType.create()`, built by C++: `Shiboken.invalidate()`
detaches children only from a root without `containsCppWrapper`, and every
object built from Python has one. Child and grandchild are `ObjectType`
subclasses, which keep `validCppObject`. A leased call on the child makes
`Shiboken.delete(root)` wait; `Shiboken.invalidate(root)` then hands the
children back, and the lease release skips the extraction because the root is
already invalid. The test expects the child to stay refused, and the
grandchild once no claim waits any more.

`proof-claim-teardown` clears `ClaimThroughTeardown`, and the child is
admitted again. Clearing `ClaimByAncestry` would not show it: that marks the
whole set at request time, and the row passes.

The grandchild check guards against a stamp that marks the detached child but
not its subtree. It has no bit of its own: with `ClaimThroughTeardown` cleared
the child check fails first.

### B6-2, a child that moves in - no test yet

A child that joins a claimed parent derives the claim once the edge is
published. The window to test is between that commit and the release of the
leases the publishing thread still holds, and nothing Python-visible runs in
it. Reaching it needs two threads parked at once, at `parent-before-commit`
and at `lease-before-release`.

`sbkfailpoint.cpp` has one armed name, one parked name and one release flag
for the whole process. Arming a second point forgets that the first holds a
thread, and releasing either name disarms both. Both points have to hold
their thread. Any window that needs two parked threads is out of reach.

The harness needs per-point arming, parking and release first. A short
timeout on the first point is no substitute: it enforces the order but hands
the result to a deadline.

### setter-conversion-fails, proof-conversion-gate

B10-3: a generated direct entry running on the output of a failed
conversion. A thread assigning to `Derived.objectTypeField` parks in the
pointer converter before the converter's own lease (`convert-before-lease`).
The test deletes the argument, so that lease refuses, writes null and sets a
RuntimeError. The test expects the field to keep its value and the setter to
raise.

The setter and not rich comparison, because the setter leaves the damage
readable. A comparison on a null operand crashes, which shows that the gate
matters but not what was left behind.

`proof-conversion-gate` clears `ConversionGate`: the null reaches the field,
which then reads `None`.

### owned-child-claimed - a guard, no proof row

A child built from Python has a C++ wrapper, and keeps `validCppObject` and
`cptr` after its parent's destruction has detached it, until its own
destructor runs. `Shiboken.delete(parent)` parks at
`delete-before-owned-dtor`, in that window, and the test expects the child to
be refused there. Only the claim stamped at extraction refuses it.

There is no `proof-*` row. Clearing `ClaimByAncestry` hides the defect rather
than restoring it: the request then marks the whole set, and the stamp has
nothing to add.

### parent-removal-alloc, proof-transaction-prepare

B6-4: a state transaction that fails halfway. `setParent(None)` reaches
`removeParentLocked()`, which erases the edge, hands ownership back and then
defers the decref of the edge reference - the last allocation, after every
write. The throwing failpoint `deferred-slot-alloc` fails that allocation. It
throws instead of parking, because a thread inside a transaction holds the
state lock.

The test expects the call to raise with ownership unchanged, and a retry to
succeed. It checks ownership and not `parent()`, because Qt has reparented
the object before the binding transaction runs.

`proof-transaction-prepare` clears `TransactionPrepare`: the room is taken
after the erase, and ownership has moved although the call raised.

### two-thread-ctor, proof-ctor-commit

B5-3: two threads run the same base `__init__` on one object. One parks
between reading the native slot and writing it, the second one runs the
whole initializer, and then the first continues. Without the transaction
both are told they won, and each of them has constructed a C++ object.

`proof-ctor-commit` clears `ConstructorCommit` in a child and requires two
winners to come back - and it clears `ConstructorClaim` in *both* runs. The
reservation refuses the second thread before it ever reaches the transaction,
so with everything on there is nothing left here to see. Measures nest, and a
counterproof for the inner one has to switch the outer one off to ask its
question at all.

### no-lock-in-python

FT8 invariant 2: no binding raw lock spans Python. A Python `__del__` is the
shortest way to ask. It runs from the middle of a wrapper's destruction,
which is exactly where the state lock and the wrapper-map lock are taken. If
either were held across the callback the `__del__` would see it, and a real
Python call under a lock deadlocks against stop-the-world.

### no-lock-in-conversion

The same invariant where an argument conversion calls back into Python. An
earlier version of this test ran its probe from a plain dict lookup and
proved nothing: that is ordinary Python, outside any call. The probe has to
run *inside* a generated entry point, and `__index__` on an integer argument
is the shortest way in - shiboken asks for it while converting, with the
receiver guard taken and the lease held.

That is what the second half of the measurement is for: `activeCalls()` on
the receiver says the probe really is inside the call, so a "no lock held" is
about the conversion path and not about some quiet moment elsewhere.

### state-lock-leaf

FT8 invariant 7: a state-lock holder needs nothing before it can let go. One
thread parks in the middle of a call, holding its lease and its receiver
guard. With it standing there, everything the state lock protects has to keep
working in other threads: wrapper creation, the parent graph, destruction. If
a transaction needed the parked thread's guard, or if a guard holder still
held the state lock, this would not come back - which is why it runs in a
subprocess with a timeout rather than trusting a join.

### no-leaked-lease

Invariants 9 and 10: every generated exit gives the lease back. The lease is
what holds the C++ destructor off, so one that survives its call would pin
the object for good and say nothing while doing it. Every shape of exit is
asked afterwards: the ordinary return, an argument that fails to convert, an
exception out of an override, a comparison, an attribute, and a method that
detaches around the native call - the detach suspends the guard, and the
lease has to outlive that.

### guard-vs-python-lock, guard-vs-annotated-lock

Two threads in opposite order: one holds a lock and then wants the receiver
guard, the other holds the guard and then wants the lock. Whether both come
back is the whole question. A wait that detaches suspends the receiver's
critical section and lets the other thread through; a wait that does not is
the deadlock a GIL build has for a method without `allow-thread`.

Invariant 8 seen from the outside: nothing may assume the receiver guard is
continuously held, and here it visibly is not. `QRecursiveMutex::lock()` is
annotated in `typesystem_core_common.xml`, so the generated code detaches
around it and the inversion resolves exactly as with a Python lock.

### guard-spans-native-wait

The documented boundary, measured instead of deadlocked. The two tests above
pass because their waits detach. A native call that blocks with the thread
attached does not, and neither does it reach a safe point where the runtime
could suspend it - so the guard is held for the whole wait and every other
thread reaching that receiver waits with it.

That is the deadlock a GIL build has for a method without `allow-thread`,
kept rather than removed, and this is where it shows. Written as a
measurement and not as a deliberate deadlock: the boundary is just as visible
in two seconds of waiting, and the test still ends. `ctypes.PyDLL` stands in
for the unannotated blocking method - it is the one way to call something
native from Python without letting go of the thread state.

With the GIL the measurement cannot tell the guard apart from the GIL, so
that row skips. The boundary holds there by construction; it is where it
comes from.

### qml-placement

FT8 finding 4 (B15-4): the placement context has to nest. QML constructs a
registered type into memory it allocated itself. The old code stored that
address in one thread-local slot behind a process-wide `QMutex` held across
`PyObject_CallObject()`: the mutex protected nothing another thread could
read, deadlocked a same-thread nested creation outright, and one slot cannot
hold two addresses.

The registered type creates another QObject before its own construction
finishes, which is what needs the addresses to nest. That inner object is of
a different type, and the type test on the address is what turns it away.

What the type test cannot turn away is a second object of the **same** type
built there before the awaited one; that one still takes the address. Telling
the two apart needs the address to travel with the object being constructed
rather than with the thread, which belongs to the wrapper-identity work.

Counterproof: `proof-qml-type` clears `QmlPlacementType` and the test
segfaults, because QML then holds the inner object.

### qml-placement-parallel

Two threads inside QML construction at the same time. It fails on the
revision before the fix by construction rather than by timing: the registered
type does not finish its `__init__` until the other thread has reached the
same point. With the `QMutex` still spanning `PyObject_CallObject()` the
second thread cannot enter `createInto()` while the first is in Python, the
first waits for the second, and the barrier times out.

Counterproof: `proof-qml-scope` clears `QmlPlacementFree`, which puts that
mutex back, and the test hangs until the runner kills it.

### qml-placement-unwinds

A guard, not a proof, and labelled as one: the placement context is popped by
a destructor, so it was popped on the old revision too and this test passes
there as well. What it holds is that the error path keeps working - the next
construction on the same thread gets its own address and its own object
rather than the one the failed construction left behind.

The registered type raises *after* `super().__init__()`, deliberately.
Raising before it leaves QML's memory unconstructed and QML then uses it;
that segfault is the caller's mistake and says nothing about the placement
context.

### makeValid() and referred objects - no test

The regress a review found in `makeValid()`. FT8 moved the walk under the
state lock and replaced `Object::checkType()` with a metatype identity test,
because the state lock has to stay a leaf and `PyType_IsSubtype()` reads
Python-owned type state. The two are not the same question: a type whose
metaclass merely derives from `SbkObjectType` - the ordinary result of
`class Meta(type(QObject), ABCMeta)` - passes the old test and fails the new
one. The walk is pruned there and everything below it stays invalidated.

The repair is the second half of FT8 design B: classify outside the lock, in
rounds, and revalidate the referred-map entry under it.

**There is no test here, and there cannot be one.** `makeValid()` has one
caller, `getOwnership()`; the generator emits that for a return value only
(`owner="target"`, and no typesystem in the tree puts it on an input
argument); and a return value is a fresh conversion from a C++ pointer. An
object is only invalid if `invalidate()` marked it, which it does only for a
wrapper it unregisters in the same transaction - so the conversion cannot
find that wrapper again, hands out a new and valid one, and `makeValid()`
returns at its first line. Measured as well as argued: over a full suite run
the two classifications never disagreed once.

The fix stays, because the code is wrong either way and the repair costs
nothing. What does not stay is a switch to turn it off: a bit no test can
observe is exactly the kind of dead mechanism this directory exists to
prevent.

### native-preflight, proof-native-preflight

B4-2: a virtual call can arrive from a Qt thread that has no Python thread
state at all. The preflight that asks "is this address wrapped?" used to
narrow by type first, and narrowing by type means reading `Py_TYPE` and
walking `tp_mro` - Python-owned state, read without a thread state. The
untyped question is an address comparison and needs none; the typed one
happens after the attach, in `acquireWrapper()`.

`proof-native-preflight` clears `NativePreflight` and the subject aborts.
What it aborts on is `SBK_ASSERT_ATTACHED()` inside the typed `hasWrapper()`,
so this counterproof discriminates through an assertion, and assertions are
compiled out under `NDEBUG`. On a free-threaded release build the A/B side
would do the unsafe read silently and the row would read "still passes". The
measure is real either way; what is debug-only is the ability to show it
here.

### MI offsets - no test, and why

The generated `mi_init()` used to fill a static array behind a sentinel, and
two threads reaching it together both sorted and moved the same array. No
failpoint can be placed there: it is generated code, and the generator emits
both sides rather than one with a hook in it. Nor does anything crash - the
threads that lose the race write the same offsets.

What carries `MiOffsetsOnce` instead is a sanitizer A/B: `stress.py
mi_first_instance` builds the first instance of every multiple-inheritance
type in the sample binding from eight threads at once, and TSan reports two
to six races in `Sbk_MDerived*_mi_init` with the bit cleared and none with it
set. That is weaker than a counterproof, and it is what the shape of the
defect allows. The developer documentation has the numbers.

### hierarchy-snapshot - a guard, and why it is only that

`addClassInheritance()` mutated the class graph with no lock while
`findDerivedType()` and `dumpTypeGraph()` were walking it. The repair: edges
are published as an immutable snapshot, a reader takes the snapshot under a
short lock and walks it with none held, because the traversal creates types
through `Module::get()` and calls generated discovery functions in the middle
of itself.

The test parks a traversal with one iterator alive - the failpoint
`hierarchy-mid-traversal` - and imports fourteen modules under it, each of
which publishes hundreds of edges. That makes the race deterministic rather
than a matter of scheduling.

It still cannot fail. Measured both ways: with the snapshot taken away the
same test passes four runs out of five and segfaults on the fifth, and with
the iterator parked it passes every time - libc++ keeps `unordered_map` nodes
alive across a rehash and relinks them, so the iteration survives an
invalidation that is undefined behaviour all the same. A one-in-five crash is
not a counterproof, and this file does not pretend otherwise: there is no
`proof-hierarchy`.

**TSan reports nothing here.** On the sanitizer tree, this test - the traversal
parked with a live iterator while four modules enter their edges - reports
nothing. That is what stands in for the counterproof this test cannot be.

Two things had to be fixed before the run said anything at all. Edges are
added by module init and by nothing else, so a run that imports no module
watches an idle map and passes either way; the list therefore includes the
shiboken test bindings, which a Core subset - what the sanitizer trees are -
does have. And the result line used to count the length of the wish list
rather than the imports that went through, which read as fourteen module
inits where there had been four.

### type-mutation

FT8 validation row "state lock": mutate a type's bases at a barrier.
`getDestructorFunctions()` walks `tp_bases` before the state-lock transaction
now, so the question is what can move between that walk and the commit.
CPython turns out to allow `__bases__` assignment on these types, and even
across layouts - a QObject subclass to a QTimer subclass - so the stability
does not come from CPython refusing.

What it does come from is the shape of the transaction: the list is taken
once, and the locked part only zips it with `cptr`. An immutable per-type
list published at type-ready time would make this an invariant instead of a
property of the code as written; that belongs with the identity and hierarchy
snapshots. Until then this is the guard rail that says the window stayed
harmless.

### lock-order

FT8 invariant 1: every raw lock has a rank, and the rank is kept.
`checkLockRank()` asserts it before every acquisition - a lock may only be
taken while holding locks that rank below it - so taking one the other way
round aborts a debug build here rather than deadlocking somewhere else later.

A rank violation therefore shows as a crash, not as a failure. What this test
compares is the other half: which pairs are held at once at all. The
inventory in `doc/developer/freethreading.md` names them, and a pair that is
not in it is a finding - a lock order nobody has argued for - not a detail to
print and move on from.

### lazy-lock-spans-destruction - expected FAIL

Open, and owned by the lazy protocol: B13-5 from the other end.
`Module::get()` holds the lazy-type mutex across `PyObject_GetAttr()`, so
arbitrary Python runs under it - and with it a refcount reaching zero, a
wrapper being destroyed, a deferred C++ destructor running. That last one is
what the state lock's own rule forbids for every other lock: a destructor
reaches Qt and user code, so a raw lock held across it deadlocks against
stop-the-world and against a re-entrant call.

Found by the assertion in `DeferredActions::run()` when two of the tests here
ran in the same process, which is why this one runs them rather than trying
to rebuild the state they leave behind. Neither of them reaches it alone: it
needs the wrappers the first one leaves for the collector and the type
incarnation the second one causes.

It no longer fires on either interpreter: a run that drops two hundred
wrappers into the collector and then walks six uncreated types records no
exception either. `Module::get()` still takes the mutex around the walk, so
the drivers changed, not the protocol - hence *skipped*, never ok. Making it
deterministic again needs a failpoint inside `Module::get()`, which belongs
with the replacement of that protocol.

Counted rather than asserted, because aborting on it would mean nobody can
run a debug build until the lazy protocol is replaced. Only the lazy line of
`contractExceptions()` is read: the wrapper-map exception is a different,
documented one, taken on every type-narrowed lookup, so counting it in here
would mean this test could never pass again.

### metaobject-commit-race, proof-metaobject-parse

B15-2. `addMetaMethod()` held the meta-object lock across the construction of
the instance `MetaObjectBuilder`, and constructing one parses the Python
type: attribute lookup on every class member, warnings, delayed enum
resolution. A raw lock held across that is the inversion the review
describes - a member with a custom `__getattribute__` runs application code
under it.

The parse moved out of the lock, which splits the operation into a lookup
that misses, a candidate built with no lock held, and a commit that publishes
one winner. That split is the new window this test is about: the parked
thread has built its candidate and is about to commit when the second one
runs the same path, builds its own and publishes first. The loser gives its
candidate back - the capsule owns it, so dropping the last reference frees it
below the lock - and continues with the winner's builder. Both signals have
to end up in one meta object, at different indexes.

`proof-metaobject-parse` clears `MetaObjectParseOutsideLock`. The parse then
goes back under the lock and `SBK_ASSERT_NO_RAW_LOCK()` at the top of
`parsePythonType()` aborts before the failpoint is reached at all. The abort
is the measurement: it says this path reaches the interpreter with a binding
raw lock held.

Debug builds only, and the reason is worth stating: `checkNoRawLock()` is
empty under `NDEBUG`, so a release build answers ok in both columns. The fix
works there, the proof does not - a green row in a release build says
nothing about this.

What is *not* shown here: that the inversion becomes a deadlock. That needs
the blocking-`__getattribute__` scenario the review names, and it is not
written. Nor is B15-3 touched - `metaBuilderFromDict()` still returns a
pointer nobody owns, and `PyObject_SetAttr()` still publishes the capsule
under the raw lock, because that is the transaction that picks the winner.
Taking the lifetime authority out of `__dict__` is what removes both.

`metaobject_lock.py` next to this file is the same question with one thread
and no failpoint: it is the `metaobject_lock` scenario in `run.py`, kept
because a single-threaded reproducer is worth more than a race when the
answer is an assertion.

### mro-snapshot-owns, mro-snapshot, proof-mro-snapshot

FT3. An assignment to `__bases__` replaces `tp_mro`, and owning a type does
not own the tuple. The walks in `getOverride()`, `methodGetAttr()`,
`find_name_in_mro()` and `callInheritedInit()` call back into Python while
they read it; `PepMroRef` holds one snapshot for the whole walk.

`mro-after-snapshot` parks a virtual in `getOverride()` between taking the
snapshot and walking it. `mro-snapshot-owns` checks the mechanism: the
parked walk holds a reference to `__mro__` that the finished walk gives
back.

`mro-snapshot` checks the window. It assigns `__bases__`, collects, and
allocates 2000 tuples of the same width whose entries carry the override
under its own name. A walk that reads the freed tuple takes the override
for an inherited default and does not call it; a walk into other memory
crashes. The test expects the override to run. The `gc.collect()` is
required: `set_tp_mro()` turns on deferred refcounting, and only the
tracing collector frees such a tuple.

`proof-mro-snapshot` clears `MroSnapshot` and expects `mro-snapshot` to
fail.

### bases-snapshot, proof-bases-snapshot

The same window on `tp_bases`, through `PepBasesRef`.
`bases-after-snapshot` parks `getFromType()`, which `QObject.property()`
reaches, between taking a type's bases and recursing into them. The test
assigns `__bases__` and allocates 2000 one-element tuples of a class
without the property; a bases tuple needs no collection. A walk that reads
them reports an invalid property rather than crashing. The test expects
the property's value; `proof-bases-snapshot` clears `MroSnapshot` and
expects the failure.

### shadowed-mro - no proof row

A metaclass can shadow `__mro__` with a property that builds a new tuple on
every access, held by nobody else. With `MroSnapshot` cleared the holder
goes back to a borrow, and it must not do that for such a tuple: the walk
would read freed memory, single-threaded, every time. The test calls
`tr()`, which walks the mro in `qObjectTr()`, 50 times on such a class and
expects the source text back. It first checks that `__mro__` really is
shadowed and built per access.

There is no `proof-*` row: no bit brings back the defect this test guards
against.
The instance is kept alive for the reason given under `metatype-subclass`.
Free-threaded builds only.

### metaclass-tuples - a guard, no proof row

A3: one metaclass answers `__mro__` with `(cls, 1, object)`, another
`__bases__` with `(cls,)`. `tr()` walks the first in `qObjectTr()`, and a
lookup of an inherited property walks the second in `getFromType()`, which
recurses over bases. Both must raise `TypeError`. Before, the first crashed
reading the name of an int as a type, and the second recursed until Python
stopped it with `RecursionError`. It runs in a child process, since a
regression crashes.
See "Walking a type's mro and bases" in the free-threading notes.

### signal-homonym - a guard, no proof row

A4: calling a signal instance calls the homonymous method of its class, found
in a class dictionary. The call parks at `signal-homonym-before-bind`, the
method found but not bound; the main thread replaces it in the class,
collects and allocates 20000 functions of the same size. The call must
answer with the method it found. Borrowed, it bound one of the new functions
in the freed memory. It runs in a child process, since a regression reads
freed memory.
See "Dictionary lookups own their result" in the free-threading notes.

### failed-override-lookup - no proof row

`getOverride()` answers nullptr both for "no override" and for a failed mro
lookup, and `Sbk_GetPyOverride()` caches "no override" per object for good.
A metaclass raises `MemoryError` from `__mro__` once, on the first virtual
call - armed only after the class and its instance exist, since creating
either reads `__mro__`. The test runs the virtual twice and expects the
override to have run. There is no bit. Free-threaded builds only.

### post-routine-owned - a guard, no proof row

A2: a worker registers a post routine and parks at
`post-routine-after-append`, right after the queue took it; the main thread
runs the batch with `QCoreApplication::shutdown()`. The reference count must
still cover the frame and the thread's argument tuple. Registered in the old
order, the runner released a reference the queue did not own yet and the
count fell below its holders. It runs in a child process, since the runner is
the application's teardown.
See "Post routines run from a batch" in the free-threading notes.

### post_routine_batch (run.py)

B16-2. A post routine registers another post routine. One thread and no
timing window, so it lives in `run.py`, like `metaobject_lock`. With
`PostRoutineBatch` the registration lands in the next batch and both
callbacks run. Cleared, the runner walks the live queue and the assertion
in `addPostRoutine()` aborts:

    PYSIDE6_OPTION_FT unset                   ->  ok
    PYSIDE6_OPTION_FT="~0x400000"             ->  CRASH(SIGABRT)

The abort shows that the path reaches a registration during the walk.
Whether the append would have moved the container on a given run depends
on QList's spare capacity; the assertion replaces that question.

Debug build only: `NDEBUG` removes the assertion, and `run.py` skips the
scenario there (`needs_contract`).

### post_routine_raises (run.py)

B16-2, the same bit: without the batch, a raising callback leaves its
exception pending for the next call. CPython's own assertion reports it:

    PYSIDE6_OPTION_FT unset                   ->  ok
    PYSIDE6_OPTION_FT="~0x400000"             ->  CRASH(SIGABRT)
        Assertion failed: (!_PyErr_Occurred(tstate)),
        function PyObject_CallObject, call.c

Debug build only: `NDEBUG` removes CPython's assertion. A release build
without the bit still mishandles the exception, silently.

### doc-recursion-per-thread, proof-doc-recursion

B16-5. `handle_doc()` suppresses the generated help text while it builds
one, and with the bit cleared the depth is one process-wide counter.
`doc-before-helptext` parks a thread with the depth raised, and a
second thread asks for the `__doc__` of another method. The test expects
the text the same question returns on a quiet process; with the shared
counter it gets the raw descriptor. A wrong string is not a crash, so the
test compares.

`proof-doc-recursion` clears `DocRecursionPerThread` and expects the
mismatch. Not covered: two threads losing an increment of the shared
counter.

### B16-3 - no test and no bit

Parking a thread between `QMetaType::fromName()` and the registration in
`createQObjectPtrMetaType()`, while a second thread registers the same
name, reproduces the defect without the lock, every time:

    FAIL: the thread that asked first lost the name - it carries 5
          methods, not 4

The locked path cannot be reached: the window is under the
registration lock, and `failpoint()` refuses to park while a lock is held.
A bit that no scenario can clear is not kept.
See "QObject-pointer metatypes" in the free-threading notes.

### method_receiver_dead (run.py)

B12-4, B14-4. `method_receiver_dead.py`, run by `run.py`, asks whether a
method slot delivers to a receiver that is gone. One thread and no
failpoint: connecting the same bound method twice gives both connections
one registry key, so the second row replaces the first while Qt keeps both.
The weakref callback removes the one row it finds, and the other connection
survives the receiver.

With `MethodReceiverUpgrade` the delivery upgrades the slot's weak
reference, finds nothing and makes no call. Cleared, it binds the raw
receiver pointer and the process dies on freed storage; a delivery that
survives counts as a failure too.

This shows the premise, a delivery binding a receiver it does not own, not
the two-thread race. The defect is not specific to free threading and
reproduces with a GIL. The orphaned connection itself is B14-5 and stays.

### receiver-dies-mid-delivery, proof-method-receiver-upgrade

B12-4 with the two-thread window. `method-receiver-before-bind` in
`MethodDynamicSlot::deliver()` parks a delivery between reading the
receiver and binding the descriptor; the thread that owns the receiver
then drops its last reference.

The test expects the receiver to be alive while the delivery waits, the
handler to run once, and the receiver to be gone after the call.
`proof-method-receiver-upgrade` clears `MethodReceiverUpgrade`: the delivery
holds a raw pointer, the drop deallocates, and the bind reads freed storage.

Each thread creates the object it is about. The receiver, because biased
reference counting makes the creating thread the owner, and a `del`
elsewhere would not deallocate. The sender, because a signal emitted from
another thread is queued and, with no event loop, never delivered.

### container-element-lease, proof-conversion-leases

An element of a container argument is deleted while the call runs: the call
leases an argument that is a wrapper, not the wrappers a list carries, and
each element's lease is taken inside its converter. `processEvent([parker,
victim], event)` on a `sample.ObjectType` calls `event()` on each element in
order; the parker's override waits while another thread calls
`Shiboken.delete(victim)`.

Expected: the delete is deferred while the parker waits, the victim's
`event()` runs on a live object, and the delete has run after the call.
`Shiboken.dump()` separates destroyed from claimed, `isValid()` does not.

`proof-conversion-leases` clears `ConversionLeasesKept`: the delete runs at
once and the parker is left on a daemon thread - released, the native loop
would call `event()` on freed memory.

### dealloc-waits-for-lease, proof-dealloc-claim

Dropping the last reference to a Python-owned parent runs its C++ destructor
from the deallocator, and that destructor deletes the children. A thread
holds a lease on a child through `Shiboken.VoidPtr(child)`, parked at
`lease-after-acquire`, and the main thread drops the parent. `VoidPtr` copies
the pointer and reads nothing behind it, so the run without the bit reports
rather than crashes.

Expected: `destroyed` of the child, connected directly, has not fired while
the lease is open, and fires once afterwards on the thread that released it.

`proof-dealloc-claim` clears `DeallocClaim`: the deallocator destroys the
owned set without looking, and `destroyed` fires under the open lease.

### dealloc-claim-survivor - a guard, no proof row

The deallocator's claim stamps the owned set as the binding graph has it, and
the graph can be wrong: `QQmlComponent.create()` parents the object on the
component, whose destructor leaves it alone. A `Placed` object has a C++
wrapper and survives with a valid one, so the stamp has to be taken back once
the destructor is past.

Both paths are asked: a component dropped with no lease open, where the
destructor runs in the deallocator, and one dropped while a `VoidPtr` lease on
the survivor is parked, where it runs from the release and has to be refused
while it waits, which shows it took that path. Expected: both survivors valid
and answering their name.

No `proof-*` row: the take-back has no bit, and clearing `DeallocClaim` drops
the waiting path with the stamp, so the test would fail because nothing was
refused - `dealloc-waits-for-lease`'s question, not this one.

### teardown-detach-edge, proof-detach-checked-parent

A child reparented in the middle of its parent's teardown. `killChild()`
deletes a Python-built `sample.ObjectType`, whose destructor detaches its
children in `_detachChildren()`. That thread parks at `detach-mid-round`,
a child picked; the main thread then moves the child to a new parent, in
C++ as well, so the destructor still to run leaves it alone.

Expected: the child's binding parent is the new one, read from
`Shiboken.dump()`. A `VoidPtr` lease on the child is then parked while
`Shiboken.delete()` destroys the new parent, and the delete has to wait.
Not covered: `runInvalidationPlan()`, the other site; it needs its own point.

`proof-detach-checked-parent` clears `DetachCheckedParent`: pick and removal
are two transactions with the point between them, and the removal takes the
new parent's edge. With the bit set the point sits after the single
transaction, where a reparent is harmless.

### constructor-tail-lease, proof-constructor-tail-lease

A generated constructor publishes the object and then still works on it, so
`Shiboken.delete()` can reach it from the commit on. A `QObject` subclass
puts `self` into a list and calls `super().__init__(tag=...)`, which
`fillQtProperties()` hands to its Python `setTag()`; the thread parks at
`ctor-after-publish` in `updateSourceObject()` and the main thread deletes
it. Not `objectName`, whose setter takes a lease the waiting delete refuses.

Expected: the delete is deferred while the constructor waits, the object is
alive inside `setTag()`, `__init__` completes, and it is destroyed after.

`proof-constructor-tail-lease` clears `ConstructorTailLease`: the delete runs
at once and the constructor stays parked on a daemon thread - released, the
setup would read `metaObject()` from freed memory.

