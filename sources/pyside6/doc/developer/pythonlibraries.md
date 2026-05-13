# Python Libraries

Python modules, plugins or libraries using the
[CPython API](https://docs.python.org/3/c-api/index.html) normally need to
link against a library providing the symbols. Several versions of the library
with distinct names may exist depending on build type (limited API,
free threaded, etc).

The build type is indicated by defines like `Py_LIMITED_API` or `Py_GIL_DISABLE`.

## UNIX

On these platforms, the symbol resolution is delayed and the symbols contained
in the Python interpreter binary are used (requiring special options on macOS).

This works for Python modules and also for the Qt Widgets Designer plugin,
in which case the symbols are provided by entry point `pyside6-designer`.

When embedding Python into an application, where no Python interpreter binary
is available, the CPython library needs to be linked against.

There are only libraries for the normal (versioned) build; no CPython library
for the limited API is provided.

The [CPython documentation](https://docs.python.org/3/extending/embedding.html#compiling-and-linking-under-unix-like-systems)
shows how to use tools like ``python3.13-config`` to obtain the correct flags.

## Windows

On Windows, the delayed loading described above is not available and the
CPython libraries need to be explicitly linked against for all use cases.

The header `pyconfig.h` contains a pragma with linking instructions
for usage by the MSVC compiler, depending on the build type:

```c
pragma comment(lib,"python3<14...>lib")
```

To explicitly specify the library by the build system instead, the define
`Py_NO_LINK_LIB` can be set to disable the pragma.

## Tools

The {ref}`Shiboken6Tools CMake package <Shiboken6Tools>` provides the
CMake macro `shiboken_generator_create_binding`, which is a convenient
way of adding the libraries.
