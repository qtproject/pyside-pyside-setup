.. _using-code-templates:

Using Code Templates
--------------------

.. _template:

template
^^^^^^^^

    The ``template`` node registers a template that can be used to avoid
    duplicate code when extending the generated code, and it is a child of the
    :ref:`typesystem` node.

    .. code-block:: xml

        <typesystem>
            <template name="my_template">
                // the code
            </template>
        </typesystem>

    Use the ``insert-template`` node to insert the template code (identified
    by the template's ``name`` attribute) into the generated code base.

.. _insert-template:

insert-template
^^^^^^^^^^^^^^^

    The ``insert-template`` node includes the code template identified by the
    name attribute, and it can be a child of the :ref:`inject-code`,
    :ref:`conversion-rule` or :ref:`template` nodes.

    .. code-block:: xml

         <inject-code class="target" position="beginning">
             <insert-template name="my_template" />
         </inject-code>

    Use the ``replace`` node to modify the template code.

replace
^^^^^^^

    The ``replace`` node allows you to modify template code before inserting it into
    the generated code, and it can be a child of the :ref:`insert-template` node.

    .. code-block:: xml

        <insert-template name="my_template">
           <replace from="..." to="..." />
        </insert-template>

    This node will replace the attribute ``from`` with the value pointed by
    ``to``.

