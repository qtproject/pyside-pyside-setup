# Snippets Translate

To install dependencies on an activated virtual environment run
`pip install -r requirements.txt`.

To run the tests, execute `python -m pytest`. It's important not to
run `pytest` alone to include the PYTHONPATH so the imports work.

Here's an explanation for each file:

* `main.py`, main file that handle the arguments, the general process
  of copying/writing files into the pyside-setup/ repository.
* `converter.py`, main function that translate each line depending
  of the decision making process that use different handlers.
* `handlers.py`, functions that handle the different translation cases.
* `parse_utils.py`, some useful function that help the translation process.
* `tests/test_converter.py`, tests cases for the converter function.

## Usage

```
% python main.py -h
usage: sync_snippets [-h] --qt QT_DIR --pyside PYSIDE_DIR [-w] [-v]

optional arguments:
  -h, --help           show this help message and exit
  --qt QT_DIR          Path to the Qt directory (QT_SRC_DIR)
  --pyside PYSIDE_DIR  Path to the pyside-setup directory
  -w, --write          Actually copy over the files to the pyside-setup directory
  -v, --verbose        Generate more output
```

For example:

```
python main.py --qt /home/cmaureir/dev/qt6/ --pyside /home/cmaureir/dev/pyside-setup -w
```

which will create all the snippet files in the pyside repository. The `-w`
option is in charge of actually writing the files.


## Pending cases

As described at the end of the `converter.py` and `tests/test_converter.py`
files there are a couple of corner cases that are not covered like:

* handler `std::` types and functions
* handler for `operator...`
* handler for `tr("... %1").arg(a)`
* support for lambda expressions
* there are also strange cases that cannot be properly handle with
  a line-by-line approach, for example, `for ( ; it != end; ++it) {`
* interpretation of `typedef ...` (including function pointers)
* interpretation of `extern "C" ...`

Additionally,
one could add more test cases for each handler, because at the moment
only the general converter function (which uses handlers) is being
tested as a whole.

## Patterns for directories

### Snippets

Everything that has .../snippets/*, for example:

```
    qtbase/src/corelib/doc/snippets/
    ./qtdoc/doc/src/snippets/

```

goes to:

```
    pyside-setup/sources/pyside6/doc/codesnippets/doc/src/snippets/*
```

### Examples

Everything that has .../examples/*/*, for example:

```
    ./qtbase/examples/widgets/dialogs/licensewizard
    ./qtbase/examples/widgets/itemviews/pixelator
```

goes to

```
    pyside-setup/sources/pyside6/doc/codesnippets/examples/
        dialogs/licensewizard
        itemviews/pixelator

```

## Patterns for files

Files to skip:

```
    *.pro
    *.pri
    *.cmake
    *.qdoc
    CMakeLists.txt
```

which means we will be copying:

```
    *.png
    *.cpp
    *.h
    *.ui
    *.qrc
    *.xml
    *.qml
    *.svg
    *.js
    *.ts
    *.xq
    *.txt
    etc
```
## Files examples

```
[repo] qt5

    ./qtbase/src/corelib/doc/snippets/code/src_corelib_thread_qmutexpool.cpp
    ./qtbase/src/widgets/doc/snippets/code/src_gui_styles_qstyle.cpp
    ./qtbase/src/network/doc/snippets/code/src_network_kernel_qhostinfo.cpp
    ./qtbase/examples/sql/relationaltablemodel/relationaltablemodel.cpp
    ./qtbase/src/printsupport/doc/snippets/code/src_gui_dialogs_qabstractprintdialog.cpp
    ./qtdoc/doc/src/snippets/qlistview-using
    ./qtbase/src/widgets/doc/snippets/layouts/layouts.cpp
```

```
[repo] pyside-setup

    ./sources/pyside6/doc/codesnippets/doc/src/snippets/code/src_corelib_thread_qmutexpool.cpp
    ./sources/pyside6/doc/codesnippets/doc/src/snippets/code/src_gui_styles_qstyle.cpp
    ./sources/pyside6/doc/codesnippets/doc/src/snippets/code/src_network_kernel_qhostinfo.cpp
    ./sources/pyside6/doc/codesnippets/examples/relationaltablemodel/relationaltablemodel.cpp
    ./sources/pyside6/doc/codesnippets/doc/src/snippets/code/src_gui_dialogs_qabstractprintdialog.cpp
    ./sources/pyside6/doc/codesnippets/doc/src/snippets/qlistview-using
    ./sources/pyside6/doc/codesnippets/doc/src/snippets/layouts
```
