.. _tutorial_qmlapplication:

#########################
QML Application Tutorial
#########################

This tutorial provides a quick walk-through of a python application
that loads a QML file. QML is a declarative language that lets you
design UIs faster than a traditional language, such as C++. The
QtQml and QtQuick modules provides the necessary infrastructure for
QML-based UIs.

In this tutorial, you'll also learn how to provide data from Python
as a QML initial property, which is then consumed by the ListView
defined in the QML file.

Before you begin, install *Qt Creator* from
`https://download.qt.io <https://download.qt.io/snapshots/qtcreator/>`_.

`Develop Qt for Python applications`_ describes how Python installations
are handled by *Qt Creator*. By default, *Qt Creator* will prompt you
to install PySide6 at the appropriate places.

The following step-by-step instructions guide you through application
development process using *Qt Creator*:

#. Open *Qt Creator* and select **File > New File or Project..** menu item
   to open following dialog:

   .. image:: newpyproject.webp

#. Select **Qt for Python - Empty** from the list of application templates
   and select **Choose**.

   .. image:: pyprojname.webp

#. Give a **Name** to your project, choose its location in the
   filesystem, and select **Finish** to create an empty ``main.py``
   and ``pyproject.toml``.

   .. image:: pyprojxplor.webp

   This should create a ``main.py`` and ```pyproject.toml`` files
   for the project.

#. Download :download:`Main.qml<App/Main.qml>`, :download:`qmldir<App/qmldir>`
   and :download:`logo.png <App/logo.png>` and place them in a subdirectory
   named `App` in your project folder. This creates a basic QML module.

#. Double-click on ``pyproject.toml``` to open it in edit mode, and append
   ``view.qml`` and ``logo.png`` to the **files** list. This is how your
   project file should look after this change:

   .. code::

       [project]
       name = "qml-application"

       [tool.pyside6-project]
       files = ["main.py", "App/Main.qml", "App/logo.png", "App/qmldir"]

#. Now that you have the necessary bits for the application, import the
   Python modules in your ``main.py``, and download country data and
   format it:

   .. literalinclude:: main.py
      :linenos:
      :lines: 5-23
      :emphasize-lines: 5-7,12-15

#. Now, set up the application window using
   :ref:`PySide6.QtGui.QGuiApplication<qguiapplication>`, which manages the application-wide
   settings.

   .. literalinclude:: main.py
      :linenos:
      :lines: 5-28
      :emphasize-lines: 21-24

   .. note:: Setting the resize policy is important if you want the
      root item to resize itself to fit the window or vice-a-versa.
      Otherwise, the root item will retain its original size on
      resizing the window.

#. You can now expose the ``data_list`` variable as a QML initial
   property, which will be consumed by the QML ListView item in ``view.qml``.

   .. literalinclude:: main.py
      :linenos:
      :lines: 5-33
      :emphasize-lines: 26-29

#. Load the ``Main.qml`` to the ``QQuickView`` and call ``show()`` to
   display the application window.

   .. literalinclude:: main.py
      :linenos:
      :lines: 5-43
      :emphasize-lines: 31-39

#. Finally, execute the application to start the event loop and clean up.

   .. literalinclude:: main.py
      :linenos:
      :lines: 5-
      :emphasize-lines: 41-43

#. Your application is ready to be run now. Select **Projects** mode to
   choose the Python version to run it.

   .. image:: projectsmode.webp

Run the application by using the ``CTRL+R`` keyboard shortcut to see if it
looks like this:

.. image:: qmlapplication.png

********************
Related information
********************

* `QML Reference <https://doc.qt.io/qt-6/qmlreference.html>`_
* `Develop Qt for Python applications <https://doc.qt.io/qtcreator/creator-python-development.html>`_
* :doc:`../qmlintegration/qmlintegration`

.. _`Develop Qt for Python applications`: https://doc.qt.io/qtcreator/creator-python-development.html
