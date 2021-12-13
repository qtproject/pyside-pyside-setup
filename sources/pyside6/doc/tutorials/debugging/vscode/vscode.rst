Debugging PySide with VSCode (Linux)
************************************

VSCode enables you to use more than one debugger in a single debugging session.
This means that we can use GDB and Python PDB in a single session. With VSCode
you would be able to do the following:

* See the call stacks for both Python and C++ together.
* Put breakpoints in both the Python and the C++ code.
* Step from Python to C++ code and vice versa.

Let's get started with setting up everything and debugging a Python process.

Creating Configurations in launch.json
--------------------------------------

Run -> Add Configuration -> Python -> Python File

This should create a launch.json file which looks like this:

.. code-block:: json

    {
        // Use IntelliSense to learn about possible attributes.
        // Hover to view descriptions of existing attributes.
        // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Python: Current File",
                "type": "python",
                "request": "launch",
                "program": "${file}",
                "console": "integratedTerminal"
            }
        ]
    }

It should already consist of a configuration named "Python: Current File", which
allows us to debug the current open Python file. With a Python virtual
environment, make sure to change the value of "program" to refer to the path of the Python
interpreter inside the virtual environment.

Now, we need to add a configuration to attach the GDB debugger to the Python
process that is already running in debug mode. Let's call it "(gdb) Attach"

.. code-block:: json

    {
        // Use IntelliSense to learn about possible attributes.
        // Hover to view descriptions of existing attributes.
        // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Python: Current File",
                "type": "python",
                "request": "launch",
                "program": "${file}",
                "console": "integratedTerminal"
            }, {
                "name": "(gdb) Attach",
                "type": "cppdbg",
                "request": "attach",
                "program": "/path/to/python",
                "processId": "${command:pickProcess}",
                "MIMode": "gdb", "setupCommands": [
                    {
                        "description": "Enable pretty-printing for gdb",
                        "text": "-enable-pretty-printing",
                        "ignoreFailures": true
                    }
                ]
            }
        ]
    }

Here also make sure that the value of "program" refers to your Python interpreter. We need the
processId to attach the gdb debugger to the process. With
"${command:pickProcess}", we find the processId on the go, as we will see later.

Now, we are ready to debug.

Debug The Process
-----------------

1. Set a breakpoint in the Python code.

2. Go to `Run And Debug` (Ctrl + Shift + D) and run the "python: Current File"
   by clicking the run symbol (green right-arrow). This will hit the breakpoint and
   will halt the Python debugger.

3. Using the drop-down menu change from "python:
   Current File" to "(gdb) Attach". Your setup should now look like this.

    .. image:: breakpoint_gdb.png
        :alt: breakpoint before attach gdb
        :align: center

4. Run "(gdb) Attach" and this should ask you for the processId of the Python
   process to which you want to attach gdb. VSCode also lets you to search for the
   process by its name. .. tip:: You can find the processId by running `ps aux |
   grep python`

    .. image:: find_process_gdb.png
        :alt: find process vscode
        :align: center

5. VSCode will now ask you for superuser permissions. Type 'y' and enter your
   password.

    .. code-block:: bash

        Superuser access is required to attach to a process. Attaching as
        superuser can potentially harm your computer. Do you want to continue?
        [y/N]_

6. That is it. You should now be able to hit the breakpoints that you have set
   on the C++ counterparts.

    .. figure:: audioformat_wrapper.png
        :alt: Breakpoint set on the shiboken wrapper class
        :align: left

        Breakpoint set on the shiboken wrapper class

    .. figure:: audioformat_cpp.png
        :alt: Breakpoint set on C++ implementation
        :align: left

        Breakpoint set on C++ implementation





