.. _pyside6-balsam:

pyside6-balsam
==============

``pyside6-qsb`` is a tool that wraps the `balsam <Balsam Asset Import Tool>`_
tool provided with Qt Quick 3D. The Balsam tool is a command line application
that is part of Qt Quick 3D's asset conditioning pipeline. The purpose is to
take assets created in digital content creation tools like `Maya`_, `3ds Max`_
or `Blender`_ and converts them into an efficient runtime format for use with Qt
Quick 3D. It is not possible, nor does it make sense to reference the
interchange formats directly in applications because a large amount of
resources are needed to parse and condition the content of the asset before it
is usable for real-time rendering. Instead, the interchange formats can be
converted via the Balsam tool into QML Components and resources like geometry
and textures.


For more information on how to use this tool, read Qt's documentation
here: `Balsam Asset Import Tool`_.

Usage
-----

.. code-block:: bash

    pyside6-balsam [options] sourceFileName

To convert a 3D asset contained in the file ``testModel.fbx`` with
``pyside6-balsam`` the following command would be used:

.. code-block:: bash

    pyside6-balsam testModel.fbx

This would generate the following files:

* meshes/testModel.mesh
* TestModel.qml

Which can then be used in a Qt Quick 3D project by using that QML Component:

.. code-block:: xml

    import QtQuick3D 1.0

    Scene {
        Model {
            source: "TestModel.qml"
        }
    }

For other modes of operation, refer to the `Balsam Asset Import Tool`_.

.. _`Balsam Asset Import Tool`: https://doc.qt.io/qt-6/qtquick3d-tool-balsam.html
.. _Maya: https://www.autodesk.com/products/maya/overview
.. _3ds Max: https://www.autodesk.com/products/3ds-max/overview
.. _Blender: https://www.blender.org/

