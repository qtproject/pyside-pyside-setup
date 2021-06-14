.. _modifying-functions:

Modifying Functions
-------------------

.. _modify-argument:

modify-argument
^^^^^^^^^^^^^^^

    Function modifications consist of a list of ``modify-argument`` nodes
    contained in a :ref:`modify-function` node.  Use the :ref:`remove-argument`,
    :ref:`replace-default-expression`, :ref:`remove-default-expression`,
    :ref:`replace-type`, :ref:`reference-count` and :ref:`define-ownership`
    nodes to specify the details of the modification.

    .. code-block:: xml

         <modify-function>
             <modify-argument index="return | this | 1 ..." rename="..."
              invalidate-after-use = "true | false" pyi-type="...">
                 // modifications
             </modify-argument>
         </modify-function>

    Set the ``index`` attribute to "1" for the first argument, "2" for the second
    one and so on. Alternatively, set it to "return" or "this" if you want to
    modify the function's return value or the object the function is called upon,
    respectively.

    The optional ``rename`` attribute is used to rename a argument and use this
    new name in the generated code.

    The optional ``pyi-type`` attribute specifies the type to appear in the
    signature strings and  ``.pyi`` files. The type string is determined by
    checking this attribute value, the :ref:`replace-type` modification and
    the C++ type. The attribute can be used for example to enclose
    a pointer return value within ``Optional[]`` to indicate that ``None``
    can occur.

    For the optional ``invalidate-after-use`` attribute,
    see :ref:`invalidationafteruse` .
