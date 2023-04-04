.. _pyside6-deploy:

pyside6-deploy: the deployment tool for Qt for Python
#####################################################

``pyside6-deploy`` is an easy to use tool for deploying PySide6 applications to different
platforms.  It is a  wrapper around `Nuitka <https://nuitka.net/>`_, a Python compiler that
compiles your Python code to C code, and links with libpython to produce the final executable.

The final executable produced has a ``.exe`` suffix on Windows. For Linux and macOS, they have a
``.bin`` suffix.

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

#. Using the command line, you can control the deployment parameters without specifying them each
   time.. It is saved permanently in a file, and any subsequent runs much later in time
   would enable the user to be aware of their last deployment parameters.

#. Since these parameters are saved into a file, they can be checked into version control. This
   gives the user more control of the deployment process. For example, when you decide to exclude
   more QML plugins, or want to include more Nuitka options into your executable.

The various parameters controlled by this file are:

**app**
  * ``title``: The name of the application
  * ``project_dir``: Project directory. The general assumption made is that the project directory
    is the parent directory of the main Python entry point file
  * ``input_file``: Path to the main Python entry point file
  * ``project_file``: If it exists, this points to the path to the `Qt Creator Python Project File
    .pyproject <https://doc.qt.io/qtforpython/tutorials/pretutorial/typesoffiles.html
    #qt-creator-python-project-file-pyproject>`_ file. Such a file makes sure that the deployment
    process never considers unnecessary files when bundling the executable.

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

**nuitka**
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


* **-v/--verbose**: Runs ``pyside6-deploy`` in verbose mode

* **--dry-run**: Displays the final Nuitka command being run

* **--keep-deployment-files**: When this option is added, it retains the build folders created by
   Nuitka during the deployment process.

* **-f/--force**: When this option is used, it forces through all the input prompts.
  ``pyside6-deploy`` prompts the user to create a Python virtual environment, if not already in one.
  With this option, the current Python environment is used irrespective of whether the current
  Python environment is a virtual environment or not.
