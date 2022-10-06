Async examples
==============

The Python language provides keywords for asynchronous operations, i.e.,
"async" to define coroutines or "await" to schedule asynchronous calls in the
event loop (see `PEP 492 <https://peps.python.org/pep-0492/>`_). It is up to
packages to implement an event loop, support for these keywords, and more.

The best-known package for this is `asyncio`. Since both an async package and
Qt itself work with event loops, special care must be taken to ensure that both
event loops work with each other. asyncio offers a function `stop` that allows
stopping an event loop without closing it. If it is called while a loop is
running through `run_forever`, the loop will run the current batch of callbacks
and then exit. New callbacks wil be scheduled the next time `run_forever` is
called.

This approach is highly experimental and does not represent the state of the
art of integrating Qt with asyncio. Instead it should rather be regarded more
as a proof of concept to contrast asyncio with other async packages such as
`trio`, which offers a dedicated `low-level API
<https://trio.readthedocs.io/en/stable/reference-lowlevel.html>`_ for more
complicated use cases such as this. Specifically, there exists a function
`start_guest_run` that enables running the Trio event loop as a "guest" inside
another event loop - Qt's in our case.

Based on this functionality, two examples for async usage with Qt have been
implemented: `eratosthenes` and `minimal`:

.. image:: minimal.png
   :alt: Async example: Minimal

* `eratosthenes` is a more extensive example that visualizes the Sieve of
  Eratosthenes algorithm. This algorithm per se is not one that is particularly
  suitable for asynchronous operations as it's not I/O-heavy, but synchronizing
  coroutines to a configurable tick allows for a good visualization.
* `minimal` is a minimal example featuring a button that triggers an
  asynchronous coroutine with a sleep. It is designed to highlight which
  boilerplate code is essential for an async program with Qt and offers a
  starting point for more complex programs.

Both examples feature:

1. A window class.
2. An `AsyncHelper` class containing `start_guest_run` plus helpers and
   callbacks necessary for its invocation. The entry point for the Trio/asyncio
   guest run is provided as an argument from outside, which can be any async
   function.

While `eratosthenes` offloads the asynchronous logic that will run in
trio's/asyncio's event loop into a separate class, `minimal` demonstrates that
async functions can be integrated into any class, including subclasses of Qt
classes.
