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

.. _predefined_templates:

Predefined Templates
--------------------

There are a number of XML templates for conversion rules for STL and Qt types
built into shiboken.

Templates for :ref:`primitive-type`:

    +---------------------------------------+--------------------------------+
    |Name                                   | Description                    |
    +---------------------------------------+--------------------------------+
    | ``shiboken_conversion_pylong_to_cpp`` | Convert a PyLong to a C++ type |
    +---------------------------------------+--------------------------------+

Templates for :ref:`container-type`:

    +----------------------------------------------------------------------+------------------------------------------------------------------------------------+
    | ``shiboken_conversion_pysequence_to_cpppair``                        | Convert a PySequence to a C++ pair (std::pair/QPair)                               |
    +----------------------------------------------------------------------+------------------------------------------------------------------------------------+
    | ``shiboken_conversion_cpppair_to_pytuple``                           | Convert a C++ pair (std::pair/QPair) to a PyTuple                                  |
    +----------------------------------------------------------------------+------------------------------------------------------------------------------------+
    | ``shiboken_conversion_cppsequence_to_pylist``                        | Convert a C++ sequential container to a PyList                                     |
    +----------------------------------------------------------------------+------------------------------------------------------------------------------------+
    | ``shiboken_conversion_cppsequence_to_pyset``                         | Convert a C++ sequential container to a PySet                                      |
    +----------------------------------------------------------------------+------------------------------------------------------------------------------------+
    | ``shiboken_conversion_pyiterable_to_cppsequentialcontainer``         | Convert an iterable Python type to a C++ sequential container (STL/Qt)             |
    +----------------------------------------------------------------------+------------------------------------------------------------------------------------+
    | ``shiboken_conversion_pyiterable_to_cppsequentialcontainer_reserve`` | Convert an iterable Python type to a C++ sequential container supporting reserve() |
    +----------------------------------------------------------------------+------------------------------------------------------------------------------------+
    | ``shiboken_conversion_pyiterable_to_cppsetcontainer``                | Convert a PySequence to a set-type C++ container (std::set/QSet)                   |
    +----------------------------------------------------------------------+------------------------------------------------------------------------------------+
    | ``shiboken_conversion_stdmap_to_pydict``                             | Convert a std::map/std::unordered_map to a PyDict                                  |
    +----------------------------------------------------------------------+------------------------------------------------------------------------------------+
    | ``shiboken_conversion_qmap_to_pydict``                               | Convert a QMap/QHash to a PyDict                                                   |
    +----------------------------------------------------------------------+------------------------------------------------------------------------------------+
    | ``shiboken_conversion_pydict_to_stdmap``                             | Convert a PyDict to a std::map/std::unordered_map                                  |
    +----------------------------------------------------------------------+------------------------------------------------------------------------------------+
    | ``shiboken_conversion_pydict_to_qmap``                               | Convert a PyDict to a QMap/QHash                                                   |
    +----------------------------------------------------------------------+------------------------------------------------------------------------------------+
    | ``shiboken_conversion_stdmultimap_to_pydict``                        | Convert a std::multimap to a PyDict of value lists                                 |
    +----------------------------------------------------------------------+------------------------------------------------------------------------------------+
    | ``shiboken_conversion_qmultimap_to_pydict``                          | Convert a QMultiMap to a PyDict of value lists                                     |
    +----------------------------------------------------------------------+------------------------------------------------------------------------------------+
    | ``shiboken_conversion_stdunorderedmultimap_to_pydict``               | Convert a std::unordered_multimap to a PyDict of value lists                       |
    +----------------------------------------------------------------------+------------------------------------------------------------------------------------+
    | ``shiboken_conversion_qmultihash_to_pydict``                         | Convert a QMultiHash to a PyDict of value lists                                    |
    +----------------------------------------------------------------------+------------------------------------------------------------------------------------+
    | ``shiboken_conversion_pydict_to_stdmultimap``                        | Convert a PyDict of value lists to std::multimap/std::unordered_multimap           |
    +----------------------------------------------------------------------+------------------------------------------------------------------------------------+
    | ``shiboken_conversion_pydict_to_qmultihash``                         | Convert a PyDict of value lists to QMultiMap/QMultiHash                            |
    +----------------------------------------------------------------------+------------------------------------------------------------------------------------+

An entry for the type ``std::list`` using these templates looks like:

.. code-block:: xml

    <container-type name="std::list" type="list">
        <include file-name="list" location="global"/>
        <conversion-rule>
            <native-to-target>
                <insert-template name="shiboken_conversion_cppsequence_to_pylist"/>
            </native-to-target>
            <target-to-native>
                <add-conversion type="PySequence">
                    <insert-template name="shiboken_conversion_pyiterable_to_cppsequentialcontainer"/>
                </add-conversion>
            </target-to-native>
        </conversion-rule>
    </container-type>

.. note:: From version 6.3, we do not have to explicitly specify the
          `<container-type/>` for C++ containers ``std::list``\, ``std::vector``\,
          ``std::pair``\, ``std::map`` and ``std::unordered_map``\. They are
          now built-in. However, they still have to be added for opaque
          containers or when modifying the built-in behavior.
