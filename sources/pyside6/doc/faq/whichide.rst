.. _whichide:

Which IDEs Are Compatible?
==========================

|project|, as any other Python module, can be used in any Python-compatible
IDE, but not all of them will provide extra functionality like `Qt Creator`_ does.

Besides writing files, there are some external steps you might want to perform
in order to help the development of your applications:

From a terminal:

* Generating a Python file from a ``.ui`` file:
  :command:`pyside6-uic form.ui -o ui_form.py`
* Generating a Python file from a ``.qrc`` file:
  :command:`pyside6-rcc resources.qrc -o rc_resources.py`
* Opening `Qt Widgets Designer`_ with the command :command:`pyside6-designer`
  to edit/create ``.ui`` files (see :ref:`tutorial_uifiles`).

External add-ons/plugins from your favorite IDE might include configuration
steps to run these commands, or open external tools like
`Qt Widgets Designer`_ and `Qt Creator`_.

QtCreator
---------

You can create new projects based on some basic templates that are currently
available in `Qt Creator`_. After selecting one, you will pass through some steps
where you can specify the details of the template, like the project name,
base Qt class to use for your interface, among others.

Here you can see an animation of the creation of a project:

.. image:: https://qt-wiki-uploads.s3.amazonaws.com/images/7/7c/Qtcreator.gif
    :alt: Qt Creator Animation

More information can be found at `Develop Qt for Python applications`_.

Visual Studio Code
------------------

For *Visual Studio Code*, we recommend using the :ref:`vscode-ext`.

PyCharm
-------

You can configure PyCharm to enable external tools, in |project| terms,
*Qt Widgets Designer*, and *Qt Creator*. Go to
``File > Settings > tools > PyCharm External Tools``, and include the following
information to add them to your project.
Later, you will be able to right click a ``.ui`` file, and select
``Qt Widgets Designer``, ``pyside6-uic``, or any tool that you configured this
way.

.. _`Qt Creator`: https://doc.qt.io/qtcreator
.. _`Develop Qt for Python applications`: https://doc.qt.io/qtcreator/creator-python-development.html
.. _`Qt Widgets Designer`: https://doc.qt.io/qt-6/qtdesigner-manual.html
