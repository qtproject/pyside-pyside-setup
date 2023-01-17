# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

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

# PYSIDE-1436: Python 3.10 had a problem with EmbeddableZipImporter because the
imports were in the functions. Moved them outside into the globals.
"""

recursion_trap = 0

import base64
import importlib
import io
import os
import sys
import traceback
import zipfile

from contextlib import contextmanager
from importlib.machinery import ModuleSpec
from pathlib import Path


def bootstrap():

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
            f = sys.stderr
            print("Problem importing shibokensupport:", file=f)
            print(f"{e.__class__.__name__}: {e}", file=f)
            traceback.print_exc()
            print("sys.path:", file=f)
            for p in sys.path:
                print("  " + p, file=f)
            f.flush()
            sys.exit(-1)
        target.remove(support_path)

    # Here we decide if we re-incarnate the embedded files or use embedding.
    incarnated = find_incarnated_files()
    if incarnated:
        target, support_path = sys.path, os.fspath(incarnated)
    else:
        target, support_path = prepare_zipfile()
    with ensure_shibokensupport(target, support_path):
        from shibokensupport.signature import loader
    return loader

# Newer functionality:
# This function checks if the support directory exist and returns it.
# If does not exist, we try to create it and return it.
# Otherwise, we return None.

def find_incarnated_files():
    import shiboken6 as root
    files_dir = Path(root.__file__).resolve().parent / "files.dir"
    handle_embedding_switch(files_dir)
    if files_dir.exists():
        sys.path.insert(0, os.fspath(files_dir))
        # Note: To avoid recursion problems, we need to preload the loader.
        # But that has the side-effect that we need to delay the feature
        # initialization until all function pointers are set.
        # See `post_init_func` in signature_globals.cpp .
        import shibokensupport.signature.loader
        del sys.path[0]
        return files_dir
    return None


def handle_embedding_switch(files_dir):
    """
    This handles the optional environment variable `SBK_EMBED`
    if not set             : do nothing
    if set to 0, false, no : de-virtualize the Python files
    if set to 1, true, yes : virtualize again (delete "files.dir")
    """
    env_name = "SBK_EMBED"
    env_var = os.environ.get(env_name)
    if not env_var:
        return
    if env_var.lower() in ("1", "t", "true", "y", "yes"):
        import shutil
        shutil.rmtree(files_dir, ignore_errors=True)
    elif env_var.lower() in ("0", "f", "false", "n", "no"):
        reincarnate_files(files_dir)


def reincarnate_files(files_dir):
    target, zip = prepare_zipfile()
    names = (_ for _ in zip.zfile.namelist() if _.endswith(".py"))
    try:
        # First check mkdir to get an error when we cannot write.
        files_dir.mkdir(exist_ok=True)
    except os.error as e:
        print(f"SBK_EMBED=False: Warning: Cannot write into {files_dir}")
        return None
    try:
        # Then check for a real error when unpacking the zip file.
        zip.zfile.extractall(path=files_dir, members=names)
        return files_dir
    except Exception as e:
        print(f"{e.__class__.__name__}: {e}", file=sys.stderr)
        traceback.print_exc()
        raise

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
        self._mod2path = {p2m(_.filename) : _.filename for _ in zip_file.filelist}

    def find_spec(self, fullname, path, target=None):
        path = self._mod2path.get(fullname)
        return ModuleSpec(fullname, self) if path else None

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        fullname = module.__spec__.name
        filename = self._mod2path[fullname]
        with self.zfile.open(filename, "r") as f:   # "rb" not for zipfile
            codeob = compile(f.read(), filename, "exec")
            exec(codeob, module.__dict__)
        module.__file__ = filename
        module.__loader__ = self
        if filename.endswith("/__init__.py"):
            module.__path__ = []
            module.__package__ = fullname
        else:
            module.__package__ = fullname.rpartition('.')[0]
        sys.modules[fullname] = module

# eof
