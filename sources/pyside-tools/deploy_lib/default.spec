[app]

# Title of your application
title = pyside_app_demo

# Project Directory. The general assumption is that project_dir is the parent directory
# of input_file
project_dir =

# Source file path
input_file =

# Directory where exec is stored
exec_directory =

# Path to .pyproject project file
project_file =

[python]

# Python path
python_path =

# python packages to install
# ordered-set: increase compile time performance of nuitka packaging
# zstandard: provides final executable size optimization
desktop_packages = nuitka==1.4.8,ordered_set,zstandard

[qt]

# Comma separated path to QML files required
# normally all the QML files are added automatically
qml_files =

# excluded qml plugin binaries
excluded_qml_plugins =

[nuitka]

# (str) specify any extra nuitka arguments
# eg: extra_args = --show-modules --follow-stdlib
extra_args = --quiet --noinclude-qt-translations=True
