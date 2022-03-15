Provides an API to make serial programming simple and portable.

Qt Serial Port provides the basic functionality, which includes configuring,
I/O operations, getting and setting the control signals of the RS-232 pinouts.

The following items are not supported by this module:

    * Terminal features, such as echo, control CR/LF, and so on.
    * Text mode.
    * Configuring timeouts and delays while reading or writing.
    * Pinout signal change notification.

To include the definitions of modules classes, use the following
directive:

::

    import PySide6.QtSerialPort
