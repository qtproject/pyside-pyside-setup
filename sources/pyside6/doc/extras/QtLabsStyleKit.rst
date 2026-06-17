StyleKit is a declarative styling system for :mod:`PySide6.QtQuickControls2`,
built on top of `Qt Quick Templates`_. It lets you define a complete visual
style for all your controls from a single `Style`_ object, including support
for `themes`_, `state-based`_ styling, and `transitions`_. StyleKit handles the
underlying template implementation automatically, letting you focus purely on
visual aspects such as `colors`_, `dimensions`_, `borders`_, and `shadows`_.

A key strength of StyleKit is its hierarchical property system: set a property
once on a base type like `abstractButton`_, and it automatically applies to all
button-like controls. Override it where needed for specific controls or states.
Changes to your style are instantly reflected across all controls, ensuring
consistency while still allowing fine-grained customization.

For controls that need custom behavior beyond what StyleKit provides, you can
still implement custom templates and integrate them seamlessly alongside
StyleKit-styled controls.

Key Features
^^^^^^^^^^^^

* **Declarative Styling** - An easy-to-use QML API that lets you focus on design over implementation
* **Hierarchical Fallbacks** - All properties propagate. Set them once, override where needed
* **State-Based Styling** - Design separate appearances for hovered, pressed, focused, etc.
* **Animated Transitions** - Define smooth animations between states
* **Theme Support** - Design light and dark themes, and any number of custom themes
* **Variations** - Design multiple variations of the same controls
* **Palette and Font Integration** - Configure control palettes and fonts using QML

The following example shows a minimal example of a Style:

.. code-block:: javascript

    // PlainStyle.qml
    import QtQuick
    import Qt.labs.StyleKit

    Style {
        control {
            padding: 6
            background {
                radius: 4
                implicitWidth: 100
                implicitHeight: 36
            }
            indicator {
                implicitWidth: 20
                implicitHeight: 20
                border.width: 1
            }
            handle {
                implicitWidth: 20
                implicitHeight: 20
                radius: 10
            }
        }

        button {
            background {
                implicitWidth: 120
                shadow.opacity: 0.6
                shadow.verticalOffset: 2
                shadow.horizontalOffset: 2
                gradient: Gradient {
                    GradientStop { position: 0.0; color: Qt.alpha("black", 0.0)}
                    GradientStop { position: 1.0; color: Qt.alpha("black", 0.2)}
                }
            }
            pressed.background.scale: 0.95
        }

        slider {
            indicator.fillWidth: true
            indicator.implicitHeight: 6
            indicator.radius: 3
        }

        light: Theme {
            applicationWindow {
                background.color: "whitesmoke"
            }
            control {
                text.color: "black"
                background.color: "#e8e8e8"
                background.border.color: "#c0c0c0"
                hovered.background.color: "#d0d0d0"
            }
            button {
                text.color: "white"
                background.color: "cornflowerblue"
                background.shadow.color: "gray"
                hovered.background.color: "royalblue"
            }
        }

        dark: Theme {
            applicationWindow {
                background.color: Qt.darker("gray", 2.0)
            }
            control {
                text.color: "white"
                background.color: "#3a3a3a"
                background.border.color: "#555555"
                hovered.background.color: "#4a4a4a"
            }
            button {
                background.color: "sandybrown"
                background.shadow.color: "black"
                hovered.background.color: Qt.darker("sandybrown", 1.2)
            }
        }
    }

This is how to set the style in your application:

.. code-block:: javascript

    // Main.qml
    import QtQuick
    import Qt.labs.StyleKit

    ApplicationWindow {
        id: app
        width: 1024
        height: 800
        visible: true

        // Assign the style to be used
        StyleKit.style: PlainStyle {}

        // Controls are used as normal
        Column {
            anchors.fill: parent
            anchors.margins: 10
            spacing: 10
            Button {
                text: "Button"
            }
            Slider {
                width: 200
            }
        }
    }

Using the Module
^^^^^^^^^^^^^^^^

To include the definitions of modules classes, use the following directive:

.. code-block:: python

    import PySide6.QtLabsStyleKit

The QML types of the module are available through the ``QtQuick.labs.StyleKit``
import. To use the types, add the following import statement to your ``.qml`` file:

.. code-block:: javascript

    import Qt.labs.StyleKit

Articles and Guides
^^^^^^^^^^^^^^^^^^^

* :ref:`StyleKit-Features-Overview` - A brief introduction to the available styling features
* :ref:`StyleKit-Property-Resolution` - How StyleKit resolves style property values
* :ref:`Reference-Fallback-Style`

.. _`Qt Quick Templates`: https://doc.qt.io/qt-6/qtquicktemplates2-index.html
.. _`Style`: https://doc.qt.io/qt-6/qml-qt-labs-stylekit-style.html
.. _`themes`: https://doc.qt.io/qt-6/qml-qt-labs-stylekit-theme.html
.. _`state-based`: https://doc.qt.io/qt-6/qml-qt-labs-stylekit-controlstatestyle.html
.. _`transitions`: https://doc.qt.io/qt-6/qml-qt-labs-stylekit-controlstyleproperties.html#transition-prop
.. _`colors`: https://doc.qt.io/qt-6/qml-qt-labs-stylekit-delegatestyle.html#color-prop
.. _`dimensions`: https://doc.qt.io/qt-6/qml-qt-labs-stylekit-delegatestyle.html#implicitWidth-prop
.. _`borders`: https://doc.qt.io/qt-6/qml-qt-labs-stylekit-delegatestyle.html#border-prop
.. _`shadows`: https://doc.qt.io/qt-6/qml-qt-labs-stylekit-delegatestyle.html#shadow-prop
.. _`abstractButton`: https://doc.qt.io/qt-6/qml-qt-labs-stylekit-abstractstylablecontrols.html#abstractButton-prop
