.. _pyside6-qsb:

pyside6-qsb
===========

``pyside6-qsb`` is a tool that wraps the `qsb <QSB Manual>`_ tool. qsb is a
command line tool provided by the `Qt Shader Tools`_ module. It integrates
third-party libraries such as `glslang`_ and `SPIRV-Cross`_, optionally invokes
external tools, such as ``fxc`` or ``spirv-opt``, and generates .qsb files.
Additionally, it can be used to inspect the contents of a .qsb package.

For more information on how to use this tool, read Qt's documentation
here: `QSB Manual`_.

Usage
-----

To create a qsb file from a shader file, e.g., ``shader.frag``, use the
following command:

.. code-block:: bash

    pyside6-qsb -o shader.frag.qsb shader.frag

To inspect the file produced, i.e., ``shader.frag.qsb``, use the following
command:

.. code-block:: bash

    pyside6-qsb -d shader.frag.qsb

This will print the reflection metadata (in JSON form) and the included shaders.

For other modes of operation, refer to the `QSB Manual`_.

.. _`glslang`: https://github.com/KhronosGroup/glslang
.. _`spirv-cross`: https://github.com/KhronosGroup/SPIRV-Cross
.. _`QSB Manual`: https://doc.qt.io/qt-6/qtshadertools-qsb.html
.. _`Qt Shader Tools`: https://doc.qt.io/qt-6/qtshadertools-index.html
