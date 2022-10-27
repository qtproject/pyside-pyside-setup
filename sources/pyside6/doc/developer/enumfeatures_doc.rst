The Set of Enum Features
========================

The development of the new Python enums took the form of a series of patches.
While we put a lot of effort into supporting the old Enums (without promoting
them), it is still possible that someone has a case where they cannot use
the Python enums as they are now. To avoid people setting the environment
flag to disable this completely, we implemented a way to select each
combination of enum functions step by step with a specific set of flags.


The Possible Enum Flags
-----------------------

This is the table of all flags used to control the creation of Python enums.

======================  =====  ======================================================
Flag Name               Value
======================  =====  ======================================================
ENOPT_OLD_ENUM           0x00  (False) Disable new enums
ENOPT_NEW_ENUM           0x01  (True) The default for PySide 6.4, full implementation
ENOPT_INHERIT_INT        0x02  Turn all Enum into IntEnum and Flag into IntFlag
ENOPT_GLOBAL_SHORTCUT    0x04  Re-add shortcuts for global enums
ENOPT_SCOPED_SHORTCUT    0x08  Re-add shortcuts for scoped enums
ENOPT_NO_FAKESHORTCUT    0x10  Don't fake rename (forgiveness mode)
ENOPT_NO_FAKERENAMES     0x20  Don't fake shortcuts (forgiveness mode)
ENOPT_NO_ZERODEFAULT     0x40  Don't use zero default (forgiveness mode)
ENOPT_NO_MISSING         0x80  Don't allow missing values in Enum
======================  =====  ======================================================

Such a set of flags can be defined either by the environment variable
``PYSIDE63_OPTION_PYTHON_ENUM`` or set by the Python variable
``sys.pyside63_option_python_enum`` before PySide6 is imported.
The environment variable also supports arbitrary integer expressions
by using ``ast.literal_eval``.


ENOPT_OLD_ENUM (0x00)
~~~~~~~~~~~~~~~~~~~~~

This option completely disables the new enum implementation.
Even though this is a valid option, we want to avoid it if possible.
The goal is to eventually remove the old implementation. To make this
possible, we have made the individual features of the enum implementation
accessible as flags. This way, if users report problems, we may be able
to provide a temporary solution before extending enum support accordingly.


ENOPT_NEW_ENUM (0x01)
~~~~~~~~~~~~~~~~~~~~~

In a perfect world, no one would choose anything other than this default
setting. Unfortunately, reality is not always like that. That is why
there are the following flags.


The most likely flags needed
----------------------------

If there are errors, they are likely to be the following: Either implicit
assumptions are there that require IntEnum, or global enums are used that
unfortunately cannot be replaced with tricks.


ENOPT_INHERIT_INT (0x02)
~~~~~~~~~~~~~~~~~~~~~~~~

When this flag is set, all ``enum.Enum/enum.Flag`` classes are converted to
``enum.IntEnum/enum.IntFlag``. This solves the most likely compatibility
problem when switching to Python enums. The old Shiboken enums always
inherit from int, but most Python enums do not.

It was a decision of Python developers not to let enums inherit from int by
default, since no order should be implied. In most cases, inheritance from
int can be avoided, either by using the value property or better by
uplifting: instead of using ``AnEnum.AnInstance.value`` in a function that
expects an int argument, you can also convert the integer to an enumeration
instance after the call by ``AnEnum(int_arg)`` and use that in comparisons.

However, there are cases where this is not possible, and explicit support in
PySide is simply not available. In those cases, you can use this flag as a
workaround until we have implemented alternatives.


ENOPT_GLOBAL_SHORTCUT (0x04)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

At the beginning of the Python enum implementation, we continued to support
the shortcut behavior of Shiboken enums: the enum constants were mirrored
into the enclosing scope.
This was later emulated in the course of forgiveness mode. For enum classes
in a PySide class this works fine, but for enum classes directly on the module
level there is no good way to implement forgiveness.

It is unlikely that errors are hidden for global enums, because they should
already produce an error during import. But for cases without access to
the source code, you can help yourself with this flag.

A flag value of 0x6 is likely to solve the majority of problems.


Flags for completeness
----------------------

The following flags complement the description of Python Enums.
They essentially serve the better understanding of the
implementation and make it fully transparent and customizable.


ENOPT_SCOPED_SHORTCUT (0x08)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For completeness, we also supported mirroring scoped enums, although this
has since been replaced by forgiveness mode. If you want to try this,
please also use the ENOPT_NO_FAKESHORTCUT flag (0x10), otherwise the
effect of this flag will remain invisible.


ENOPT_NO_FAKERENAMES (0x10)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Forgiveness mode emulates renaming ``Enum.Flag`` classes back to Shiboken
QFlags structures, which have slightly different names.
So when such a defunct name is used, the system replaces it internally
with the new ``enum.Flag`` structure. Unless special boundary problems
are provoked, this replacement should work.

To see the effect of this renaming, you can turn it off with this flag.


ENOPT_NO_ZERODEFAULT (0x40)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

As part of the forgiveness mode, Python enums can be created by a
parameterless call, although Python enums actually force a parameter
when called.

The effect can be examined if this flag is set to disable it.


ENOPT_NO_MISSING (0x80)
~~~~~~~~~~~~~~~~~~~~~~~

There are a few cases where Shiboken enums use missing values. In
``enum.Flag`` structures, this is allowed anyway because we have set the
``FlagBoundary.KEEP`` flag (see ``enum.py``).

Normal ``enum.Enum`` structures don't have this provision, but the
``enum`` module allows to pass a ``_missing_`` function for customization.

Our way of dealing with this situation is to create a new fake
``enum.Enum`` class with the same name and a nameless instance, and
pretend with an attribute setting that it has the same type.
The additional instances created in this way are recorded in a class dict
``_sbk_missing_`` in order to preserve their identity.

You will see the effect of not defining a ``_missing_`` function if you
set this flag.
