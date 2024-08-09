LICENSE_TEXT = """
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
"""

# flake8: noqa E:402

"""
pyi_generator.py

This script generates .pyi files for arbitrary modules.
"""

import argparse
import io
import logging
import os
import re
import sys
import typing

from pathlib import Path
from contextlib import contextmanager
from textwrap import dedent

from shibokensupport.signature.lib.enum_sig import HintingEnumerator
from shibokensupport.signature.lib.tool import build_brace_pattern

# Can we use forward references?
USE_PEP563 = sys.version_info[:2] >= (3, 7)

indent = " " * 4


class Writer(object):
    def __init__(self, outfile, *args):
        self.outfile = outfile
        self.history = [True, True]

    def print(self, *args, **kw):
        # controlling too much blank lines
        if self.outfile:
            if args == () or args == ("",):
                # We use that to skip too many blank lines:
                if self.history[-2:] == [True, True]:
                    return
                print("", file=self.outfile, **kw)
                self.history.append(True)
            else:
                print(*args, file=self.outfile, **kw)
                self.history.append(False)


class Formatter(Writer):
    """
    Formatter is formatting the signature listing of an enumerator.

    It is written as context managers in order to avoid many callbacks.
    The separation in formatter and enumerator is done to keep the
    unrelated tasks of enumeration and formatting apart.
    """
    def __init__(self, outfile, options, *args):
        # XXX Find out which of these patches is still necessary!
        self.options = options
        Writer.__init__(self, outfile, *args)
        # patching __repr__ to disable the __repr__ of typing.TypeVar:
        """
            def __repr__(self):
                if self.__covariant__:
                    prefix = '+'
                elif self.__contravariant__:
                    prefix = '-'
                else:
                    prefix = '~'
                return prefix + self.__name__
        """
        def _typevar__repr__(self):
            return f"typing.{self.__name__}"
        # This is no longer necessary for modern typing versions.
        # Ignore therefore if the repr is read-only and cannot be changed.
        try:
            typing.TypeVar.__repr__ = _typevar__repr__
        except TypeError:
            pass
        # Adding a pattern to substitute "Union[T, NoneType]" by "Optional[T]"
        # I tried hard to replace typing.Optional by a simple override, but
        # this became _way_ too much.
        # See also the comment in layout.py .
        brace_pat = build_brace_pattern(3, ",")
        pattern = fr"\b Union \s* \[ \s* {brace_pat} \s*, \s* NoneType \s* \]"
        replace = r"Optional[\1]"
        optional_searcher = re.compile(pattern, flags=re.VERBOSE)

        def optional_replacer(source):
            # PYSIDE-2517: findChild/findChildren type hints:
            # PlaceHolderType fix to avoid the '~' from TypeVar.__repr__
            if "~PlaceHolderType" in str(source):
                source = str(source).replace("~PlaceHolderType", "PlaceHolderType")

            return optional_searcher.sub(replace, str(source))
        self.optional_replacer = optional_replacer
        # self.level is maintained by enum_sig.py
        # self.is_method() is true for non-plain functions.

    def section(self):
        if self.level == 0:
            self.print()
        self.print()

    @contextmanager
    def module(self, mod_name):
        self.mod_name = mod_name
        txt = f"""\
            # Module `{mod_name}`

            <<IMPORTS>>
            """
        self.print(dedent(txt))
        yield

    @contextmanager
    def klass(self, class_name, class_str):
        spaces = indent * self.level
        while "." in class_name:
            class_name = class_name.split(".", 1)[-1]
            class_str = class_str.split(".", 1)[-1]
        if self.have_body:
            self.print(f"{spaces}class {class_str}:")
        else:
            self.print(f"{spaces}class {class_str}: ...")
        yield

    @contextmanager
    def function(self, func_name, signature, decorator=None):
        if func_name == "__init__":
            self.print()
        key = func_name
        spaces = indent * self.level
        if isinstance(signature, list):
            for sig in signature:
                self.print(f'{spaces}@overload')
                self._function(func_name, sig, spaces)
        else:
            self._function(func_name, signature, spaces, decorator)
        if func_name == "__init__":
            self.print()
        yield key

    def _function(self, func_name, signature, spaces, decorator=None):
        if decorator:
            # In case of a PyClassProperty the classmethod decorator is not used.
            self.print(f'{spaces}@{decorator}')
        elif self.is_method() and "self" not in signature.parameters:
            kind = "class" if "cls" in signature.parameters else "static"
            self.print(f'{spaces}@{kind}method')
        signature = self.optional_replacer(signature)
        self.print(f'{spaces}def {func_name}{signature}: ...')

    @contextmanager
    def enum(self, class_name, enum_name, value):
        spaces = indent * self.level
        hexval = hex(value)
        self.print(f"{spaces}{enum_name:25}: {class_name} = ... # {hexval}")
        yield

    @contextmanager
    def attribute(self, attr_name, attr_value):
        spaces = indent * self.level
        self.print(f"{spaces}{attr_name:25} = ...  # type: {type(attr_value).__qualname__}")
        yield

    @contextmanager
    def signal(self, class_name, sig_name, sig_str):
        spaces = indent * self.level
        self.print(f"{spaces}{sig_name:25}: ClassVar[{class_name}] = ... # {sig_str}")
        yield


def find_imports(text):
    return [imp for imp in PySide6.__all__ if f"PySide6.{imp}." in text]


FROM_IMPORTS = [
    (None, ["builtins"]),
    (None, ["os"]),
    (None, ["enum"]),
    ("collections.abc", ["Iterable"]),
    ("typing", sorted(typing.__all__)),
    ("PySide6.QtCore", ["PyClassProperty", "Signal", "SignalInstance"]),
    ("shiboken6", ["Shiboken"]),
    ]


def filter_from_imports(from_struct, text):
    """
    Build a reduced new `from` structure (nfs) with found entries, only
    """
    nfs = []
    for mod, imports in from_struct:
        lis = []
        nfs.append((mod, lis))
        for each in imports:
            # PYSIDE-1603: We search text that is a usage of the class `each`,
            #              but only if the class is not also defined here.
            if (f"class {each}(") not in text:
                if re.search(rf"(\b|@){each}\b([^\s\(:]|\n)", text):
                    lis.append(each)
                # Search if a type is present in the return statement
                # of function declarations: '... -> here:'
                if re.search(rf"->.*{each}.*:", text):
                    lis.append(each)
        if not lis:
            nfs.pop()
    return nfs


def find_module(import_name, outpath, from_pyside):
    """
    Find a module either directly by import, or use the full path,
    add the path to sys.path and import then.
    """
    if from_pyside:
        # internal mode for generate_pyi.py
        plainname = import_name.split(".")[-1]
        outfilepath = Path(outpath) / f"{plainname}.pyi"
        return import_name, plainname, outfilepath
    # we are alone in external module mode
    p = Path(import_name).resolve()
    if not p.exists():
        raise ValueError(f"File {p} does not exist.")
    if not outpath:
        outpath = p.parent
    # temporarily add the path and do the import
    sys.path.insert(0, os.fspath(p.parent))
    plainname = p.name.split(".")[0]
    __import__(plainname)
    sys.path.pop(0)
    return plainname, plainname, Path(outpath) / (plainname + ".pyi")


def generate_pyi(import_name, outpath, options):
    """
    Generates a .pyi file.
    """
    import_name, plainname, outfilepath = find_module(import_name, outpath, options._pyside_call)
    top = __import__(import_name)
    obj = getattr(top, plainname) if import_name != plainname else top
    if not getattr(obj, "__file__", None) or Path(obj.__file__).is_dir():
        raise ModuleNotFoundError(f"We do not accept a namespace as module `{plainname}`")

    outfile = io.StringIO()
    fmt = Formatter(outfile, options)
    fmt.print(LICENSE_TEXT.strip())
    if USE_PEP563:
        fmt.print("from __future__ import annotations")
        fmt.print()
    fmt.print(dedent(f'''\
        """
        This file contains the exact signatures for all functions in module
        {import_name}, except for defaults which are replaced by "...".
        """
        '''))
    HintingEnumerator(fmt).module(import_name)
    fmt.print("# eof")
    # Postprocess: resolve the imports
    if options._pyside_call:
        global PySide6
        import PySide6
    with outfilepath.open("w") as realfile:
        wr = Writer(realfile)
        outfile.seek(0)
        while True:
            line = outfile.readline()
            if not line:
                break
            line = line.rstrip()
            # we remove the "<<IMPORTS>>" marker and insert imports if needed
            if line == "<<IMPORTS>>":
                text = outfile.getvalue()
                wr.print("import " + import_name)
                for mod_name in find_imports(text):
                    imp = "PySide6." + mod_name
                    if imp != import_name:
                        wr.print("import " + imp)
                wr.print()
                for mod, imports in filter_from_imports(FROM_IMPORTS, text):
                    # Sorting, and getting uniques to avoid duplications
                    # on "Iterable" having a couple of entries.
                    import_args = ', '.join(sorted(set(imports)))
                    if mod is None:
                        # special case, a normal import
                        wr.print(f"import {import_args}")
                    else:
                        wr.print(f"from {mod} import {import_args}")
                # Adding extra typing import for types that are used in
                # the followed generated lines
                wr.print("from typing import TypeAlias, TypeVar")
                wr.print()
                wr.print()
                wr.print("NoneType: TypeAlias = type[None]")
                # We use it only in QtCore at the moment, but this
                # could be extended to other modules.
                wr.print("PlaceHolderType = TypeVar(\"PlaceHolderType\", bound=QObject)")
                wr.print()
            else:
                wr.print(line)
    if not options.quiet:
        options.logger.info(f"Generated: {outfilepath}")


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=dedent("""\
            pyi_generator.py
            ----------------

            This script generates the .pyi file for an arbitrary module.
            You pass in the full path of a compiled, importable module.
            pyi_generator will try to generate an interface "<module>.pyi".
            """))
    parser.add_argument("module",
        help="The full path name of an importable module binary (.pyd, .so)")  # noqa E:128
    parser.add_argument("--quiet", action="store_true", help="Run quietly")
    parser.add_argument("--outpath",
        help="the output directory (default = location of module binary)")  # noqa E:128
    options = parser.parse_args()
    module = options.module
    outpath = options.outpath

    qtest_env = os.environ.get("QTEST_ENVIRONMENT", "")
    logging.basicConfig(level=logging.DEBUG if qtest_env else logging.INFO)
    logger = logging.getLogger("pyi_generator")

    if outpath and not Path(outpath).exists():
        os.makedirs(outpath)
        logger.info(f"+++ Created path {outpath}")
    options._pyside_call = False
    options.is_ci = qtest_env == "ci"

    options.logger = logger
    generate_pyi(module, outpath, options=options)


if __name__ == "__main__":
    main()
# eof
