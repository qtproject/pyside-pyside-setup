# Maintenance

## Frequent tasks

- Merges to *tqtc* branches
- Manual cherry-picks of the changes done by the submodule update bot
  to the *dependencies.yaml* file from dev to the version branches

## Adapting to Python versions

New Python versions are developed during the year and released in fall.
See [Adapting to changes in supported Python versions](adapting_to_changes_in_supported_python_versions).

## Adapting to Qt versions

See [Adapt to new Qt versions](developer-adapt-qt).

## Code base

- Since [Unity](https://qt-project.atlassian.net/browse/QTBUG-109394) builds
  are now default, Non-Unity builds need to be checked in intervals
  (by passing `--no-unity` to *setup.py*).
- `clang-tidy` warnings and Qt deprecations need to be checked in regular
  intervals.

## Updating examples

The script `tools/sync_examples.py` can be used
to update QML, `.ui` and other files from a Qt source tree.
Care must be taken when updating `qmldir` files, the `prefer`
directives used in C++ do not work for Python.
Also, the usage of `.qrc` may differ.

Note: QML examples in Python generally use subdirectories
with a `qmldir` file for QML modules, whereas in C++, the
`.qml` files are in the main directory.

See also [Add a new example or port one](developer-add-port-example).

## Documentation

Some things need to be checked in regular intervals:
- List of C++ overviews used in PySide
  (see [Maintaining additionaldocs.lst](maintaining-additionaldocs) ).
- Documentation warnings
- Module overviews in `sources/pyside6/doc/developer/extras`
