Qt Quick Examples - Window and Screen
=====================================

This example demonstrates the Window and Screen types in QML.

.. image:: window.png
   :width: 392
   :alt: Window and Screen screenshot

In addition, this example demonstrates the usage of the Qt Resource System in
Qt for Python for more advanced scenarios. There are several QML files, one of
which imports a module from this sibling directory. Both this "shared" module
and the QML files of the example need to be compiled into Python modules with
the resource compiler rcc.

For the "shared" module approach to work with QML and rcc, you need:

* A module definition *qmldir* file
* A Qt Resource Collection file (.qrc) specifying all the QML files and other
  resources, plus the *qmldir* file

The .qrc file is the input to rcc. This will generate a Python module (called
*shared_rc* here) that can then be imported from the Python code. At runtime,
only this Python module is needed, not the .qrc file or any of the .qml files
or even the image resources, as they have all been compiled into the Python
module.

For the example, rcc needs:

* A Qt Resource Collection file (.qrc) specifying all the QML files and other
  resources. There is no qmldir file here because this is not a module.

This will generate a Python module (called *window_rc* here) that can then be
imported from the Python code. Again, only the Python module is needed at
runtime.
