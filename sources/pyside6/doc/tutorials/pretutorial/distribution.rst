.. _distribution:

Distributing Your Application to Other Systems/Platforms
========================================================

After developing a couple of applications, you might want to distribute them to
other users. In case you do not have much experience with Python packages, you
might have even asked: *How do I create a Python executable?*.

If you come from compiled programming languages, deployment is something
almost trivial, but for Python is a bit difficult.

The deployment process for Python applications is called, "freezing", which is
distributing your virtual environment content to other users.

.. important:: As Python does not support WebAssembly and mobile platforms,
   such as Android and iOS, you cannot deploy applications to these platforms
   directly, and you require advanced processes to do so.

.. note:: For embedded systems, you currently need to build |project| for your
   target platform, and deploy the installation alongside your application.

Reproducible deployment
-----------------------

A common approach is to only provide a ``requirements.txt`` file, where you
state your dependencies. Users would need to install them from there
to run your Application.

For example, imagine I have a project with two dependencies, ``module_a`` and
``module_b``, which I use in my ``main.py`` file. So my structure is:

.. code-block:: python

    # Content of the main.py file
    from module_a import something
    import module_b

    # ...

So the ``requirements.txt`` for my application would look like this::

    module_a
    module_b

Later, when a user want to execute your ``main.py``, the dependencies
must be installed using :command:`pip install -r requirements.txt`
in a new virtual environment.

.. important:: You can notice that this approach includes sharing your code
   so it fails if you want to hide the code of your application.

Freezing Your Application
-------------------------

This is the most common approach for users to distribute their applications
and even though the code is still available for the end user, it is a bit more
difficult to retrieve it.

You can find a series of tutorials based on the most popular tools that
allow Python users to freeze and distribute applications in our
:ref:`deployment` section.

Compiling Python
----------------

Even though Python does not natively support to be compiled, there are
complementary tools that let you to achieve this.
You can check the `Nuitka <https://nuitka.net/>`_ project to learn more.
