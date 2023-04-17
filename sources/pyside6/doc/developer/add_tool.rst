.. _developer-add-tool:

Add a new tool or a Qt tool wrapper
===================================

Tooling is essential to |project|, for that reason you can find many ad-hoc
tools in the repository, which include wrappers of Qt tools or newly developed
tools to solve issues, or improve some project workflows.

Add a new tool
--------------

Tools not available to end users
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This depicts the tools that are not shipped with Qt for Python wheels and are used to aid
Qt for Python development

- Place your tool in the ``tools`` directory.
- If your project has more than one file, create a directory.
- Create a ``.pyproject`` file including all the relevant files
  for your tool.

Tools available to end users
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Place your tool in the ``sources/pyside-tools`` directory.
- If your project has more than one file, create a directory.
- Create a ``.pyproject`` file including all the relevant files
  for your tool.
- Add the relevant files in ``sources/pyside-tools/CMakeLists.txt``.
- Add the tool in ``sources/pyside-tools/pyside_tool.py``.
- Add the tool in ``build_scripts/__init__.py`` to create the setuptools entry points
  i.e. this enable using the tool from the console as "pyside6-<tool_name>"
- Add an entry to ``sources/pyside6/doc/gettingstarted/package_details.rst``.
- Include the necessary Qt binaries explicitly on ``build_scripts/wheel_files.py``
- Build with ``--standalone``, verify it is working.


Add a Qt tool wrapper
---------------------

- Add the relevant files in ``sources/pyside-tools/CMakeLists.txt``.
- Add the tool in ``sources/pyside-tools/pyside_tool.py``.
- Add the tool in ``build_scripts/__init__.py`` to create the setuptools entry points
  i.e. this enable using the tool from the console as "pyside6-<tool_name>"
- Add an entry to ``sources/pyside6/doc/gettingstarted/package_details.rst``.
- Include the necessary Qt binaries explicitly on ``build_scripts/wheel_files.py``
- Build with ``--standalone``, verify it is working.
