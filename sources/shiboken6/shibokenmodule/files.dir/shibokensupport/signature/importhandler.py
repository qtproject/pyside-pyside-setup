# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

"""
importhandler.py

This module handles special actions after the import of PySide modules.
The reason for this was the wish to replace some deprecated functions
by a Python implementation that gives a warning.

It provides a framework to safely call functions outside of files.dir,
because the implementation of deprecated functions should be visible
to the users (in the hope they don't use it any longer <wink>).

As a first approach, the function finish_import redirects to
PySide6/support/deprecated.py . There can come other extensions as well.
"""

try:
    from PySide6.support import deprecated
    have_deprecated = True
except ImportError:
    have_deprecated = False


# called by loader.py from signature.cpp
def finish_import(module):
    if have_deprecated and module.__name__.startswith("PySide6."):
        try:
            name = "fix_for_" + module.__name__.split(".")[1]
            func = getattr(deprecated, name, None)
            if func:
                func(module)
        except Exception as e:
            name = e.__class__.__qualname__
            print(72 * "*")
            print(f"Error in deprecated.py, ignored:")
            print(f"    {name}: {e}")

"""
A note for people who might think this could be written in pure Python:

Sure, by an explicit import of the modules to patch, this is no problem.
But in the general case, a module should only be imported on user
request and not because we want to patch it. So I started over.

I then tried to do it on demand by redirection of the __import__ function.
Things worked quite nicely as it seemed, but at second view this solution
was much less appealing.

Reason:
If someone executes as the first PySide statement

    from PySide6 import QtGui

then this import is already running. We can see the other imports like the
diverse initializations and QtCore, because it is triggered by import of
QtGui. But the QtGui import can not be seen at all!

With a lot of effort, sys.setprofile() and stack inspection with the inspect
module, it is *perhaps* possible to solve that. I tried for a day and then
gave up, since the solution is anyway not too nice when __import__ must
be overridden.
"""
#eof
