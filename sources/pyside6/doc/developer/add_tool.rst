.. _developer-add-tool:

Add a new tool or a Qt tool wrapper
===================================

Tooling is essential to |project|, for that reason you can find many ad-hoc
tools in the repository, which include wrappers of Qt tools or newly developed
tools to solve issues, or improve some project workflows.

Add a new tool
--------------

- Place your tool in the ``tools`` directory.
- If your project has more than one file, create a directory.
- Create a ``.pyproject`` file including all the relevant files
  for your tool.
- If you would like to interface the tool for end users,
  you need to create an entry point for the wheel creation,
  and also copy the files in the wheel creation process.


Add a Qt tool wrapper
---------------------

- Add script and optional library under ``sources/pyside-tools``.
- Install the files (``sources/pyside-tools/CMakeLists.txt``).
- Include the tool in the deprecated 'setup.py bdist_wheel' process:

  - Add the tool in ``build_scripts/__init__.py``.

  - Copy the files to the wheels in ``build_scripts/platforms/*.py``.

  - Add an entry to ``sources/pyside6/doc/gettingstarted/package_details.rst``.

- Include the tool in the new wheel creation process:

  - Add an entry to ``create_wheels.py``.

  - Include the Qt binaries explicitly on ``build_scripts/wheel_files.py``

- Build with ``--standalone``, verify it is working.
