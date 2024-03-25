.. _developer-adapt-qt:

Adapt to new Qt versions
========================

Adapting to source changes
--------------------------

The dev branch of PySide is switched to a new Qt minor version
after its API review is finished and the API is stable.

Until that happens, a patch should be continuously developed
to adapt to this version.

The `new classes page <https://doc-snapshots.qt.io/qt6-6.7/newclasses67.html>`_
is a good source of information for new API.

New classes and should be added to the type system file (using
a ``since`` attribute) and ``CMakeList.txt`` file of the respective module.

Should the class not be available on all platforms, the respective
``QT_CONFIG`` macro needs to be specified in the type system file and
feature checks need to be added to ``CMakeList.txt`` (see for example
``QPermission``).

The process consists of running a build and evaluating the log file.
The script
`shiboken2tasks.py <https://code.qt.io/cgit/qt-creator/qt-creator.git/tree/scripts/shiboken2tasks.py>`_
from the *Qt Creator* repository can be used to convert the shiboken warnings
into a `task file <https://doc.qt.io/qtcreator/creator-task-lists.html>`_
for display in the build issues pane of *Qt Creator*.

Warnings about new enumerations will be shown there; they should be added
to type system file using a ``since`` attribute.

Warnings about not finding a function signature for modification
also need to be handled; mostly this is a sign of a function parameter
being changed from ``int`` to ``qsizetype`` or similar.

If the build succeeds, a test run should be done.

The Qt source code should be checked for new overloads
(indicated by ``QT6_DECL_NEW_OVERLOAD_TAIL`` starting from 6.7).
The resolution needs to be decided for each individual case,
mostly by removing old functions and using ``<declare-function>``
to declare new API.

Bumping the version
-------------------

To instruct ``COIN`` to use the next version of Qt, adapt the files
``coin/dependencies.yaml`` and/or ``product_dependencies.yaml`` accordingly.
Next, the wheel names should be changed by adapting
``sources/shiboken6/.cmake.conf`` and ``sources/pyside6/.cmake.conf``.
