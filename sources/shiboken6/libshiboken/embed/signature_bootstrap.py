#############################################################################
##
## Copyright (C) 2019 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of PySide6.
##
## $QT_BEGIN_LICENSE:LGPL$
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## GNU Lesser General Public License Usage
## Alternatively, this file may be used under the terms of the GNU Lesser
## General Public License version 3 as published by the Free Software
## Foundation and appearing in the file LICENSE.LGPL3 included in the
## packaging of this file. Please review the following information to
## ensure the GNU Lesser General Public License version 3 requirements
## will be met: https://www.gnu.org/licenses/lgpl-3.0.html.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 2.0 or (at your option) the GNU General
## Public license version 3 or any later version approved by the KDE Free
## Qt Foundation. The licenses are as published by the Free Software
## Foundation and appearing in the file LICENSE.GPL2 and LICENSE.GPL3
## included in the packaging of this file. Please review the following
## information to ensure the GNU General Public License requirements will
## be met: https://www.gnu.org/licenses/gpl-2.0.html and
## https://www.gnu.org/licenses/gpl-3.0.html.
##
## $QT_END_LICENSE$
##
#############################################################################

"""
signature_bootstrap.py
----------------------

This file was originally directly embedded into the C source.
After it grew more and more, I now prefer to have it as Python file.

Meanwhile, there is also no more a stub loader necessary:
Because we meanwhile have embedding support, we could also load this file
directly from a .pyc file.

This file replaces the hard to read Python stub in 'signature.cpp', and we
could distinguish better between bootstrap related functions and loader
functions.
It is embedded into 'signature.cpp' as "embed/signature_bootstrap.inc".
"""

recursion_trap = 0

# We avoid real imports in phase 1 that could fail (simply removed all).
# Python 2 is not able to import when the extension import is still active.
# Phase 1 simply defines the functions, which will be used in Phase 2.
# PYSIDE-1621: This can be removed after the backport but we leave it so.

def bootstrap():
    import sys
    import os
    import tempfile
    import traceback
    from contextlib import contextmanager
    from pathlib import Path

    global recursion_trap
    if recursion_trap:
        # we are probably called from outside, already
        print("Recursion occurred in Bootstrap. Did you start by hand? Then it's ok.")
        print("But you should trigger start by '_init_pyside_extension()', only!")
    recursion_trap += 1

    @contextmanager
    def ensure_shibokensupport(target, support_path):
        # Make sure that we always have the shibokensupport containing package first.
        # Also remove any prior loaded module of this name, just in case.
        # PYSIDE-1621: support_path can also be a finder instance.
        target.insert(0, support_path)

        sbks = "shibokensupport"
        if sbks in sys.modules:
            del sys.modules[sbks]
        prefix = sbks + "."
        for key in list(key for key in sys.modules if key.startswith(prefix)):
            del sys.modules[key]
        try:
            import shibokensupport
            yield
        except Exception as e:
            print("Problem importing shibokensupport:")
            print(f"{e.__class__.__name__}: {e}")
            traceback.print_exc()
            print("sys.path:")
            for p in sys.path:
                print("  " + p)
            sys.stdout.flush()
            sys.exit(-1)
        target.remove(support_path)

    import shiboken6 as root
    path = Path(root.__file__)
    rp = path.parent.resolve()
    # This can be the shiboken6 directory or the binary module, so search.
    look_for = Path("files.dir") / "shibokensupport" / "signature" / "loader.py"
    while not (rp / look_for).exists():
        dir = rp.parent
        if dir == rp:  # Hit root, '/', 'C:\', '\\server\share'
            break
        rp = dir

    # Here we decide if we work embedded or not.
    embedding_var = "pyside_uses_embedding"
    use_embedding = bool(getattr(sys, embedding_var, False))
    loader_path = rp / look_for
    files_dir = loader_path.parents[2]
    assert files_dir.name == "files.dir"

    if not loader_path.exists():
        use_embedding = True
    setattr(sys, embedding_var, use_embedding)

    if use_embedding:
        target, support_path = prepare_zipfile()
    else:
        target, support_path = sys.path, os.fspath(files_dir)

    try:
        with ensure_shibokensupport(target, support_path):
            from shibokensupport.signature import loader
    except Exception as e:
        print('Exception:', e)
        traceback.print_exc(file=sys.stdout)

    return loader


# New functionality: Loading from a zip archive.
# There exists the zip importer, but as it is written, only real zip files are
# supported. Before I will start an own implementation, it is easiest to use
# a temporary zip file.
# PYSIDE-1621: make zip file access totally virtual

def prepare_zipfile():
    """
    Old approach:

    Write the zip file to a real file and return its name.
    It will be implicitly opened as such when we add the name to sys.path .

    New approach (Python 3, only):

    Use EmbeddableZipImporter and pass the zipfile structure directly.
    The sys.path way does not work, instead we need to use sys.meta_path .
    See https://docs.python.org/3/library/sys.html#sys.meta_path
    """
    import base64
    import io
    import sys
    import zipfile

    # 'zipstring_sequence' comes from signature.cpp
    zipbytes = base64.b64decode(''.join(zipstring_sequence))
    vzip = zipfile.ZipFile(io.BytesIO(zipbytes))
    return sys.meta_path, EmbeddableZipImporter(vzip)


class EmbeddableZipImporter(object):

    def __init__(self, zip_file):
        def p2m(filename):
            if filename.endswith("/__init__.py"):
                return filename[:-12].replace("/", ".")
            if filename.endswith(".py"):
                return filename[:-3].replace("/", ".")
            return None

        self.zfile = zip_file
        self._path2mod = {_.filename : p2m(_.filename) for _ in zip_file.filelist}
        self._mod2path = {_[1] : _[0] for _ in self._path2mod.items()}

    def find_module(self, fullname, path):
        return self if self._mod2path.get(fullname) else None

    def load_module(self, fullname):
        import importlib
        import sys

        filename = self._mod2path.get(fullname)
        if filename not in self._path2mod:
            raise ImportError(fullname)
        module_spec = importlib.machinery.ModuleSpec(fullname, None)
        new_module = importlib.util.module_from_spec(module_spec)
        with self.zfile.open(filename, "r") as f:   # "rb" not for zipfile
            exec(f.read(), new_module.__dict__)
        new_module.__file__ = filename
        new_module.__loader__ = self
        if filename.endswith("/__init__.py"):
            new_module.__path__ = []
            new_module.__package__ = fullname
        else:
            new_module.__package__ = fullname.rpartition('.')[0]
        sys.modules[fullname] = new_module
        return new_module

# eof
