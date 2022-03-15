The Qt Concurrent module contains functionality to support concurrent execution
of program code.

The Qt Concurrent module provides high-level APIs that make it possible to
write multi-threaded programs without using low-level threading primitives such
as mutexes, read-write locks, wait conditions, or semaphores. Programs written
with Qt Concurrent automatically adjust the number of threads used according to
the number of processor cores available. This means that applications written
today will continue to scale when deployed on multi-core systems in the future.

Qt Concurrent includes functional programming style APIs for parallel list
processing, including a MapReduce and FilterReduce implementation for
shared-memory (non-distributed) systems, and classes for managing asynchronous
computations in GUI applications:

    * :class:`QFuture<PySide6.QtCore.QFuture>` represents the result of an
      asynchronous computation.
    * :class:`QFutureIterator<~.QFutureIterator>` allows iterating through results
      available via :class:`QFuture<PySide6.QtCore.QFuture>` .
    * :class:`QFutureWatcher<PySide6.QtCore.QFutureWatcher>` allows monitoring a
      :class:`QFuture<PySide6.QtCore.QFuture>` using signals-and-slots.
    * :class:`QFutureSynchronizer<~.QFutureSynchronizer>` is a convenience class
      that automatically synchronizes several QFutures.
    * :class:`QPromise<~.QPromise>` provides a way to report progress and results
      of the asynchronous computation to :class:`QFuture<PySide6.QtCore.QFuture>` .
      Allows suspending or canceling the task when requested by
      :class:`QFuture<PySide6.QtCore.QFuture>` .

Using the Module
^^^^^^^^^^^^^^^^

To include the definitions of modules classes, use the following
directive:

::

    import PySide6.QtConcurrent
