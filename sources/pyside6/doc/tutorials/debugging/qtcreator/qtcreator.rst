Debugging PySide with Qt Creator (Linux)
****************************************

As opposed to VSCode, presently Qt Creator does not support mixed mode debugging.
However, we can debug the C++ implementation of the corresponding Python PySide
code. Unlike VSCode, Qt Creator provides a very easy interface to attach GDB to
the Python interpreter. It saves you from doing all the extra configuration
steps, that have to be done with VSCode.

Here are the steps:

1. Set a breakpoint on the C++ code.

2. Go to Projects -> Run -> Run Configuration -> Add. This is going to open a
   new window shown below.

    .. image:: custom_executable_create.png
        :alt: creation of custom executable
        :align: center

3. Click on Custom Executable and `Create` a new configuration. Feed in the
details like shown below.

    .. image:: custom_executable_run_config.png
        :alt: run configuration of custom executable
        :align: center

4. Debug -> Start Debugging -> Start Debugging Without Deployment.

    .. image:: start_debugging_without_deployment.png
        :alt: start debugging without deployment
        :align: center

You will now hit you breakpoint and can start debugging your code.

    .. image:: breakpoint_cpp.png
        :alt: breakpoint cpp
        :align: center

