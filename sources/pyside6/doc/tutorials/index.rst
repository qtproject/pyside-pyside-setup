|project| Tutorials
====================

A collection of tutorials with walkthrough guides are
provided with |project| to help new users get started.

Some of these documents were ported from C++ to Python and cover a range of
topics, from basic use of widgets to step-by-step tutorials that show how an
application is put together.

Before you start
----------------

Here you can find a couple of common questions and situations that will
clarify questions before you start programming.
If you have not installed PySide yet, remember to check the
`Quick Start <../quickstart.html>`_ section.

.. panels::
    :container: container-lg pb-1
    :column: col-lg-4 col-md-4 col-sm-6 col-xs-12 p-2

    .. link-button:: pretutorial/whatisqt
        :type: ref
        :text: Qt, QML, Widgets... What is the difference?
        :classes: btn-link btn-block stretched-link
    ---

    .. link-button:: pretutorial/whichide
        :type: ref
        :text: Which IDEs are compatible with PySide?
        :classes: btn-link btn-block stretched-link
    ---

    .. link-button:: pretutorial/whatisshiboken
        :type: ref
        :text: Binding Generation: What is Shiboken?
        :classes: btn-link btn-block stretched-link
    ---

    .. link-button:: pretutorial/typesoffiles
        :type: ref
        :text: File Types in PySide
        :classes: btn-link btn-block stretched-link
    ---

    .. link-button:: pretutorial/distribution
        :type: ref
        :text: Distributing your application to other systems and platforms
        :classes: btn-link btn-block stretched-link

    ---

    .. link-button:: pretutorial/whyqtforpython
        :type: ref
        :text: As a Qt/C++ developer, why should I consider Qt for Python?
        :classes: btn-link btn-block stretched-link

.. toctree::
    :hidden:

    pretutorial/whatisqt.rst
    pretutorial/whichide.rst
    pretutorial/whatisshiboken.rst
    pretutorial/typesoffiles.rst
    pretutorial/distribution.rst
    pretutorial/whyqtforpython.rst

Qt Widgets: Basic tutorials
---------------------------

If you want to see the available widgets in action, you can check the
`Qt Widget Gallery <https://doc.qt.io/qt-6/gallery.html>`_ to learn their
names and how they look like.

.. panels::
    :container: container-lg pb-1
    :column: col-lg-4 col-md-4 col-sm-6 col-xs-12 p-2
    :img-top-cls: d-flex align-self-center

    :img-top: basictutorial/widgets.png

    .. link-button:: basictutorial/widgets
        :type: ref
        :text: Your First QtWidgets Application
        :classes: btn-link btn-block stretched-link
    ---
    :img-top: basictutorial/clickablebutton.png

    .. link-button:: basictutorial/clickablebutton
        :type: ref
        :text: Using a Simple Button
        :classes: btn-link btn-block stretched-link
    ---
    :img-top: basictutorial/signals_slots.png

    .. link-button:: basictutorial/signals_and_slots
        :type: ref
        :text: Signals and Slots
        :classes: btn-link btn-block stretched-link
    ---
    :img-top: basictutorial/dialog.png

    .. link-button:: basictutorial/dialog
        :type: ref
        :text: Creating a Dialog Application
        :classes: btn-link btn-block stretched-link
    ---
    :img-top: basictutorial/tablewidget.png

    .. link-button:: basictutorial/tablewidget
        :type: ref
        :text: Displaying Data Using a Table Widget
        :classes: btn-link btn-block stretched-link

    ---
    :img-top: basictutorial/treewidget.png

    .. link-button:: basictutorial/treewidget
        :type: ref
        :text: Displaying Data Using a Tree Widget
        :classes: btn-link btn-block stretched-link

    ---
    :img-top: basictutorial/uifiles.png

    .. link-button:: basictutorial/uifiles
        :type: ref
        :text: Using .ui files from Designer or QtCreator with QUiLoader and pyside6-uic
        :classes: btn-link btn-block stretched-link

    ---
    :img-top: basictutorial/player-new.png

    .. link-button:: basictutorial/qrcfiles
        :type: ref
        :text: Using .qrc Files (pyside6-rcc)
        :classes: btn-link btn-block stretched-link

    ---
    :img-top: basictutorial/translations.png

    .. link-button:: basictutorial/translations
        :type: ref
        :text: Translating Applications
        :classes: btn-link btn-block stretched-link

    ---
    :img-top: basictutorial/widgetstyling-yes.png

    .. link-button:: basictutorial/widgetstyling
        :type: ref
        :text: Styling the Widgets Application
        :classes: btn-link btn-block stretched-link


.. toctree::
    :hidden:

    basictutorial/widgets.rst
    basictutorial/clickablebutton.rst
    basictutorial/signals_and_slots.rst
    basictutorial/dialog.rst
    basictutorial/tablewidget.rst
    basictutorial/treewidget.rst
    basictutorial/uifiles.rst
    basictutorial/qrcfiles.rst
    basictutorial/translations.rst
    basictutorial/widgetstyling.rst


Quick/QML: Basic tutorials
--------------------------

.. panels::
    :container: container-lg pb-1
    :column: col-lg-4 col-md-4 col-sm-6 col-xs-12 p-2
    :img-top-cls: d-flex align-self-center

    :img-top: basictutorial/greenapplication.png

    .. link-button:: basictutorial/qml
        :type: ref
        :text: Your First QtQuick/QML Application
        :classes: btn-link btn-block stretched-link
    ---
    :img-top: qmlintegration/textproperties_material.png

    .. link-button:: qmlintegration/qmlintegration
        :type: ref
        :text: Python-QML integration
        :classes: btn-link btn-block stretched-link
    ---
    :img-top: qmlapp/qmlapplication.png

    .. link-button:: qmlapp/qmlapplication
        :type: ref
        :text: QML Application Tutorial (QtCreator)
        :classes: btn-link btn-block stretched-link
    ---
    :img-top: qmlsqlintegration/example_list_view.png

    .. link-button:: qmlsqlintegration/qmlsqlintegration
        :type: ref
        :text: QML, SQL and PySide Integration Tutorial
        :classes: btn-link btn-block stretched-link


.. toctree::
    :maxdepth: 1
    :hidden:

    basictutorial/qml.rst
    qmlintegration/qmlintegration.rst
    qmlapp/qmlapplication.rst
    qmlsqlintegration/qmlsqlintegration.rst

General Applications
--------------------

.. panels::
    :container: container-lg pb-1
    :column: col-lg-4 col-md-4 col-sm-6 col-xs-12 p-2
    :img-top-cls: d-flex align-self-center

    :img-top: datavisualize/images/datavisualization_app.png

    .. link-button:: datavisualize/index
        :type: ref
        :text: Data Visualization Tool
        :classes: btn-link btn-block stretched-link
    ---
    :img-top: expenses/expenses_tool.png

    .. link-button:: expenses/expenses
        :type: ref
        :text: Expenses Tool
        :classes: btn-link btn-block stretched-link

.. toctree::
    :hidden:

    datavisualize/index.rst
    expenses/expenses.rst


C++ and Python
--------------

.. toctree::
    :maxdepth: 1

    portingguide/index.rst
