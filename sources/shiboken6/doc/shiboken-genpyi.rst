.. _shiboken6-genpyi:

shiboken6-genpyi
================

`shiboken6-genpyi` is a command line tool to generate Python stub files
(.pyi) for any shiboken binding-based module (not just PySide). Stub
files define signatures of all classes, methods (including overloads),
constants and enums of a module. Signatures also contain type hints.
This helps your module integrate with Python type checkers and IDEs.
For example, if you use any function from your module, your IDE's
function lookup feature will show you the function signature and its
parameters and return value including types.


Usage
-----

To generate stub files for a module, run the following command:

.. code-block:: bash

    shiboken6-genpyi <module_names> [OPTIONS]

where `<module_names>` is a space-separated list of module names (the
modules must be importable from the working directory) and where
`[OPTIONS]` can be one of the following:

* **--quiet**: Run the tool quietly without output to stdout.
* **--outpath <output_dir>**: Specify the output directory for the
  generated stub files. If not specified, the stub files are generated
  in the location of the module binary.
