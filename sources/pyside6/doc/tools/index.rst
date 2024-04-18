.. _package_tools:

Tools
=====

Following the same idea from the modules, we also include in the packages
(wheels) Qt tools that are important for any Qt application development
workflow, like ``uic``, ``rcc``, etc.

All the tools **must** be used from the PySide wrappers, and not directly.
For example, if exploring the ``site-packages/`` directory on your installation
you find ``uic.exe`` (on Windows), you should not click on that, and use
``pyside6-uic.exe`` instead.
The reason for this is the proper setup of PATHs, plugins, and more,
to properly work with the installed Python package.

Here you can find all the tools we include in |project| starting
from 6.3.0, grouped by different topics:

Project development
~~~~~~~~~~~~~~~~~~~

.. grid:: 2
    :gutter: 3 3 4 5

    .. grid-item-card:: ``pyside6-project``
        :link: pyside6-project
        :link-type: ref

        to build *Qt Widgets Designer* forms (``.ui`` files),
        resource files (``.qrc``) and QML type files (``.qmltype``)
        from a ``.pyproject`` file.

Widget Development
~~~~~~~~~~~~~~~~~~

.. grid:: 2
    :gutter: 3 3 4 5

    .. grid-item-card:: ``pyside6-designer``
        :link: pyside6-designer
        :link-type: ref

        drag-and-drop tool for designing Widget UIs (generates ``.ui`` files,
        see :ref:`using_ui_files`).

    .. grid-item-card:: ``pyside6-uic``
        :link: pyside6-uic
        :link-type: ref

        to generate Python code from ``.ui`` form files.

    .. grid-item-card:: ``pyside6-rcc``
        :link: pyside6-rcc
        :link-type: ref

        to generate serialized data from ``.qrc`` resources files.
        Keep in mind these files can be used in other non-widget projects.


QML Development
~~~~~~~~~~~~~~~

.. grid:: 2
    :gutter: 3 3 4 5

    .. grid-item-card:: ``pyside6-qmllint``
        :link: pyside6-qmllint
        :link-type: ref

        that verifies the syntactic validity of QML files.

    .. grid-item-card:: ``pyside6-qmltyperegistrar``
        :link: pyside6-qmltyperegistrar
        :link-type: ref

        to read metatypes files and generate files that contain the necessary
        code to register all the types marked with relevant macros.

    .. grid-item-card:: ``pyside6-qmlimportscanner``
        :link: pyside6-qmlimportscanner
        :link-type: ref

        to identify the QML modules imported from a
        project/QML files and dump the result as a JSON array.

    .. grid-item-card:: ``pyside6-qmlcachegen``
        :link: pyside6-qmlcachegen
        :link-type: ref

        to compile QML to bytecode at compile time for bundling inside the
        binary.

    .. grid-item-card:: ``pyside6-qml``
        :link: pyside6-qml
        :link-type: ref

        to enable quick prototyping with QML files. This tool mimics some of
        the capabilities of Qt's ``QML`` runtime utility by
        directly invoking QQmlEngine/QQuickView.

Translations
~~~~~~~~~~~~

.. grid:: 2
    :gutter: 3 3 4 5

    .. grid-item-card:: ``pyside6-linguist``
        :link: pyside6-linguist
        :link-type: ref

        for translating text in applications.

    .. grid-item-card:: ``pyside6-lrelease``
        :link: pyside6-lrelease
        :link-type: ref

        to create run-time translation files for the application.

    .. grid-item-card:: ``pyside6-lupdate``
        :link: pyside6-lupdate
        :link-type: ref

        to synchronize source code and translations.

Qt Help
~~~~~~~

.. grid:: 2
    :gutter: 3 3 4 5

    .. grid-item-card:: ``pyside6-assistant``
        :link: pyside6-assistant
        :link-type: ref

        for viewing online documentation in Qt Help file format.
        Read more about the formats on the `QtHelp Framework`_ page.

.. _`QtHelp Framework`: https://doc.qt.io/qt-6/qthelp-framework.html

PySide Utilities
~~~~~~~~~~~~~~~~

.. grid:: 2
    :gutter: 3 3 4 5

    .. grid-item-card:: ``pyside6-genpyi``
        :link: pyside6-genpyi
        :link-type: ref

        to generate Python stubs (``.pyi`` files) for Qt modules.

    .. grid-item-card:: ``pyside6-metaobjectdump``
        :link: pyside6-metaobjectdump
        :link-type: ref

        a tool to print out the metatype information in JSON to be used as
        input for ``qmltyperegistrar``.

Deployment
~~~~~~~~~~

.. grid:: 2
    :gutter: 3 3 4 5

    .. grid-item-card:: ``pyside6-deploy``
        :link: pyside6-deploy
        :link-type: ref

        to deploy PySide6 applications to desktop platforms - Linux, Windows
        and macOS.

    .. grid-item-card:: ``pyside6-android-deploy``
        :link: pyside6-android-deploy
        :link-type: ref

        to deploy PySide6 application as an Android app targeting different
        Android platforms - aarch64, armv7a, i686, x86_64.

Shader Tools
~~~~~~~~~~~~

.. grid:: 2
    :gutter: 3 3 4 5

    .. grid-item-card:: ``pyside6-qsb``
        :link: pyside6-qsb
        :link-type: ref

        a command-line tool provided by the Qt Shader Tools modules to
        generate and inspect .qsb files.

Qt Quick 3D
~~~~~~~~~~~

.. grid:: 2
    :gutter: 3 3 4 5

    .. grid-item-card:: ``pyside6-balsam``
        :link: pyside6-balsam
        :link-type: ref

        a command line tool that takes assets created in digital content
        creation tools like Maya, 3ds Max or Blender and converts them into an
        efficient runtime format for use with Qt Quick 3D.

    .. grid-item-card:: ``pyside6-balsamui``
        :link: pyside6-balsamui
        :link-type: ref

        a graphical user interface for the ``pyside6-balsam`` tool.
