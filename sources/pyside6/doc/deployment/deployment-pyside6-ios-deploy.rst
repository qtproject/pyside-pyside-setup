.. _pyside6-ios-deploy:

pyside6-ios-deploy: the iOS deployment tool for Qt for Python
#############################################################

``pyside6-ios-deploy`` is a tool for deploying PySide6 applications to iOS devices and to the iOS
simulator. It uses the same configuration file ``pysidedeploy.spec`` as ``pyside6-deploy`` and
``pyside6-android-deploy``, reading its options from the ``[ios]`` section.

Unlike the other two tools, ``pyside6-ios-deploy`` does not produce a finished application package.
Instead, it merely generates an **Xcode project**, statically linked against a cross-compiled
PySide6/shiboken6 iOS wheel and the ``Python.xcframework``. You then build and sign that project in
Xcode, and from there run it on the simulator or deploy it to a connected device. This split exists
because signing and provisioning an iOS application requires Apple's own toolchain.

The generated project is written to a ``deployment/<platform tag>/`` next to your entry point.
Device and simulator builds therefore land in separate directories and do not overwrite each other.
That directory contains ``main.mm``, ``Info.plist``, and ``<AppName>.xcodeproj``, and a ``_wheels/``
cache of the unpacked wheels.

.. note:: ``pyside6-ios-deploy`` only works from a macOS host. A Windows or Linux host is rejected,
   because the generated project can only be built by Xcode.

.. note:: Qt, its plugins and PySide6/shiboken6 are linked into the application statically. Since
   the official Qt for iOS builds are static, putting PySide6 into shared libraries on top of them
   duplicates Qt's symbols. Plugins are registered at build time with ``Q_IMPORT_PLUGIN`` in the
   generated ``main.mm``, and several limitations described below follow directly from this.

.. _ios_prerequisites:

Prerequisites
=============

Before using ``pyside6-ios-deploy``, ensure that the following prerequisites are met:

Xcode
-----

A full Xcode installation is required, along with the iOS platform SDK. The ``Command Line Tools``
package alone is not sufficient, because the generated ``.xcodeproj`` is built with ``xcodebuild``
and relies on the iOS SDK and the simulator runtimes that ship with Xcode.

Building for a physical device additionally requires an ``Apple Developer Team ID``, supplied
through the ``--team-id`` option or the ``team_id`` key in ``pysidedeploy.spec``. Building for the
simulator does not require one.

Download Python.xcframework
---------------------------

The Python interpreter that runs inside the application comes from the official
``Python.xcframework`` published on python.org. ``pyside6-ios-deploy`` does not build CPython, and
the host Python version does not have to match the version running on the device.

You do not normally need to download it yourself. If neither ``--xcframework-path`` nor the
``xcframework_path`` key in ``pysidedeploy.spec`` is set, the tool downloads the pinned release into
its cache directory ``~/.pyside6_ios/Python-iOS/`` and verifies it against a SHA-256 checksum
published on the python.org release page. Subsequent runs reuse the cached copy.

To use your own build instead, pass its path explicitly:

.. code-block:: bash

    pyside6-ios-deploy --xcframework-path=/path/to/Python.xcframework

You never state which Python version you are targeting, and there is no configuration key for it.
The tool reads it from the framework's own ``lib/python3.X`` directory, so the interpreter paths in
the generated project cannot drift out of sync with the framework you supplied.

Download Qt for Python iOS wheels
---------------------------------

``pyside6-ios-deploy`` needs a PySide6 wheel and a shiboken6 wheel built for iOS. These are not the
desktop wheels from PyPI, and they cannot be installed with ``pip``, they are read directly from
disk, and the tool unpacks them itself.

An iOS PySide6 wheel embeds a complete Qt-for-iOS kit under ``PySide6/Qt/``, including the Qt
frameworks, headers, ``.prl`` files, plugins, QML modules and ``qt.toolchain.cmake``. You therefore
do not need a separate Qt-for-iOS installation to *deploy*; you only need one to *build the wheels*
as described in :ref:`cross_compile_ios`.

There are three ways to obtain the wheels:

1. Download them from the `Qt for Python downloads page`_.

2. Use :ref:`qtpip` to download them:

   .. code-block:: bash

       qtpip download PySide6 --ios --arch arm64 --platform device

   ``--arch`` accepts ``arm64`` or ``x86_64``, and ``--platform`` (or ``--plat``) accepts
   ``device`` or ``simulator``. Both may be omitted: ``--platform`` defaults to ``device``,
   except for ``x86_64``, where the simulator is selected automatically because no iOS device
   uses that architecture. ``--arch`` defaults to ``arm64`` for a device, and to the host
   architecture for the simulator.

3. Build them yourself, as described in :ref:`cross_compile_ios`.

Each wheel targets exactly one architecture and one platform, encoded in its platform tag:

.. list-table::
   :header-rows: 1

   * - Platform tag
     - Target
   * - ``ios_arm64``
     - Physical device
   * - ``ios_arm64_simulator``
     - Simulator on Apple Silicon
   * - ``ios_x86_64_simulator``
     - Simulator on Intel

There is no universal wheel covering more than one of these. The target architecture and the
device-versus-simulator choice are never passed on the command line; they are derived from the
wheel's platform tag alone. Selecting a different target means passing a different pair of wheels.

Before generating anything, the tool checks that the PySide6 and shiboken6 wheels target the same
platform tag. A mismatch is reported up front rather than surfacing later as a confusing Xcode
link failure.

How to use it?
==============

``pyside6-ios-deploy`` takes the path to your main Python entry point file as an optional positional
argument:

.. code-block:: bash

    pyside6-ios-deploy /path/to/main.py --name "<AppName>"
        --wheel-pyside=path_to_downloaded_PySide_wheel
        --wheel-shiboken=path_to_downloaded_shiboken_wheel

The path of your main Python entry point can be left out in two cases. If the current directory
contains a file named ``main.py``, that file is used, so running the tool from the application
directory needs no path at all. Or if you pass an existing ``pysidedeploy.spec`` with
``-c``/``--config-file``, the entry point is taken from its ``input_file`` key instead.

``--xcframework-path`` is optional; without it the tool uses its cache, downloading
``Python.xcframework`` on first use. ``--team-id`` is required only for device builds.

On the first run, a ``pysidedeploy.spec`` file is created with the values you passed. For any
subsequent run, those values are read back from it, so the wheel paths do not have to be repeated:

.. code-block:: bash

    pyside6-ios-deploy --config-file pysidedeploy.spec

Note that ``--config-file`` has to be passed explicitly here, even though it defaults to
``pysidedeploy.spec`` in the current directory. ``--wheel-pyside`` and ``--wheel-shiboken``
are only optional when ``-c``/``--config-file`` appears on the command line; without it they
remain required arguments and the tool exits before it would have read the configuration file.


Opening the generated project
-----------------------------

Once the tool finishes, open the project in Xcode:

.. code-block:: bash

    open deployment/<platform tag>/<AppName>.xcodeproj

From there, select a simulator or a connected device as the run destination and build and run as you
would with any other Xcode project. Note that the run destination must match the wheels you deployed
with: a project generated from ``ios_arm64`` wheels will not run on the simulator.

Your application's Python files, QML directories, PySide6 and shiboken6, and the Python standard
library are copied into the application bundle by build phases in the generated project, so they are
refreshed on every Xcode build without rerunning ``pyside6-ios-deploy``. The list of files is fixed
when the project is generated, so adding a new Python file or QML directory does need a rerun.

.. _pysideiosdeploy:

pysidedeploy.spec
=================

Like the other deployment tools, ``pyside6-ios-deploy`` uses ``pysidedeploy.spec`` to control the
deployment. The advantages of such a file are mentioned :ref:`here <pysidedeployspec_advantages>`.
Sharing one file across all platforms means a single project can be configured for desktop, Android
and iOS at once.

Several ``[ios]`` keys have no command line equivalent and can only be set by editing the file
directly: ``deployment_target``, ``entitlements``, ``signing_style`` and ``header_search_paths``.

The relevant parameters for ``pyside6-ios-deploy`` are:

**app**
  * ``title``: The name of the application. Also used to derive the Xcode product name and the
    bundle identifier while ``bundle_id`` is still empty. Once a value has been recorded there,
    changing the title alone does not change it. Clear the ``bundle_id`` key to have it derived from
    the title again.
  * ``project_dir``: Project directory. The general assumption made is that the project directory is
    the parent directory of the main Python entry point file.
  * ``input_file``: Path to the main Python entry point file. Recorded from the path you passed on
    the command line, and used on subsequent runs when no path is given.
  * ``project_file``: If it exists, this points to the path of a :ref:`python_project_file` or a
    :ref:`qt_creator_pyproject_file`. Such a file in the project directory ensures that deployment
    does not consider unnecessary files when bundling the application.

**qt**
  * ``modules``: Comma-separated list of all the Qt modules used by the application. This option is
    computed automatically by ``pyside6-ios-deploy``. If you want to explicitly include certain Qt
    modules, the module names can be appended to this list without the ``Qt`` prefix, e.g.
    ``Network`` instead of ``QtNetwork``.
  * ``plugins``: This field is *not relevant* for ``pyside6-ios-deploy``. Qt plugins are resolved
    from the Qt kit embedded in the PySide6 wheel and registered statically in the generated
    ``main.mm``; there is nothing to configure.

.. _ios_key:

**ios**
  * ``wheel_pyside``: Path to the PySide6 iOS wheel. Its platform tag determines the target
    architecture and whether the build targets a device or the simulator.
  * ``wheel_shiboken``: Path to the shiboken6 iOS wheel. Must match ``wheel_pyside``.
  * ``xcframework_path``: Path to ``Python.xcframework``. If left empty, the tool downloads the
    pinned python.org release into ``~/.pyside6_ios/Python-iOS/`` and writes the resulting path back
    here.
  * ``bundle_id``: Reverse-DNS bundle identifier, e.g. ``com.example.myapp``. Defaults to
    ``com.example.<app name>`` with the name reduced to the characters Apple permits in a bundle
    identifier. This is a placeholder in the same sense as Xcode's own default organization
    identifier, and has to be replaced with an identifier you own before App Store distribution.
    See :ref:`ios_bundle_id` for why it is worth changing earlier than that.
  * ``team_id``: Apple Developer Team ID, used for code signing. Required only for device builds.
  * ``version``: Application version, used as ``CFBundleShortVersionString``.
  * ``deployment_target``: Minimum iOS version the application supports. Leave it **empty** to
    follow Qt: the value comes from the Qt kit in the PySide6 wheel, read from its
    ``qt.toolchain.cmake``, and is deliberately never written back, so the key keeps tracking Qt
    across upgrades. This is the recommended setting. A **non-empty** value is yours to maintain,
    including when a Qt upgrade raises Qt's own minimum underneath it. Lower than Qt's minimum is
    rejected, since the application would claim support for iOS versions its linked Qt cannot run
    on. Higher is accepted, and is legitimate if your application needs a newer iOS API, but it
    narrows the range of devices that can install it.
  * ``entitlements``: Path to an ``.entitlements`` file, relative to ``project_dir``. The file
    is copied next to the generated project and referenced by it.
  * ``signing_style``: Either ``Automatic`` or ``Manual``. Defaults to ``Automatic``.
  * ``header_search_paths``: Comma-separated extra header search paths, relative to ``project_dir``,
    added to the generated Xcode target.

Command Line Options
====================

Here are all the command line options of ``pyside6-ios-deploy``:

* **main_file**: Path to the main Python entry point file, given as an optional positional argument.
  When it is omitted, ``main.py`` in the current directory is used, unless ``-c``/``--config-file``
  is passed, in which case the entry point comes from the configuration file's ``input_file`` key.

* **-c/--config-file**: This option is used to specify the path to ``pysidedeploy.spec`` explicitly.
  Its value defaults to ``pysidedeploy.spec`` in the current directory, but passing the option is
  what makes ``--wheel-pyside`` and ``--wheel-shiboken`` optional, so it is needed on every run
  after the first even when the default path is the right one.

* **--init**: Creates or updates ``pysidedeploy.spec`` without generating the Xcode project, which
  is useful for reviewing the configuration first. Note that ``pysidedeploy.spec`` is created or
  updated on every run regardless and that the wheels are still validated and unpacked and
  ``Python.xcframework`` still downloaded, so this is not a no-op. ``--wheel-pyside`` and
  ``--wheel-shiboken`` are required here too unless ``-c/--config-file`` is passed.
  Usage::

    pyside6-ios-deploy --init --wheel-pyside=<path> --wheel-shiboken=<path>

* **-v/--verbose**: Runs ``pyside6-ios-deploy`` in verbose mode.

* **--dry-run**: Displays the files that would be generated, without writing them. The wheels are
  still unpacked into ``deployment/<platform tag>/_wheels/``, since their contents are needed to
  resolve Qt modules.

* **--name**: Application name. Note that changing the name on a later run does not change an
  already-recorded ``bundle_id``; pass ``--bundle-id`` as well if you want both to change.

* **--wheel-pyside**: Path to the PySide6 iOS wheel.

* **--wheel-shiboken**: Path to the shiboken6 iOS wheel.

* **--xcframework-path**: Path to ``Python.xcframework``. If omitted, the tool uses its cache
  at ``~/.pyside6_ios/Python-iOS/``, downloading the framework on first use.

* **--bundle-id**: Reverse-DNS bundle identifier, e.g. ``com.example.myapp``.

* **--team-id**: Apple Developer Team ID, used for code signing. Required only for device
  builds.

* **--app-version**: Application version, used as ``CFBundleShortVersionString``.

.. _ios_bundle_id:

Bundle identifiers
==================

The bundle identifier is the application's identity, both to iOS and to the Apple developer team it
is registered against. When you do not supply one, ``pyside6-ios-deploy`` derives
``com.example.<app name>`` from the application's title (keeping only the characters Apple permits),
a placeholder in the same sense as Xcode's own default organization identifier.

Replace it as soon as you deploy to a real device, not only when preparing for distribution: pass
``--bundle-id`` once, or set ``bundle_id`` in ``pysidedeploy.spec``, to a reverse-DNS name under a
domain you control. With automatic signing, building for a device registers the identifier against
your team, and ``com.example.*`` is a namespace many projects leave in place, so it is likely to be
rejected there before the application is ever installed. Note that renaming the application later
does not update an identifier that has already been recorded.

.. _ios_permissions:

Permissions
===========

Qt's cross-platform permission API is described in :ref:`permission-considerations`. For iOS,
``pyside6-ios-deploy`` writes the usage description strings into the generated ``Info.plist``.

All six are always declared, whether or not your application uses them. PySide6 registers all six
Darwin permission plugins (camera, microphone, Bluetooth, contacts, calendar and location) with
``Q_IMPORT_PLUGIN`` when PySide6 itself is built, a consequence of the static linking described
above, so they cannot be enabled or disabled per application. The generated ``Info.plist``
therefore declares all six ``NS*UsageDescription`` keys with generic text of the form
``<AppName> uses the camera.``, and there is no equivalent of ``pyside6-deploy``'s
``macos.permissions`` key to customize them.

At runtime this is harmless, since iOS only prompts when the application actually requests a
permission. It matters for distribution: Apple displays the purpose string verbatim and expects it
to explain why the capability is needed, and declaring capabilities an application does not use is a
recognized App Review risk. Editing the generated ``Info.plist`` works, but it is regenerated on
every run, so adjust the purpose strings and remove the unused keys as a release step, and keep a
record of it outside the generated directory.

.. _ios_third_party_packages:

Third-party Python packages
===========================

Your application's own Python files are handled for you: every ``.py`` file in the project directory
is copied into the bundle, keeping its path relative to the project directory, and your entry point
is the one run at launch. The bundle root is on ``sys.path``, so imports between your own modules
resolve on the device exactly as they do on the desktop. Directories excluded through a
:ref:`python_project_file` or a :ref:`qt_creator_pyproject_file` are skipped, which is the
recommended way to keep unrelated files out of the bundle.

Third-party packages are a different matter. There is currently **no configuration key for adding
them**, and neither kind below should be considered supported yet.

Pure-Python packages
--------------------

A package made up of just ``.py`` files doesn't run into any real obstacle here: it needs to end up
inside the bundle and on ``sys.path``, and both already happen for anything sitting in the project
directory. So copying a package's folder in next to your own code is enough to make it import
correctly.

What's missing is a supported way to declare it as a dependency, plus everything in the package that
isn't ``.py`` code. Only ``.py`` files get copied, so a data file the package reads at runtime is
left behind, and there's no ``.dist-info`` folder for code that checks its own package metadata. A
package that builds a path from ``__file__`` to one of its own resource files will get a path that
looks right, but the file won't be there.

Packages with C extensions
--------------------------

Desktop wheels from PyPI cannot be used. The extension has to be built from source for the correct
iOS architecture and platform, against the same ``Python.xcframework`` as the PySide6 wheels in use,
signed with the application, and packaged in the layout CPython's iOS support expects rather than as
a loose shared object. For most projects that is a substantial undertaking in its own right.

.. _cross_compile_ios:

Cross-compile Qt for Python wheels for iOS
==========================================

The cross-compilation of the Qt for Python wheels for a specific iOS target needs to be done only
once per Qt version and target, irrespective of the number of applications you deploy.
Cross-compiling iOS wheels requires a macOS host.

The script does not build CPython. It downloads the official prebuilt ``Python.xcframework`` from
python.org and verifies it against a pinned SHA-256 checksum, so the host Python version does not
have to match the Python version running on the device.

#. `Download <qt_download_>`_ and install the Qt version for which you would like to create Qt for
   Python wheels. Both the iOS build and the matching macOS build are required: the macOS build
   supplies the host tools used during cross-compilation, while the iOS build supplies the target
   libraries.

#. Clone the Qt for Python repository::

    git clone https://code.qt.io/pyside/pyside-setup

#. Check out the version that you want to build. The version checked out has to correspond to the
   Qt version installed in Step 1::

    cd pyside-setup && git checkout 6.12

#. Install the dependencies::

    pip install -r requirements.txt
    pip install -r tools/cross_compile_ios/requirements.txt

#. Run the cross-compilation script::

    python tools/cross_compile_ios/main.py --qt-install-path=~/Qt/6.12.0 --arch=arm64

   *--qt-install-path* refers to the Qt installation root. It is not the path to a single Qt build:
   the script appends a fixed subdirectory name to it, chosen from the target you asked for, so one
   path covers both the target Qt and the host Qt.

   .. list-table::
      :header-rows: 1

      * - Subdirectory
        - Used for
      * - ``ios_device``
        - Target Qt, device build (default)
      * - ``ios_simulator_arm64``
        - Target Qt, simulator build with ``--arch=arm64 --simulator``
      * - ``ios_simulator_x86_64``
        - Target Qt, simulator build with ``--arch=x86_64``
      * - ``macos``
        - Host Qt, supplying the tools used during cross-compilation

   These names are not configurable, so the Qt installation has to match this layout. Passing a path
   directly to an iOS build, rather than to the root containing it, will not work.

   *--arch* selects the target CPU architecture and accepts ``arm64`` or ``x86_64``. Add
   *--simulator* to build for the iOS Simulator instead of a device; ``x86_64`` implies
   ``--simulator``, since no iOS device uses that architecture. Use *--dry-run* to print the
   ``bdist_wheel`` command without running it, and *--help* to see all available options::

     python tools/cross_compile_ios/main.py --help

Each invocation produces wheels for exactly one target, so building for both a device and the
simulator means running the script twice.

The finished iOS wheels are written to ``dist_ios/`` in the repository root.

.. _`qt_download`: https://www.qt.io/download
.. _`Qt for Python downloads page`: https://download.qt.io/official_releases/QtForPython/pyside6/
