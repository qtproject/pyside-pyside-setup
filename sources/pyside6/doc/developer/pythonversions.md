# Adapting to changes in supported Python versions

## Relevant preprocessor defines

- The version range is determined by `wheel_artifacts/pyproject.toml.base`.
  This file also defines the version tag (`py_limited_api = "cp310"`).
- `PY_VERSION_HEX` Python version (defined in CPython headers)
- `Py_LIMITED_API` Limited API minimum version, defined in several CMake files
- `PYPY_VERSION`  [PyPy](https://pypy.org/) version (defined in PyPy headers)

## Removing outdated Python versions

The removal of Python versions is tied to their lifetime
(see [Wiki](https://wiki.qt.io/Qt_for_Python)).

- Raise the `Py_LIMITED_API` definition in the CMake files.
- Check the source code for preprocessor defines depending on
  values `Py_LIMITED_API`, `PY_VERSION_HEX` and simplify or
  remove conditions if possible.
- Check the usages of `_PepRuntimeVersion()` for outdated versions
- Run the tests and some examples. There might actually
  some version checks in Python code that trigger
  (see for example 
   `sources/shiboken6/shibokenmodule/files.dir/shibokensupport/signature/parser.py:70`).

## Adapting to new Python versions

New versions appear as branches in the `https://github.com/python/cpython.git`
repository, are developed over the course of a year and released around fall.
Change logs and information about deprecations are found in the directory
`Doc/whatsnew`.

It is recommended to build a release and a debug version of it and check
whether PySide works with it from time to time.

It is possible that some breakages occur that are fixed later in the
development process, so, one should not prematurely submit fixes to PySide.

A debug version of CPython can be build from a shadow build directory
using:
```
<src_dir>/configure --prefix=<target_dir> --enable-shared --with-ensurepip=install \
   -with-pydebug --with-trace-refs --with-valgrind \
   "CFLAGS=-O0 -g -fno-inline -fno-omit-frame-pointer" CPPFLAGS=-O0 LDFLAGS=-O0
make && make install
```

For a release build:

```
<src_dir>/configure --prefix=<target_dir> --enable-shared --with-ensurepip=install \
   --enable-optimizations
make && make install
```

Those binaries can then be used to create `venv`s and build PySide normally.

Tests should always pass in the release build. The debug build might
have some test failures; but it should not assert.

It should also be checked whether PySide compiles when raising the Limited API
minimum version to the new version (although the change can only be submitted
much later).

Also, the documentation should be checked for outdated version information.
