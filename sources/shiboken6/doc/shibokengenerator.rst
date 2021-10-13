.. _gen-overview:

******************
Generator Overview
******************

The following diagram summarizes Shiboken's role in the Qt for Python
project.

.. image:: images/qtforpython-underthehood.png

An XML typesystem file is used to specify the types to be exposed to Python
and to apply modifications to properly represent and manipulate the types in
the Python World. For example, you can remove and add methods to certain types,
and also modify the arguments of each method. These actions are inevitable to
properly handle the data structures or types.

The final outcome of this process is a set of wrappers written in CPython,
which can be used as a module in your Python code.

In a few words, the Generator is a utility that parses a collection of header and
typesystem files, generating other files (code, documentation, etc.) as result.

Creating new bindings
=====================

.. figure:: images/bindinggen-development.png
   :scale: 80
   :align: center

   Creating new bindings

Each module of the generator system has an specific role.

1. Provide enough data about the classes and functions.
2. Generate valid code, with modifications from typesystems and injected codes.
3. Modify the API to expose the objects in a way that fits you target language best.
4. Insert customizations where handwritten code is needed.

.. figure:: images/shibokenqtarch.png
   :scale: 80
   :align: center

   Runtime architecture

The newly created binding will run on top of Shiboken which takes
care of interfacing Python and the underlying C++ library.

Handwritten inputs
==================

Creating new bindings involves creating several pieces of "code": the header,
the typesystem and, in most cases, the injected code.

:header: A header with ``#include`` directives listing all the headers of the
         desired classes. This header is not referenced by the generated code.
         Alternatively, it is possible to pass a list of the headers of the
         desired classes directly on the command line. In this case,
         the command line option ``--use-global-header`` should be passed as
         well to prevent the headers from being suppressed in the generated
         code.

::ref:`typesystem`: XML files that provides the developer with a tool to customize the
             way that the generators will see the classes and functions. For
             example, functions can be renamed, have its signature changed and
             many other actions.
::ref:`inject code <codeinjectionsemantics>`: allows the developer to insert
              handwritten code where the generated code is not suitable or
              needs some customization.

.. _command-line:

Command line options
********************

Usage
-----

::

   shiboken [options] header-file(s) typesystem-file


Options
-------

``--disable-verbose-error-messages``
    Disable verbose error messages. Turn the CPython code hard to debug but saves a few kilobytes
    in the generated binding.

.. _parent-heuristic:

``--enable-parent-ctor-heuristic``
    This flag enable an useful heuristic which can save a lot of work related to object ownership when
    writing the typesystem.
    For more info, check :ref:`ownership-parent-heuristics`.

.. _pyside-extensions:

``--enable-pyside-extensions``
    Enable pyside extensions like support for signal/slots. Use this if you are creating a binding based
    on PySide.

.. _return-heuristic:

``--enable-return-value-heuristic``
    Enable heuristics to detect parent relationship on return values.
    For more info, check :ref:`return-value-heuristics`.

.. _avoid-protected-hack:

``--avoid-protected-hack``
    Avoid the use of the '#define protected public' hack.

.. _use-isnull-as-nb-nonzero:

``--use-isnull-as-nb_nonzero``
    If a class has an isNull() const method, it will be used to
    compute the value of boolean casts (see :ref:`bool-cast`).

.. _use-operator-bool-as-nb-nonzero:

``--use-operator-bool-as-nb_nonzero``
    If a class has an operator bool, it will be used to compute
    the value of boolean casts (see :ref:`bool-cast`).

.. _no-implicit-conversions:

``--no-implicit-conversions``
    Do not generate implicit_conversions for function arguments.

.. _api-version:

``--api-version=<version>``
    Specify the supported api version used to generate the bindings.

.. _documentation-only:

``--documentation-only``
    Do not generate any code, just the documentation.

.. _drop-type-entries:

``--drop-type-entries="<TypeEntry0>[;TypeEntry1;...]"``
    Semicolon separated list of type system entries (classes, namespaces,
    global functions and enums) to be dropped from generation. Values are
    fully qualified Python type names ('Module.Class'), but the module can
    be omitted ('Class').

.. _conditional_keywords:

``-keywords=keyword1[,keyword2,...]``
    A comma-separated list of keywords for conditional typesystem parsing
    (see :ref:`conditional_processing`).

``--use-global-header``
    Use the global headers passed on the command line in generated code.

.. _generation-set:

``--generation-set``
    Generator set to be used (e.g. qtdoc).

.. _skip-deprecated:

``--skip-deprecated``
    Skip deprecated functions.

.. _diff:

``--diff``
    Print a diff of wrapper files.

.. _dryrun:

``--dryrun``
    Dry run, do not generate wrapper files.

.. _--project-file:

``--project-file=<file>``
    Text file containing a description of the binding project.
    Replaces and overrides command line arguments.

.. _clang_option:

``--clang-option=<option>``
    Option to be passed to clang

.. _clang_options:

``--clang-options=<option1>[,<option2>,...]>``
    Options to be passed to clang.
    When '-' is passed as the first option in the list, none of the options
    built into shiboken will be added, allowing for a complete replacement.

.. _include-paths:

``-I<path>, --include-paths=<path>[:<path>:...]``
    Include paths used by the C++ parser.

... _system-include-paths:

``-isystem<path>, --system-include-paths=<path>[:<path>:...]``
    System include paths used by the C++ parser

.. _framework-include-paths:

``-F<path>, --framework-include-paths=<path>[:<path>:...]``
    Framework include paths used by the C++ parser

.. _language-level:

``--language-level=, -std=<level>``
    C++ Language level (c++11..c++17, default=c++14)

.. _typesystem-paths:

``-T<path>, --typesystem-paths=<path>[:<path>:...]``
    Paths used when searching for type system files.

.. _output-directory:

``--output-directory=[dir]``
    The directory where the generated files will be written.

.. _license-file=[license-file]:

``--license-file=[license-file]``
    File used for copyright headers of generated files.

.. _no-suppress-warnings:

``--no-suppress-warnings``
    Show all warnings.

.. _silent:

``--silent``
    Avoid printing any message.

.. _debug-level:

``--debug-level=[sparse|medium|full]``
    Set the debug level.

.. _help:

``--help``
    Display this help and exit.

.. _version:

``--version``
    Output version information and exit.

QtDocGenerator Options
----------------------

.. _doc-parser:

``--doc-parser=<parser>``
    The documentation parser used to interpret the documentation
    input files (qdoc|doxygen).

.. _documentation-code-snippets-dir:

``--documentation-code-snippets-dir=<dir>``
    Directory used to search code snippets used by the documentation.

.. _documentation-data-dir:

``--documentation-data-dir=<dir>``
    Directory with XML files generated by documentation tool.

.. _documentation-extra-sections-dir=<dir>:

``--documentation-extra-sections-dir=<dir>``
    Directory used to search for extra documentation sections.

.. _library-source-dir:

``--library-source-dir=<dir>``
    Directory where library source code is located.

.. _additional-documentation:

``--additional-documentation=<file>``
   List of additional XML files to be converted to .rst files
   (for example, tutorials).

.. _project-file:

********************
Binding Project File
********************

Instead of directing the Generator behavior via command line, the binding
developer can write a text project file describing the same information, and
avoid the hassle of a long stream of command line arguments.

.. _project-file-structure:

The project file structure
==========================

Here follows a comprehensive example of a generator project file.

    .. code-block:: ini

         [generator-project]
         generator-set = path/to/generator/CHOICE_GENERATOR
         header-file = DIR/global.h" />
         typesystem-file = DIR/typesystem_for_your_binding.xml
         output-directory location="OUTPUTDIR" />
         include-path = path/to/library/being/wrapped/headers/1
         include-path = path/to/library/being/wrapped/headers/2
         typesystem-path = path/to/directory/containing/type/system/files/1
         typesystem-path = path/to/directory/containing/type/system/files/2
         enable-parent-ctor-heuristic


Project file tags
=================

The generator project file tags are in direct relation to the
:ref:`command line arguments <command-line>`. All of the current command line
options provided by |project| were already seen on the
:ref:`project-file-structure`, for new command line options provided by
additional generator modules (e.g.: qtdoc, Shiboken) could also be used in the
generator project file following simple conversion rules.

For tags without options, just write as an empty tag without any attributes.
Example:

    .. code-block:: bash

         --BOOLEAN-ARGUMENT

becomes

    .. code-block:: ini

         BOOLEAN-ARGUMENT

and

    .. code-block:: bash

         --VALUE-ARGUMENT=VALUE

becomes

    .. code-block:: ini

         VALUE-ARGUMENT = VALUE


