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

# Application icon
icon =

[python]

# Python path
python_path =

# python packages to install
# ordered-set: increase compile time performance of nuitka packaging
# zstandard: provides final executable size optimization
packages = Nuitka==2.3.2

# buildozer: for deploying Android application
android_packages = buildozer==1.5.0,cython==0.29.33

[qt]

# Comma separated path to QML files required
# normally all the QML files required by the project are added automatically
qml_files =

# excluded qml plugin binaries
excluded_qml_plugins =

# Qt modules used. Comma separated
modules =

# Qt plugins used by the application
plugins =

[android]

# path to PySide wheel
wheel_pyside =

# path to Shiboken wheel
wheel_shiboken =

# plugins to be copied to libs folder of the packaged application. Comma separated
plugins =

[nuitka]

# usage description for permissions requested by the app as found in the Info.plist file
# of the app bundle
# eg: NSCameraUsageDescription:CameraAccess
macos.permissions =

# (str) specify any extra nuitka arguments
# eg: extra_args = --show-modules --follow-stdlib
extra_args = --quiet --noinclude-qt-translations

[buildozer]

# build mode
# possible options: [release, debug]
# release creates an aab, while debug creates an apk
mode = debug

# contrains path to PySide6 and shiboken6 recipe dir
recipe_dir =

# path to extra Qt Android jars to be loaded by the application
jars_dir =

# if empty uses default ndk path downloaded by buildozer
ndk_path =

# if empty uses default sdk path downloaded by buildozer
sdk_path =

# other libraries to be loaded. Comma separated.
# loaded at app startup
local_libs =

# architecture of deployed platform
# possible values: ["aarch64", "armv7a", "i686", "x86_64"]
arch =
