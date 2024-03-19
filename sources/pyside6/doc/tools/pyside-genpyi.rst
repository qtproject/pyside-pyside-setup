.. _pyside6-genpyi:

pyside6-genpyi
==============

`pyside6-genpyi` is a command line tool to generate Python stub files
(.pyi) for PySide modules. Stub files define signatures of all classes,
methods (including overloads), constants and enums of the PySide
modules. Signatures also contain type hints. This helps PySide integrate
with Python type checkers and IDEs. For example, if you use any function
from the Qt API with PySide, your IDE's function lookup feature will
show you the function signature and its parameters and return value
including types.

PySide6 already ships with stub files that were generated with
`pyside6-genpyi`. However, if you want to generate new stub files for
several (or all) modules, for example to toggle a few features, you can
run `pyside6-genpyi` manually. If you want to generate stub files for
your own custom module, refer to :ref:`shiboken6-genpyi`.


Usage
-----

To generate stub files for a PySide module, run the following command:

.. code-block:: bash

    pyside6-genpyi <module_names> [OPTIONS]

where `<module_names>` is a space-separated list of module names (the
modules must be importable from the working directory) and where
`[OPTIONS]` can be one of the following:

* **--quiet**: Run the tool quietly without output to stdout.
* **--outpath <output_dir>**: Specify the output directory for the
  generated stub files. If not specified, the stub files are generated
  in the location of the module binary.
* **--sys-path <paths>**: Prepend the system path (`sys.path`) with a
  space-separated list of strings `<paths>`. This is useful if the
  module is not installed in a default lookup location.
* **--feature <features>**: A space-separate list of optional PySide
  features to enable (see :ref:`pysideapi2`). This option has no effect
  when using PyPy. Currently, the following features are available:

  * **snake_case**: All methods in the module are switched from
    ``camelCase`` to ``snake_case``. A single upper case letter is
    replaced by an underscore and the lower case letter.
  * **true_property**: All getter and setter functions in the module
    which are marked as a property in the Qt6 docs are replaced by Python
    property objects. Properties are also listed as such in the according
    QMetaObject of a class.
