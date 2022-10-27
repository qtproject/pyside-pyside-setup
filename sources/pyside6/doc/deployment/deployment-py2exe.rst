|project| & py2exe
##################

Deploying an application using py2exe requires writing a small `setup.py` file.
It is explained in the `Tutorial <http://www.py2exe.org/index.cgi/Tutorial>`_.

py2exe is not generally aware of Qt. It merely copies the dependent libraries
of the application to the `dist` directory, so, the plugins, QML imports
and translations of Qt are missing.

The latter need to be copied manually after running py2exe.
This can be achieved by running the `windeployqt` tool
from the Qt SDK on the Qt libraries present in the `dist` directory,
for example:

   windeployqt dist\\Qt6Widgets.dll
