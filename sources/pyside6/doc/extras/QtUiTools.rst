*Qt Widgets Designer* forms are processed at run-time to produce
dynamically-generated user interfaces. In order to generate a form at
run-time, a resource file containing a UI file is needed.

A form loader object, provided by the ``QUiLoader`` class, is used to
construct the user interface. This user interface can be retrieved
from any ``QIODevice``; for example, a ``QFile`` object can be used to obtain
a form stored in a project's resources. The
:meth:`PySide6.QtUiTools.QUiLoader.load` function takes the user
interface description contained in the file and constructs the form
widget.

To include the definitions of the module's classes, use the following directive:

::

    import PySide.QtUiTools

Security Considerations
^^^^^^^^^^^^^^^^^^^^^^^

Only load forms from trusted sources, like the
:ref:`Qt resource system <tutorial_qrcfiles>`.

Loading ''.ui'' files from untrusted sources can lead to security
threats in your application, such as denial of service attacks,
UI deception, or the loading of unexpected plugins.
