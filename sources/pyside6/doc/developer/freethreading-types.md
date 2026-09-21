# Free Threading: Types and Shared State

The type side and the process-wide state: parent information, the class
hierarchy, type walks and dictionary lookups, caches, and the globals the
bindings keep.

Part of the free-threading notes. [The overview](freethreading.md) has the
state lock, the call guard and the leases these sections build on.

## Who may read parentInfo

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
the children and the referred objects under the lock, so neither may be called
while holding it. `shiboken6.dumpTree()` would have to format each child with
the lock released, and raises `NotImplementedError` instead.

`tp_traverse()` keeps its plain reads, because the collector stops the world
around them.

There is no bit: the readers were saving a lock acquisition, not trading a
guarantee. No failpoint test carries this - the defect is a data race with no
divergent outcome to observe, so TSan is what shows it.

## The class hierarchy publishes snapshots

`addClassInheritance()` mutated the graph under no lock while
`findDerivedType()` and `dumpTypeGraph()` were walking it (B4-4). A lock
around both ends is not available here: the traversal creates types through
`Module::get()` and calls generated discovery functions in the middle of
itself, so it runs arbitrary Python and cannot hold one.

The edges are immutable instead. A writer copies the map and publishes the
copy; a reader takes the current snapshot under a short lock and walks it
with none held. What a traversal sees is therefore one graph from beginning
to end, even when a module publishes hundreds of edges underneath it. The
lock is `ClassHierarchy`, rank 2, and
[the inventory](freethreading.md#the-complete-inventory) says what may be
held across it.

A module hands its edges over as one table for the same reason the snapshot
exists: publishing copies the map, so one call per edge copied it once per
edge.
The generated `initInheritance()` calls `addClassInheritance()` once.

There is no counter-proof. `hierarchy-snapshot` parks a traversal with one
iterator alive and imports fourteen modules under it, which makes the race
deterministic - but with the snapshot taken away it still passes four runs
out of five, because libc++ keeps `unordered_map` nodes alive across a
rehash. A one-in-five crash is not a proof, and the test says so.

## MI offsets have one owner

A type with more than one C++ base is registered under one address per base,
and the generated `mi_init()` computes those offsets. It used to fill a
static array behind a sentinel check: two threads reaching it together both
saw the sentinel, and both sorted, uniqued and `memmove`d the same array
(B4-3). The initializer of a function-local static does that exactly once,
whoever arrives, and that is what the generator emits now.

The offsets were also cached in the type, filled by whichever registration
came first and copied into every Python subclass on every constructor call -
three writers to type state that readers walk without a lock. There is
nothing to cache: `mi_init()` computes on its first call and hands out the
same array afterwards, so the aliases are asked of `miOffsets()` where they
are used. `SbkObjectTypePrivate::mi_offsets` is gone.

The offsets are a property of the layout, not of an instance. Virtual
inheritance is not modelled by them and is not supported.

There is no deterministic test for this one, and there cannot be: the race is
inside generated code, where a failpoint cannot be placed, and the threads
that lose it all write the same offsets, so nothing crashes either way. A
sanitizer carries it instead, and for that both sides have to exist: the
generator emits the sentinel version as well, behind `MiOffsetsOnce`, and
`stress.py mi_first_instance` builds the first instance of every
multiple-inheritance type from eight threads at once. With the bit cleared
TSan has a race to report there, with it set none - weaker than a
counter-proof, and what the shape of the defect allows.

Bit `MiOffsetsOnce`; cleared, the sentinel check is back, which two threads
reaching the type first can pass together, and that sanitizer A/B is the
evidence rather than a counter-proof.

## Function-local statics whose initializer calls Python

A C++ function-local static has a compiler-generated guard, and a second
thread blocks in it while the first initializes. Where that initialization
calls Python, the guard is a raw lock across Python by another name. The
audit found these classes:

- **Interned strings**, the large majority. `createStaticString()` statics
  are spread over the tree; `STATIC_STRING_IMPL()` is confined to
  `sbkstaticstrings.cpp` and `pysidestaticstrings.cpp`; and
  `getDataFromKwArgs()` in `pysideproperty.cpp` interns without either. Each
  interns one string once - bounded, no user code, no callback; kept.
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

## Post routines run from a batch

`qAddPostRoutine()` queues callbacks from any thread, and they run at Qt's
teardown or in `QCoreApplication::shutdown()` (B16-2). A runner that walks
the live queue lets a callback append under the iterator, and a raising
callback leaves its exception pending for the next call.

The runner takes the pending callbacks out as a batch under a short
lock and calls them with no lock held: a Python call under a raw lock
deadlocks against stop-the-world. Registrations made meanwhile go into the
next batch, and the loop ends on an empty one. A raised exception is
reported through `PyErr_WriteUnraisable()` and the batch goes on. A
registration owns its callback before it publishes it: a runner may take
the batch and release that reference as soon as the lock is gone.

The loop stops after 1024 batches per run. A routine that re-registers
itself would otherwise hang shutdown, and a build with a GIL has no other
path.
What is left after the limit is reported and released, not run.

Bit `PostRoutineBatch`; cleared, the runner walks the live queue, and a
debug build asserts on a registration during the walk.

## QObject-pointer metatypes

`createQObjectPtrMetaType()` asks `QMetaType::fromName()` whether the
pointer name is taken and registers an interface if not (B16-3). Two
threads registering the same name can both get "not taken". Qt does not reject
the second registration: `registerCustomType()` in `qmetatype.cpp` finds the
name among its aliases, stores the existing id into the new interface and
returns it. The caller gets a valid `QMetaType` whose meta-object is the
other class's, with no error. This applies to any code registering custom
metatypes by name from more than one thread.

The question and the registration run under one lock. It is a leaf and
held across `QMetaType::id()`: a lock of ours reached from Qt's
registration aborts a debug build instead of deadlocking. Qt's own locks
are outside the ranks; for those the claim is that Qt's registration never
calls back into `createQObjectPtrMetaType()`.

The meta-object sits in a record next to the interface, and the record is
never freed. `metaObjectFunc()` reads it through the interface pointer Qt
hands back, so a Qt callback reads nothing another thread inserts.

There is no bit and no test for the lock: a failpoint in the window would
park under the lock, which `failpoint()` refuses. Making it testable means
taking `QMetaType::id()` out of the lock, which belongs to FT9.

## Documentation recursion

`handle_doc()` suppresses the generated help text while it builds one,
because `make_helptext()` asks the object for its own `__doc__` (B16-5).
With one process-wide counter, a thread asking for an unrelated `__doc__`
while another builds help text gets the raw descriptor, and two threads
losing an increment can leave it nonzero for good. The depth is per thread
in the free-threaded build. A build with a GIL keeps its one counter,
although `make_helptext()` runs Python and can switch threads there too.
The globals the signature bootstrap publishes (B16-1) are not covered.

Bit `DocRecursionPerThread`; cleared, the shared counter is back, and
`proof-doc-recursion` expects the mismatch it produces.

## Parsing a Python type happens outside the lock

`addMetaMethod()` held the meta-object lock across the construction of the
instance `MetaObjectBuilder`, and building one parses the Python type:
attribute lookup on every class member, warnings, delayed enum resolution
(B15-2). A member with a custom `__getattribute__` then runs application
code under a raw binding lock, which is the inversion the lock contract
forbids.

The parse happens with no binding lock held, which splits the operation into
a lookup that misses, a candidate built unlocked, and a commit that publishes
one winner. The loser gives its candidate back - the capsule owns it, so the
last reference frees it below the lock - and continues with the winner's
builder, so both signals end up in one meta object at different indexes.

Bit `MetaObjectParseOutsideLock`; cleared, the parse goes back under the lock
and `proof-metaobject-parse` aborts in `SBK_ASSERT_NO_RAW_LOCK()` at the top
of `parsePythonType()`. That abort is the measurement, and it is debug-only:
`checkNoRawLock()` is empty under `NDEBUG`, so a release build answers ok
either way.

## The two caches on a virtual call

A generated virtual override caches two things: the name of the Python method
to look for, in a function-local `nameCache[2]`, and the override it found, in
`m_PyMethodCache[i]` on the wrapper instance. Both were plain pointers written
by whichever thread reached the virtual first, and read by all the others.

The value is never wrong. Every thread computes the same name and finds the
same override, so a lost race costs a reference and not correctness: only the
pointer that ends up in the slot is ever owned by anybody, and the names come
from `PyUnicode_InternFromString()`, which hands out a new reference on every
call. What it also costs is a data race that a sanitizer reports on every
single run, which is the kind of noise a real finding hides in.

`Shiboken::CacheSlot` is the replacement: one pointer, `get()`, `publish()`
and `reset()`. Under free threading it is a `std::atomic<PyObject *>` with a
compare-exchange, and `publish()` returns what the slot holds afterwards and
drops the reference that lost. With a GIL it is the plain pointer it always
was. It is the size and alignment of the pointer it replaces, and a
`static_assert` says so.

There is no bit and no counter-proof for this one, and there should not be: it
takes nothing away and adds no window. What it fixes is a reference leak no
test can see and sanitizer noise only a sanitizer can, so a sanitizer is what
says whether it worked: no report names `overrideMethodName()`,
`Sbk_GetPyOverride()` or either cache slot any more. What the same run still
reports belongs to the feature system, which is FT2 and not this.

## Walking a type's mro and bases

An assignment to `__bases__` replaces `tp_mro` and `tp_bases`, and owning a
type does not own the tuples. A walk that borrows one and calls back into
Python before it is done - `PepType_GetDict()`, a dict lookup,
`PyObject_GetAttr()` - can read a tuple another thread has released.
`PepMroRef` and `PepBasesRef` hold an owned snapshot for the walk (FT3).

The snapshot comes from `PyObject_GetAttr()`, not from the field:
`set_tp_bases()` stores under the type lock without stopping the world and
`set_tp_mro()` stops it only from 3.14 on, so loading the field and then
incrementing races the writer's decrement. `_PyType_GetBases()` takes the
type lock around those two steps, and the attribute is how an extension gets
the same. The price is that a metaclass answers: it can raise or return
something that is not a tuple, so a null snapshot carries an exception, and a
caller with no error channel stores it. The same holds for a tuple whose items
are not types, or a `__bases__` that names the type itself: every walk takes
the items for types, and the one over bases recurses.

No raw binding lock may be held around a holder. The lookup can run
Python, and releasing a bases tuple can free the types in it. An mro tuple
is freed only by the tracing collector from 3.14 on, because `set_tp_mro()`
turns on deferred refcounting; on 3.13t it falls like any other tuple. The
holder asserts on both ends.

A failed lookup makes `getOverride()` answer nullptr, as "no override"
does, and `Sbk_GetPyOverride()` caches that answer for the object's
lifetime. It caches only when no error is set.

Bit `MroSnapshot`; cleared, a walk borrows the type's own tuple again. A
tuple a metaclass builds per access stays owned, since nothing else holds
it. Cleared, `find_name_in_mro()` borrows as well, which no release did,
and `proof-mro-snapshot` and `proof-bases-snapshot` walk into both.

## Walks that are not converted

| Where | Why |
|---|---|
| `walkThroughBases()`, `isDirectAncestor()` | shiboken's own graph walks; converting them needs its own measurement. `walkThroughBases()` asserts that the state lock is not held |
| `dynamicqmetaobject.cpp` | the dynamic meta object, FT10 |
| `feature_select.cpp`, `sbkfeature_base.cpp` | the feature system, FT2. Still compiled into free-threaded builds, and `lookupUnqualifiedOrOldEnum()` walks `tp_mro` on every failed attribute lookup on a Qt class |
| `helper.cpp` | diagnostics, FT12 |
| `pep384impl.cpp` | the startup probe, before a second thread exists |
| `sbktypefactory.cpp` | writes the fields while the type is created |
| `resolveMetaType()` | reads `tp_base`, the third field `__bases__` replaces, bare. Reached only for a type without bases, which an initialized type never is |

## Dictionary lookups own their result

`PyDict_GetItem()` and `PyDict_GetItemString()` return a borrowed value.
With the GIL nothing runs between the lookup and the caller's incref;
without it another thread can remove the entry and release the value in
that gap. The same holds for `PyDict_Next()`: its key and value are borrowed
from a dict another thread can change, and a loop body that calls Python
releases a critical section on the dict, so a section alone does not help.

`PepDict_GetItemOwned()` and `PepDict_GetItemStringOwned()` return a new
reference, through `PyDict_GetItemRef()` on a free-threaded build; they
suppress errors and keep a pending exception, as the borrowed calls do.
`PepDict_IterationSnapshot()` hands a loop a private copy on a free-threaded
build and the dict itself otherwise. Type and instance dictionaries,
`sys.modules`, module globals and dicts handed in by the caller take these
paths, the generated `getattro` and the dict converter templates included.
A dict private to the call, such as its keyword arguments, keeps the plain
API. A signal call owns the homonymous method it found until it is bound.
That list is what was converted, not a claim about every
borrowed lookup: `find_name_in_mro()` still returns one out of a type dict,
and the `__feature__` code is left as it is (FT2).

There is no option bit: the owned form only closes a gap, it trades nothing.

## A failed type function stops there

A generated type function that fails answers nullptr with an error set.
Every step after it took the answer as a type: `incarnateHelper()` and
`incarnateType()` incremented it, `getEnclosingObject()` asserted on it and a
release build walked on with nullptr, and the attribute walk in
`Module::get()` looked the next name up on it. All of that sits on the
import path, so the failure ends startup either way - what must not happen is
that a crash replaces the report.

Under free threading each of these stops on nullptr and leaves the error set.
`incarnateType()` restores the feature switch it turned off for the call, as
its normal exit does, and when a subtype failed it reports that error rather
than hand out the main type with an exception pending.

That is the entry side of B13-2. Whether a failed initializer may leave a
readiness flag, a half-built type or a dropped subtype entry behind, and what
a retry then sees, belongs to the lazy machinery and is not settled here.

There is no bit: not dereferencing a null answer trades against nothing, and
a counter-proof would have to make a generated type function fail.

## A virtual dispatch owns the override it found

`getOverride()` looked the method up, took what `PyMethod_Function()` or the
compiled-method attribute gave it - both borrowed - and let the bound method
go at the return. After that the callable hung on the class dictionary alone,
and the one caller treats it as owned: it releases it when an error is
pending, which drops a reference nobody took.

The walk between the lookup and the return runs Python, so the reference has
to be taken where the callable is found, not where it is handed out. Under
free threading the two branches own what they found, an `AutoDecRef` carries
it across the mro walk, and each return hands the caller a reference of its
own. The caller is then right as it stands: it releases on the error path,
and the reference it takes for `publish()` is the one that keeps the override
alive across the call.

There is no bit: owning what you return is not a trade against anything.
There is no guard test either, although the window can be reached: the
walk parks at `mro-after-snapshot`, which `proof-mro-snapshot` uses, and
another thread could replace the method in the class there.
