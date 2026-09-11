# Deterministic lifetime races

The A/B harness in this directory reaches a race by repetition: it starts
threads and hopes they collide, which takes tens of runs to hit a window of a
few instructions once. `failpoints.py` arms a named point in libshiboken
instead, so the two threads meet in the order the test wants, every time. That
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

Three tests are expected to FAIL. They hold findings that belong to other
work packages; the day one of them passes, that package is done and the line
comes out of the registry.

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
and the referent must be dead when it does.

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

### metaobject-lifetime - expected FAIL, and not ours

Every QObject answers `metaObject()` with the same `&QObject::staticMetaObject`,
so the wrapper map holds one wrapper for it and hands that one to everybody.
Destroying any single QObject invalidates it and hits every other holder,
although the C++ object behind it is static and never dies.

Four lines, with a GIL, no threads:

    a, b = QObject(), QObject()
    ma = a.metaObject()
    Shiboken.delete(b)          # a stranger
    ma.className()              # RuntimeError: already deleted

Bisected to `4c1d56fb6` (29.07.2026, "Add a coarse lock for free-threaded
builds"), which moved the bookkeeping in `callCppDestructors()` ahead of the
C++ destructors. Before that, `~Wrapper() -> Object::destroy() ->
clearReferences()` had already taken the referred objects out by the time
`invalidate()` ran, so it found nothing to mark dead. Now it runs while they
are still attached.

The move itself is right and its reason is in the code: `ThreadStateSaver`
detaches the thread, which suspends the critical section, and a second thread
then destroys the same C++ object again. But it sits in **common** code with
a free-threading-only justification, so a GIL build gets the side effect and
none of the benefit. Not on dev, and not in this series either - the fix
belongs on the free-threading branch, where that commit lives.

Free threading only changes how often it is met: 139 of 600 without the GIL
against 3 of 600 with it.

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
ran in the same process, and it fires every time they do - which is why this
one runs them rather than trying to rebuild the state they leave behind.
Neither of them reaches it alone: it needs the wrappers the first one leaves
for the collector and the type incarnation the second one causes.

Counted rather than asserted, because aborting on it would mean nobody can
run a debug build until the lazy protocol is replaced. Only the lazy line of
`contractExceptions()` is read: the wrapper-map exception is a different,
documented one, taken on every type-narrowed lookup, so counting it in here
would mean this test could never pass again.

### metaobject-lifetime - expected FAIL

Open: `metaObject()` hands out a wrapper it does not keep alive. Found while
driving the lock-order test. Four threads doing nothing but
`metaObject().className()` on their own objects, and three of them get
"Internal C++ object (QMetaObject) already deleted". Measured on the same
binary: 3 errors free-threaded, 0 with `PYTHON_GIL=1`, 0 on traditional
CPython - so it is not an old bug that free-threading happens to show, it is
one free-threading introduces.

`retrieveMetaObjectForCppObject()` returns a `QMetaObject *` whose wrapper
reference is dropped by the same line; with a GIL nothing runs between the
drop and the use. It is a lifetime question about a returned wrapper, so it
belongs with the lease work rather than here, and this test holds the finding
until then.
