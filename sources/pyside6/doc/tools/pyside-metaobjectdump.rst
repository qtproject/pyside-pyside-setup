.. _pyside6-metaobjectdump:

pyside6-metaobjectdump
======================

``pyside6-metaobjectdump`` is a command line tool. It scans Python source
files and dumps out information on classes to be registered with QML in
JSON-format. This serves as input for the :ref:`pyside6-qmltyperegistrar` tool.

The tool is the equivalent of the `moc`_ tool in Qt / C++.

It is automatically run by the :ref:`pyside6-project` tool
when passing the ``qmllint`` argument instructing it to check
the QML source files.

Usage
-----

Classes to be registered with QML are indicated by QML decorators
like :deco:`QmlElement`. Invoking:

.. code-block:: bash

    pyside6-metaobjectdump birthdayparty.py

produces the JSON data on stdout:

.. code-block:: json

    [
        {
            "classes": [
                {
                    "className": "BirthdayParty",
                    "qualifiedClassName": "BirthdayParty",
                    "object": true,
                    "superClasses": [
                        {
                            "access": "public",
                            "name": "QObject"
                        }
                    ],
                    "classInfos": [
                        {
                            "name": "QML.Element",
                            "value": "auto"
                        }
                    ],
                    "properties": [
                        {
                            "name": "host",
                            "type": "Person",
                            "index": 0,
                            "read": "host",
                            "notify": "host_changed",
                            "write": "host"
                        },
                        {
                            "name": "guests",
                            "type": "QQmlListProperty<Person>",
                            "index": 1
                        }
                    ],
                    "signals": [
                        {
                            "access": "public",
                            "name": "host_changed",
                            "arguments": [],
                            "returnType": "void"
                        },
                        {
                            "access": "public",
                            "name": "guests_changed",
                            "arguments": [],
                            "returnType": "void"
                        }
                    ]
                }
            ],
            "outputRevision": 68,
            "QML_IMPORT_NAME": "People",
            "QML_IMPORT_MAJOR_VERSION": 1,
            "QML_IMPORT_MINOR_VERSION": 0,
            "QT_MODULES": [
                "QtCore",
                "QtQml"
            ],
            "inputFile": ".../examples/qml/tutorials/extending-qml-advanced/advanced1-Base-project/birthdayparty.py"
        }
    ]

.. _`moc`: https://doc.qt.io/qt-6/moc.html
