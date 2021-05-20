Manipulating Documentation
--------------------------

inject-documentation
^^^^^^^^^^^^^^^^^^^^

    The inject-documentation node inserts the documentation into the generated
    documentation. This node is a child of the :ref:`object-type`,
    :ref:`value-type` and :ref:`modify-function` nodes.

    .. code-block:: xml

         <value-type>
             <inject-documentation mode="append | prepend | replace" format="native | target" >
                 // the documentation
             </inject-code>
         </value-type>

    The **mode** attribute default value is *replace*.

    The **format** attribute specifies when the documentation injection will
    occur and it accepts the following values:

        * native: Before XML<->Backend transformation occur, so the injected code *must* be a valid XML.
        * target: After XML<->Backend transformation occur, so the injected code *must* be a valid backend format.

    At the moment the only supported backend is Sphinx.

modify-documentation
^^^^^^^^^^^^^^^^^^^^

    The modify-documentation node allows you to change the auto-generated
    documentation. . This node is a child of the :ref:`object-type`,
    :ref:`value-type` and :ref:`modify-function` nodes.
    API Extractor transforms XML's from `qdoc`_ (the Qt documentation
    tool) into .rst files to be processed later using `Sphinx`_. You can modify
    the XML before the transformation takes place.

.. _`qdoc`: https://doc.qt.io/qt-6/qdoc-index.html

.. _`Sphinx`: https://www.sphinx-doc.org/en/master

    .. code-block:: xml

        <modify-documentation xpath="...">
            <!-- new documentation -->
        </modify-documentation>

    The **xpath** attribute is the `XPath`_ to the node that you want to modify.

.. _`XPath`: https://www.w3.org/TR/1999/REC-xpath-19991116/
