# Free-Threaded Python (PEP 703)

On a free-threaded build (`Py_GIL_DISABLED`) the interpreter no longer
serializes Python execution, so several threads can enter the bindings at the
same time. The binding layer keeps per-object bookkeeping - ownership and
validity flags, the parent/child graph, the wrapper lifecycle, the signal
connection tables - which was previously protected by the GIL and by nothing
else.

Shiboken replaces that protection with one process-wide lock, the *object
graph guard*. This document describes what it does, what it deliberately does
not do, and what that means for application code.

## The object graph guard

The guard is injected at the entry of every generated method wrapper and taken
explicitly in the hand-written paths that reach the same state. It is one
lock for the whole graph rather than one per container, because the guarded
paths call into each other; a hierarchy of finer locks would need a lock order
that the binding cannot state for Qt and for application code.

The lock is not taken directly. It is entered through a Python critical
section, which gives it the release behaviour of the GIL rather than only its
exclusion behaviour:

* whenever the holding thread detaches - an `allow-thread` region, a
  destructor, blocking on a `threading.Lock`, a queue, an import - the
  runtime suspends the section and releases the lock, and resumes it when the
  thread reattaches;
* a nested guard on the same thread suspends the outer section and reacquires,
  so the guard is reentrant without a hand-maintained counter;
* a thread waiting for a contended guard is detached, so waiting here never
  prevents a stop-the-world pause from completing.

The practical effect is that anything the runtime can see - Python locks,
imports, queue and event waits, thread-state transitions - cannot deadlock
against the guard. A raw mutex held across those waits would.

## What this does not give you

Qt itself does not become thread-safe. The guard protects the *binding's*
bookkeeping, not the objects it wraps. Qt's thread affinity rules and the
per-class thread-safety documentation continue to apply unchanged: a QWidget
still belongs to the GUI thread, and a QObject still may not be used from two
threads just because Python allows it.

The intended shape of a free-threaded application is therefore the same one
that worked before: keep the GUI on one thread, do the parallel work in
threads that do not touch Qt objects, and hand results over at a controlled
point.

## Residual deadlock classes

Three classes remain. All three exist on GIL-enabled builds as well, which is
the bar this design is measured against: it does not make an existing program
less safe, and it does not claim to be deadlock-free.

**Waits the runtime cannot see.** A wait that does not detach the thread keeps
the critical section active. A Qt mutex, a `std::mutex`, a condition wait or
blocking I/O reached from C++ beneath a wrapper are all of that kind. This is
exactly what the GIL does too - it is held across any C++ call that is not
annotated `allow-thread`. It cannot be closed by adding annotations: an
ordinary internal mutex acquisition is a potentially blocking operation, and
establishing that property would require auditing the implementation and the
transitive callees of every wrapped method, for every future Qt version.

A caller can also construct the cycle without any callback into Python, by
holding a lock that Qt deliberately exposes:

```
thread A: QMutex.lock() - the wrapper returns while A still owns the lock
thread B: enters a wrapper, takes the guard, calls C++ that wants that lock
thread A: enters any wrapper and waits for the guard
```

Avoiding this requires a process-wide rule - no thread may enter the bindings
while holding a lock that C++ beneath another wrapper might take - which the
bindings can neither state nor enforce for Qt, application code and other
extensions.

**Contended acquisition beneath an external C++ lock.** A thread that detaches
while entering a wrapper below an untracked lock, together with a second
thread that blocks on that lock without detaching, can stall a stop-the-world
pause. This is CPython issue 149162, demonstrated by static initialization in
other extensions. Detaching is required to avoid one variant and forbidden to
avoid the other, and the correct choice depends on locks held by callers,
which is not knowable at wrapper entry.

**Weaker atomicity than the GIL.** Contended per-object critical sections can
suspend the guard where a GIL build would not have switched threads. Code that
touches Python containers between two C++ operations therefore gets slightly
weaker atomicity than it did before.

## One-time initialization is not covered

The guard serializes access to the object graph, but it is suspended whenever
the holding thread calls back into Python. Any state that is built lazily and
calls into Python while building therefore needs its own serialization: the
guard is not held across the part that matters.

Lazy type creation is such a case. A type is incarnated on first attribute
access, from whichever thread happens to need it first, and building it
creates enum types through Python. It is serialized by a separate recursive
lock (clearing its `PYSIDE6_OPTION_FT` bit takes it away for the A/B proof), entered with the
thread detached so that a waiting thread holds nothing. Similar one-time
initializations should follow that pattern rather than rely on the guard.

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

Clearing its `PYSIDE6_OPTION_FT` bit disables the guard. It exists for stress testing - it is
what makes the A/B comparison possible that shows the object graph racing
without the lock - and it is not a supported production setting: the modules
still declare that they do not need the GIL, while the synchronization backing
that declaration is gone. Taking the declaration back at runtime is not
possible, because the GIL slot is evaluated when the module object is created,
before any binding code runs. Disabling the guard therefore warns instead.

## Testing

Free-threading specific tests skip themselves unless the GIL is actually
disabled. Two are worth knowing about:

`sources/shiboken6/tests/samplebinding/free_threading_stress_test.py`
: hammers the shared parent graph, reparenting and racing wrapper deletion.
  Without that bit it crashes, which is what makes it evidence.

`sources/pyside6/tests/pysidetest/signal_slot_lock_inversion_test.py`
: drives the classic AB-BA shape: a thread holding a Python lock enters a
  wrapper while another thread holds the guard and calls back into Python. It
  runs in a subprocess with a hard timeout, so a regression fails the test
  instead of hanging the suite.

Deadlock tests belong in subprocesses for that reason. Passing race stress
tests shows protection against the races they exercise; it does not show
deadlock freedom, which needs targeted tests and an argument about lock scope.

A passing test also only shows one half of the argument: that the code
survives, not that the synchronization is what makes it survive. The other
half needs the locks switched off, which produces crashing processes and
therefore cannot be part of the automatic suite. It lives in
`sources/pyside6/tests/manually/freethreading/run.py`, which runs each
scenario twice, with and without the lock it depends on:

```
scenario        unlocked    locked
shared_parent   10CRASH/10  ok/10
reparent        10CRASH/10  ok/10
shared_delete   10CRASH/10  ok/10
lazy_types      2CRASH/10   ok/10
```

Run it with the free-threaded interpreter; `REPEATS`, `STRESS_THREADS` and
`STRESS_ITERS` size the run, and naming scenarios restricts it.
