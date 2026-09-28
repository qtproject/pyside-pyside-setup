.. _overload-removal:

Restricting Function Overloads
------------------------------

Some class member functions have a number of overloads that differ in one parameter:

.. code-block:: c++

    class QByteArray {
    public:
    ...
    static QByteArray number(int, int base = 10);
    static QByteArray number(unsigned int, int base = 10);
    static QByteArray number(long, int base = 10);
    static QByteArray number(unsigned long, int base = 10);
    static QByteArray number(long long, int base = 10);
    static QByteArray number(unsigned long long, int base = 10);
    ...

In this case, it does not make sense to generate a binding for ``QByteArray number(int,...)``
since it is equivalent to ``QByteArray number(long long,...)``.

In the type system file, it is possible to specify a rule stating that the ``int``
overload is to be removed when an ``long long`` overload exists by using
the ``<overload-removal>`` element:

.. code-block:: xml

     <overload-removal type="long long" replaces="int"/>

The ``type`` attribute specifies the preferred type and the
``replaces`` attribute specifies a ';'-delimited list of types to be removed.

.. note:: This is limited to the first 4 arguments of types that are passed by value or const-ref.

.. note:: The rules are applied in the order specified. That is, a rule specifying that ``int``
          replaces ``short`` should go before a rule rule specifying that ``long long`` replaces ``int``.
