The Qt XML module provides implementations of the SAX and DOM standards for XML.

.. note::  Qt XML will no longer receive additional features. For reading or writing XML documents iteratively (SAX), use the :class:`QXmlStreamReader<PySide6.QtCore.QXmlStreamReader>` and :class:`QXmlStreamWriter<PySide6.QtCore.QXmlStreamWriter>` classes. The classes are both easier to use and more compliant with the XML standard.

Using the Module
^^^^^^^^^^^^^^^^

To include the definitions of modules classes, use the following
directive:

::

    import PySide6.QtXml
