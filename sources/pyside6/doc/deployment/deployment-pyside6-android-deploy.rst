.. _pyside6-android-deploy:

pyside6-android-deploy: the Android deployment tool for Qt for Python
#####################################################################

``pyside6-android-deploy`` is an easy-to-use tool for deploying PySide6 applications to different
Android architectures, namely *arm64-v8a, x86_64, x86 and armeabi-v7a*. This tool works similarly to
the ``pyside6-deploy`` tool and uses the same configuration file ``pysidedeploy.spec`` as
``pyside6-deploy`` to configure the deployment process. Using the deployment configuration
options either from the command line or from ``pysidedeploy.spec``, ``pyside6-android-deploy``
configures the deployment to be initiated and invokes `buildozer`_, a tool used for packaging Python
applications to Android.

The final output is a `.apk` or a `.aab` file created within the project's source directory. The
`mode` option specified under the :ref:`buildozer <buildozer_key>` key in ``pysidedeploy.spec``
determines whether a `.apk` or a `.aab` is created.

.. warning:: Currently, users are required to cross-compile Qt for Python to generate the wheels
    required for a specific Android target architecture. This requirement will disappear when
    there are official Qt for Python Android wheels (*in progress*). Because of this
    requirement ``pyside6-android-deploy`` will be considered in **Technical Preview**.
    Instructions on cross-compiling Qt for Python for Android can be found
    :ref:`here <cross_compile_android>`.

.. note:: ``pyside6-android-deploy`` only works on a Linux host at the moment. This constraint
    is also because Qt for Python cross-compilation for Android currently only works on Linux
    systems.

How to use it?
==============

Like ``pyside6-deploy``, there are :ref:`two different ways <how_pysidedeploy>` with which
you can deploy your PySide6 application using ``pyside6-android-deploy``. The only difference is
that for ``pyside6-android-deploy`` to work, the main Python entry point file should be named
``main.py``.

.. _pysideandroiddeploy:

pysidedeploy.spec
=================

Like ``pyside6-deploy``, you can use the ``pysidedeploy.spec`` file to control the various
parameters of the deployment process. The file has multiple sections, with each section containing
multiple keys (parameters being controlled) assigned to a value. The advantages of such a file are
mentioned :ref:`here <pysidedeployspec_advantages>`. The benefit of using the same
``pysidedeploy.spec`` for both ``pyside6-deploy`` and ``pyside6-android-deploy`` is that you can
have one single file to control deployment to all platforms.

The relevant parameters for ``pyside6-android-deploy`` are:

**app**
  * ``title``: The name of the application.
  * ``project_dir``: Project directory. The general assumption made is that the project directory
    is the parent directory of the main Python entry point file.
  * ``input_file``: Path to the main Python entry point file. For ``pyside6-android-deploy`` this
    file should be named `main.py`.
  * ``project_file``: If it exists, this points to the path to the `Qt Creator Python Project File
    .pyproject <https://doc.qt.io/qtforpython-6/faq/typesoffiles.html
    #qt-creator-python-project-file-pyproject>`_ file. Such a file in the project directory ensures
    that deployment does not consider unnecessary files when bundling the executable.
  * ``exec_directory``: The directory where the final executable is generated.

**python**
  * ``python_path``: Path to the Python executable. It is recommended to run
    ``pyside6-android-deploy`` from a virtual environment as certain Python packages will be
    installed onto the Python environment. However, note to keep the created virtual environment
    outside the project directory so that ``pyside6-android-deploy`` does not try to package it
    as well.
  * ``android_packages``: The Python packages installed into the Python environment for deployment
    to work. By default, the Python packages `buildozer`_ and `cpython`_ are installed.

.. _qt_key:

**qt**
  * ``modules``: Comma-separated list of all the Qt modules used by the application. Just like the
    other configuration options in ``pysidedeploy.spec``, this option is also computed automatically
    by ``pyside6-android-deploy``. However, if you want to explicitly include certain Qt modules,
    the module names can be appended to this list without the `Qt` prefix.
    e.g. Network instead of QtNetwork
  * ``plugins``: This field is *not relevant* for ``pyside6-android-deploy`` and is only specific to
    ``pyside6-deploy``. The plugins relevant for ``pyside6-android-deploy`` are specified through
    the ``plugins`` option under the :ref:`android <android_key>` key.

.. _android_key:

**android**
  * ``wheel_pyside``: Specifies the path to the PySide6 Android wheel for a specific target
    architecture.
  * ``wheel_pyside``: Specifies the path to the Shiboken6 Android wheel for a specific target
    architecture.
  * ``plugins``: Comma-separated list of all the Qt plugins used by the application. Just like the
    other configuration options in ``pysidedeploy.spec``, this option is also computed automatically
    by ``pyside6-android-deploy``. However, if you want to to explicitly include certain Qt plugins,
    the plugin names can be appended to this list. To see all the plugins bundled with PySide6, see
    the `plugins` folder in the ``site-packages`` on your Python where PySide6 is installed. The
    plugin name corresponds to their folder name. This field can be confused with the ``plugins``
    option under :ref:`qt <qt_key>` key. In the future, they will be merged into one single option.

.. _buildozer_key:

**buildozer**
  * ``mode``: Specifies one of the two modes - `release` and `debug`, to run `buildozer`_. The
    `release` mode creates an *aab* while the `debug` mode creates an apk. The default mode is
    `debug`.
  * ``recipe_dir``: Specifies the path to the directory containing `python-for-android`_ recipes.
    This option is automatically computed by ``pyside6-android-deploy`` during deployment. Without
    the :ref:`--keep-deployment-files <keep_deployment_files>` option of ``pyside6-android-deploy``,
    the `recipe_dir` will point to a temporary directory that is deleted after the final Android
    application package is created.
  * ``jars_dir``: Specifies the path to the Qt Android `.jar` files that are relevant for
    creating the Android application package. This option is automatically computed by
    ``pyside6-android-deploy`` during deployment. Just like ``recipe_dir``, this field is also
    *not relevant* unless used with the :ref:`--keep-deployment-files <keep_deployment_files>`
    option of ``pyside6-android-deploy``.
  * ``ndk_path``: Specifies the path to the Android NDK used for packaging the application.
  * ``sdk_path``: Specifies the path to the Android SDK used for packaging the application.
  * ``local_libs``: Specifies non-Qt plugins or other libraries compatible with the Android target
    to be loaded by the Android runtime on startup.
  * ``sdk_path``: Specifies the path to the Android SDK used for packaging the application.
  * ``arch``: Specifies the target architecture's instruction set. This option take one of the four
    values - *aarch64, armv7a, i686, x86_64*.

Command Line Options
====================

Here are all the command line options of ``pyside6-android-deploy``:

* **-c/--config-file**: This option is used to specify the path to ``pysidedeploy.spec`` explicitly.

* **--init**: Used to only create the ``pysidedeploy.spec`` file.
  Usage::

    pyside6-android-deploy --init

* **-v/--verbose**: Runs ``pyside6-android-deploy`` in verbose mode.

* **--dry-run**: Displays the commands being run to produce the Android application package.

.. _keep_deployment_files:

* **--keep-deployment-files**: When this option is added, it retains the build folders created by
  `buildozer`_ during the deployment process. This includes the folder storing the
  `python-for-android`_ recipes, relevant `.jar` files and even the Android Gradle project for the
  application.

* **-f/--force**: When this option is used, it assumes ``yes`` to all prompts and runs
  ``pyside6-android-deploy`` non-interactively. ``pyside6-android-deploy`` prompts the user to
  create a Python virtual environment, if not already in one. With this option, the current Python
  environment is used irrespective of whether the current Python environment is a virtual
  environment or not.

* **--name**: Application name.

* **--wheel-pyside**:  Path to the PySide6 Android wheel for a specific target architecture.

* **--wheel-shiboken**: Path to the Shiboken6 Android wheel for a specific target architecture.

* **--ndk-path**:  Path to the Android NDK used for packaging the application.

* **--sdk-path**: Path to the Android SDK used for packaging the application.

* **--extra-ignore-dirs**: Comma-separated directory names inside the project directory. These
  directories will be skipped when searching for Python files relevant to the project.

* **--extra-modules**:  Comma-separated list of Qt modules to be added to the application,
  in case they are not found automatically. The module name can either be specified
  by omitting the prefix of Qt or including it eg: both Network and QtNetwork works.

.. _cross_compile_android:

Cross-compile Qt for Python wheels for Android
==============================================

The cross-compilation of Qt for Python wheel for a specific Android target architecture needs to be
done only once per Qt version, irrespective of the number of applications you are deploying.
Currently, cross-compiling Qt for Python wheels only works with a Linux host. Follow these steps
to cross-compile Qt for Python Android wheels.

#. `Download <qt_download>`_ and install Qt version for which you would like to create Qt for Python
   wheels.

#. Cloning the Qt for Python repository::

    git clone https://code.qt.io/pyside/pyside-setup

#. Check out the version that you want to build, for example 6.7. The version checked out has
   to correspond to the Qt version downloaded in Step 1::

    cd pyside-setup && git checkout 6.7

#. Installing the dependencies::

    pip install -r requirements.txt
    pip install -r tools/cross_compile_android/requirements.txt

#. Run the cross-compilation Python script.::

    python tools/cross_compile_android/main.py --plat-name=aarch64 --qt-install-path=/opt/Qt/6.7.0
    --auto-accept-license --skip-update

   *--qt-install-path* refers to the path where Qt 6.7.0 is installed. *--auto-accept-license* and
   *--skip-update* are required for downloading and installing Android NDK and SDK if not already
   specified through command line options or if they don't already exist in the
   ``pyside6-android-deploy`` cache. Use --help to see all the other available options::

     python tools/cross_compile_android/main.py --help

.. _`buildozer`: https://buildozer.readthedocs.io/en/latest/
.. _`python-for-android`: https://python-for-android.readthedocs.io/en/latest/
.. _`qt_download`: https://www.qt.io/download
.. _`cpython`: https://pypi.org/project/Cython/
