.. _developer-qtasyncio:

QtAsyncio developer notes
=========================

QtAsyncio is a module that provides integration between Qt and Python's
`asyncio`_ module. It allows you to run `asyncio` event loops in a Qt
application, and to use Qt APIs from `asyncio` coroutines.

.. _asyncio: https://docs.python.org/3/library/asyncio.html

As a pure Python module that integrates deeply with another Python
module, developing for QtAsyncio has some interesting aspects that
differ from other parts of Qt for Python.

QtAsyncio vs asyncio
--------------------

QtAsyncio has an interesting property from a developer perspective. As
one of its purposes is to be a transparent replacement to asyncio's own
event loop, for any given code that uses asyncio APIs, QtAsyncio will
(or should!) behave identically to asyncio. (Note that the reverse does
not apply if we also have Qt code). This is especially handy when
debugging, as one can run the asyncio code to compare and to check the
expected behavior. It also helps to debug both QtAsyncio and asyncio
step by step and compare the program flow to find where QtAsyncio might
go wrong (as far as their code differences allow). Often, one will also
be able to implement a unit test by asserting that QtAsyncio's output is
identical to asyncio's. (Note that a limitation to this is the fact that
Qt's event loop does not guarantee the order of execution of callbacks,
while asyncio does.)

The step function
-----------------

When debugging, a significant amount of time will likely be spent inside
the ``_step`` method of the ``QAsyncioTask`` class, as it is called
often and it is where coroutines are executed. You will find that it is
similar to asyncio's equivalent method, but with some differences. Read
the in-line comments carefully. Some variables and associated lines of
code might seem innocuous or even unnecessary, but provide important bug
fixes.

Keeping QtAsyncio in sync with asyncio
--------------------------------------

QtAsyncio implements `asyncio's API <https://docs.python.org/3/library/asyncio.html>`_,
which can change with new releases. As it is part of the standard
library, this lines up with new Python versions. It is therefore good
practice to check whether the API has changed for every new Python
version. This can include new classes or methods, changed signatures for
existing functions, deprecations or outright removals. For example,
event loop policies are expected to be deprecated with Python 3.13, with
subsequent removal in Python 3.15. This removal will in turn require a
small refactoring to make sure the ``QtAsyncio.run()`` function no
longer uses the policy mechanism.

asyncio developer guidance
--------------------------

asyncio's resources go beyond the pure API documentation. E.g., asyncio
provides its own `developer guidance <https://docs.python.org/3/library/asyncio-dev.html>`_
that is worth following when developing for QtAsyncio. In addition,
there is documentation for
`extending asyncio <https://docs.python.org/3/library/asyncio-extending.html>`_
that details a few essential points to keep in mind when building your
own event loop.
