[app]

# Title of your application
title = My Application

# Project Directory
project_dir =

# Source file path
input_file =

# Directory where exec is stored
exec_directory =

[python]

# Python path
python_path =

# python packages to install
# ordered-set: increase compile time performance of nuitka packaging
# zstandard: provides final executable size optimization
packages = nuitka,PySide6,ordered_set,zstandard

[qt]

# Comma separated path to QML files required
# normally all the QML files are added automatically
qml_files =

[nuitka]

# (str) specify any extra nuitka arguments
# eg: extra_args = --show-modules --follow-stdlib
extra_args = --quiet
