.. _pyside6-deploy:

pyside6-deploy: the deployment tool for Qt for Python
#####################################################

``pyside6-deploy`` is an easy to use tool for deploying PySide6 applications to different
platforms. It is a wrapper around `Nuitka <https://nuitka.net/>`_, a Python compiler that
compiles your Python code to C code, and links with libpython to produce the final executable.

The final executable produced has a ``.exe`` suffix on Windows, ``.bin`` on Linux and ``.app`` on
macOS.

.. note:: The default version of Nuitka used with the tool is version ``2.4.8``. This can be
    updated to a newer version by updating your ``pysidedeploy.spec`` file.

.. _how_pysidedeploy:

How to use it?
==============

There are 2 different ways with which you can deploy your PySide6 application using
``pyside6-deploy``:

Approach 1: Using the main python entry point file
--------------------------------------------------

In this approach, you point ``pyside6-deploy`` to the file containing the main Python entry point
file of the project i.e. the file containing ``if __name__ == "__main__":``.
The command looks like this::

    pyside6-deploy /path/to/main_file.py

On running the command, ``pyside6-deploy`` installs all the dependencies required for deployment
into the Python environment.

If your main Python entry point file is named ``main.py``, then you don't have to point it to the
filename. You can run ``pyside6-deploy`` without any options, and it will work.

.. note:: If your project contains a ``pysidedeploy.spec`` file, which is generated on the first
    run of ``pyside6-deploy`` on the project directory, then for any subsequent runs of
    ``pyside6-deploy`` you can run ``pyside6-deploy`` without specifying the main Python entry
    point file. It would take the path to the main file from the ``pysidedeploy.spec`` file.
    To know more about what deployment parameters are controlled by ``pysidedeploy.spec`` file,
    read `pysidedeploy`_.

.. _approach_two:

Approach 2: Using pysidedeploy.spec config file
------------------------------------------------

When you run ``pyside6-deploy`` for the first time, it creates a file called ``pysidedeploy.spec``
in the project directory. This file controls various :ref:`parameters <pysidedeploy>` that influence
the deployment process. Any subsequent runs of ``pyside6-deploy`` on the project directory, would
not require additional parameters like the main Python entry point file. You can also point
``pyside6-deploy`` to the path of the ``pysidedeploy.spec`` file (in case it is not in the same
directory), to take the parameters from that file. This can be done with the following command::

    pyside6-deploy -c /path/to/pysidedeploy.spec

.. _pysidedeploy:

pysidedeploy.spec
=================

As mentioned in the `Approach 2 <approach_two>`_ above, you can use this file to control the various
parameters of the deployment process. The file has multiple sections, with each section containing
multiple keys (parameters being controlled) assigned to a value. The advantages of such a file are
two folds:

.. _pysidedeployspec_advantages:

#. Using the command line, you can control the deployment parameters without specifying them each
   time. It is saved permanently in a file, and any subsequent runs much later in time
   would enable the user to be aware of their last deployment parameters.

#. Since these parameters are saved into a file, they can be checked into version control. This
   gives the user more control of the deployment process. For example, when you decide to exclude
   more QML plugins, or want to include more Nuitka options into your executable.

This file is also used by the ``pyside6-android-deploy`` tool as a configuration file. The advantage
here is that you can have one single file to control deployment to all platforms.

The relevant parameters for ``pyside6-deploy`` are:

**app**
  * ``title``: The name of the application
  * ``project_dir``: Project directory. The general assumption made is that the project directory
    is the parent directory of the main Python entry point file
  * ``input_file``: Path to the main Python entry point file
  * ``project_file``: If it exists, this points to the path to the `Qt Creator Python Project File
    .pyproject <https://doc.qt.io/qtforpython-6/faq/typesoffiles.html
    #qt-creator-python-project-file-pyproject>`_ file. Such a file makes sure that the deployment
    process never considers unnecessary files when bundling the executable.
  * ``exec_directory``: The directory where the final executable is generated.
  * ``icon``: The icon used for the application. For Windows, the icon image should be of ``.ico``
    format, for macOS it should be of ``.icns`` format, and for linux all standard image formats
    are accepted.

**python**
  * ``python_path``: Path to the Python executable. It is recommended to run the deployment
    process inside a virtual environment as certain python packages will be installed onto the
    Python environment.
  * ``packages``: The Python packages installed into the Python environment for deployment to
    work. By default, the Python packages `nuitka <https://pypi.org/project/Nuitka/>`__,
    `ordered_set <https://pypi.org/project/ordered-set/>`_ and `zstandard
    <https://pypi.org/project/zstandard/>`_ are installed. If the deployment platform is
    Linux-based, then `patchelf <https://pypi.org/project/patchelf/>`_ is also installed

**qt**
  * ``qml_files``: Comma-separated paths to all the QML files bundled with the executable
  * ``excluded_qml_plugins``: The problem with using Nuitka for QML deployment is that all the QML
    plugins are also bundled with the executable. When the plugins are bundled, the binaries of
    the plugin's Qt module are also packaged. For example, size heavy module like QtWebEngine
    also gets added to your executable, even when you do not use it in your code. The
    ``excluded_qml_plugins`` parameter helps you to explicitly specify which all QML plugins are
    excluded. ``pyside6-deploy`` automatically checks the QML files against the various QML
    plugins and excludes the following Qt modules if they don't exist::

      QtQuick, QtQuick3D, QtCharts, QtWebEngine, QtTest, QtSensors

    The reason why only the presence of the above 6 Qt modules is searched for is because they
    have the most size heavy binaries among all the Qt modules. With this, you can drastically
    reduce the size of your executables.
  * ``modules``: Comma-separated list of all the Qt modules used by the application. Just like the
    other configuration options in `pysidedeploy.spec`, this option is also computed automatically
    by ``pyside6-deploy``. However, if the user wants to explicitly include certain Qt modules, the
    module names can be appended to this list without the `Qt` prefix.
    e.g. Network instead of QtNetwork
  * ``plugins``: Comma-separated list of all the Qt plugins used by the application. Just like the
    other configuration options in `pysidedeploy.spec`, this option is also computed automatically
    by ``pyside6-deploy``. However, if the user wants to explicitly include certain Qt plugins,
    the plugin names can be appended to this list. To see all the plugins bundled with PySide6,
    see the `plugins` folder in the `site-packages` on your Python where PySide6 is installed. The
    plugin name correspond to their folder name.

**nuitka**
  * ``macos.permissions``: Only relevant for macOS. This option lists the  permissions used by the
    macOS application, as found in the ``Info.plist`` file of the macOS application bundle, using
    the so-called UsageDescription strings. The permissions are normally automatically found by
    ``pyside6-deploy``. However the user can also explicitly specify them using the format
    `<UsageDescriptionKey>:<Short Description>`. For example, the Camera permission is specified
    as::

      NSCameraUsageDescription:CameraAccess

  * ``mode``: Accepts one of the options: ``onefile`` or ``standalone``. The default is ``onefile``.
    This option corresponds to the mode in which Nuitka is run. The onefile mode creates a single
    executable file, while the standalone mode creates a directory with the executable and all the
    necessary files. The standalone mode is useful when you want to distribute the application as a
    directory with dependencies and other files required by the app.

  * ``extra_args``: Any extra Nuitka arguments specified. It is specified as space-separated
    command line arguments i.e. just like how you would specify it when you use Nuitka through
    the command line. By default, it contains the following arguments::

      --quiet --noinclude-qt-translations=True

Command Line Options
====================

The most important command line options are the path to the main Python entry point file and the
``pysidedeploy.spec`` file. If neither of these files exists or their command line options are
given, then ``pyside6-deploy`` assumes that your current working directory does not contain a
PySide6 project.

Here are all the command line options of ``pyside6-deploy``:

* **main entry point file**: This option does not have a name or a flag and is not restricted by it.
  This enables ``pyside6-deploy`` to be used like::

    pyside6-deploy /path/to/main_file.py

* **-c/--config-file**: This option is used to specify the path to ``pysidedeploy.spec`` explicitly

* **--init**: Used to only create the ``pysidedeploy.spec`` file
  Usage::

    pyside6-deploy /path/to/main --init


* **-v/--verbose**: Runs ``pyside6-deploy`` in verbose mode.

* **--dry-run**: Displays the final Nuitka command being run.

* **--keep-deployment-files**: When this option is added, it retains the build folders created by
   Nuitka during the deployment process.

* **-f/--force**: When this option is used, it forces through all the input prompts.
  ``pyside6-deploy`` prompts the user to create a Python virtual environment, if not already in one.
  With this option, the current Python environment is used irrespective of whether the current
  Python environment is a virtual environment or not.

* **--name**: Application name.

* **--extra-ignore-dirs**: Comma-separated directory names inside the project directory. These
  directories will be skipped when searching for Python files relevant to the project.

* **--extra-modules**:  Comma-separated list of Qt modules to be added to the application,
  in case they are not found automatically. The module name can either be specified
  by omitting the prefix of Qt or including it eg: both Network and QtNetwork works.

Considerations
===============

For deployment to work efficiently by bundling only the necessary plugins, the following utilities
are required to be installed on the system:

.. list-table::
   :header-rows: 1

   * - OS
     - Dependencies
     - Installation
   * - Windows
     - dumpbin
     - Shipped with MSVC. Run `vcvarsall.bat` to add it to PATH
   * - Linux
     - readelf
     - Available by default
   * - macOS
     - dyld_info
     - Available by default from macOS 12 and upwards

Creating a bug report
=====================

If you are unsure if the bug is from ``pyside6-deploy`` or ``Nuitka``:

#. Create a bug report in Qt for Python. See instructions
   `here <https://wiki.qt.io/Qt_for_Python/Reporting_Bugs/>`_.

#. Run ``pyside6-deploy`` command with the ``--verbose`` option and replace ``--quiet`` with
   ``--verbose`` in the ``extra_args`` parameter in the ``pysidedeploy.spec`` file. Attach the
   output from stdout to the bug report.

#. Attach a minimal example that reproduces the bug with the bug report.

If you think the bug originates from ``Nuitka``:

#. Try using a newer version of ``Nuitka``. You can change this from the ``packages`` parameter in
   your generated ``pysidedeploy.spec`` file.

#. If the bug persists, create a bug report on the
   `Nuitka GitHub page <https://github.com/Nuitka/Nuitka/issues>`_.

   * Run ``pyside6-deploy`` with the ``--dry-run`` option to see the actual ``Nuitka`` command
     generated. Attach the ``Nuitka`` command ran to the bug report.
   * Follow the Nuitka bug report template to create a bug report.
