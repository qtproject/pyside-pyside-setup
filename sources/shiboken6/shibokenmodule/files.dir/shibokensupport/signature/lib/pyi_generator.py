LICENSE_TEXT = """
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations
"""

# flake8: noqa E:402

"""
pyi_generator.py

This script generates .pyi files for arbitrary modules.
"""

import argparse
import inspect
import io
import logging
import re
import sys
import typing

from pathlib import Path
from contextlib import contextmanager
from textwrap import dedent

from shibokensupport.signature.lib.enum_sig import HintingEnumerator
from shibokensupport.signature.lib.tool import build_brace_pattern

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
        self.options = options
        Writer.__init__(self, outfile, *args)

    # Re-add the `typing` prefix that inspect would throw away.
    # We do that by overwriting the relevant part of the function.

    backup = inspect.formatannotation

    @classmethod
    def formatannotation(cls, annotation, base_module=None):
        if getattr(annotation, '__module__', None) == 'typing':
            # do not remove the prefix!
            return repr(annotation)
        # do the normal action.
        return cls.backup(annotation, base_module)

    @classmethod
    def fix_typing_prefix(cls, signature):
        # modify the module, format the signature, restore the module.
        inspect.formatannotation = cls.formatannotation
        stringized = str(signature)
        inspect.formatannotation = cls.backup
        return stringized

    # Adding a pattern to substitute "Union[T, NoneType]" by "Optional[T]"
    # I tried hard to replace typing.Optional by a simple override, but
    # this became _way_ too much.
    # See also the comment in layout.py .

    # PYSIDE-2786: Since Python 3.9, we can use the "|" notation.
    #              Transform "Union" and "Optional" this way.
    brace_pat = build_brace_pattern(3, ",=")
    opt_uni_searcher = re.compile(fr"""
            \b                      # edge of a word
            (typing\.Optional |
             typing\.Union)         # word to find
            \s*                     # optional whitespace
            (?= \[ )                # Lookahead enforces a square bracket
            {brace_pat}             # braces tower, one capturing brace level
        """, flags=re.VERBOSE)
    brace_searcher = re.compile(brace_pat, flags=re.VERBOSE)
    split = brace_searcher.split

    @classmethod
    def optional_replacer(cls, source):
        # PYSIDE-2517: findChild/findChildren type hints:
        # PlaceHolderType fix to avoid the '~' from TypeVar.__repr__
        if "~PlaceHolderType" in source:
            source = source.replace("~PlaceHolderType", "PlaceHolderType")

        while match := cls.opt_uni_searcher.search(source):
            start = match.start()
            end = match.end()
            name = match.group(1)
            body = match.group(2).strip()[1:-1]
            # Note: this list is interspersed with "," and surrounded by "", see parser.py
            parts = [x.strip() for x in cls.split(body) if x.strip() not in ("", ",")]
            if name == "typing.Optional":
                parts.append("None")
            res = " | ".join(parts)
            source = source[: start] + res + source[end :]
        # Replace all "NoneType" strings by "None" which is a typing convention.
        return source.replace("NoneType", "None")

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
    def klass(self, class_name, class_str, has_misc_error=None):
        err_ignore = "  # type: ignore[misc]"
        opt_comment = err_ignore if has_misc_error else ""
        spaces = indent * self.level
        while "." in class_name:
            class_name = class_name.split(".", 1)[-1]
            class_str = class_str.split(".", 1)[-1]
        if self.have_body:
            self.print(f"{spaces}class {class_str}:{opt_comment}")
        else:
            self.print(f"{spaces}class {class_str}: ...{opt_comment}")
        yield

    @contextmanager
    def function(self, func_name, signature, decorator=None, aug_ass=None):
        if func_name == "__init__":
            self.print()
        key = func_name
        spaces = indent * self.level
        err_ignore = "  # type: ignore[misc]"
        if isinstance(signature, list):
            # PYSIDE-2846: mypy does not handle inconsistent static methods
            #              in overload chains. Check this and disable the error.
            #              Also disable errors in augmented assignments.
            opt_comment = (err_ignore if is_inconsistent_overload(self, signature)
                           or aug_ass else "")
            for sig in signature:
                self.print(f'{spaces}@typing.overload{opt_comment}')
                opt_comment = ""
                self._function(func_name, sig, spaces)
        else:
            opt_comment = err_ignore if aug_ass else ""
            self._function(func_name, signature, spaces, decorator, opt_comment)
        if func_name == "__init__":
            self.print()
        yield key

    def _function(self, func_name, signature, spaces, decorator=None, opt_comment=""):
        if decorator:
            # In case of a PyClassProperty the classmethod decorator is not used.
            self.print(f'{spaces}@{decorator}')
        elif self.is_method() and "self" not in signature.parameters:
            kind = "class" if "cls" in signature.parameters else "static"
            self.print(f'{spaces}@{kind}method')
        # the formatting with the inspect module explicitly removes the `typing` prefix.
        signature = self.fix_typing_prefix(signature)
        # from now on, the signature will be stringized.
        signature = self.optional_replacer(signature)
        self.print(f'{spaces}def {func_name}{signature}: ...{opt_comment}')

    @contextmanager
    def enum(self, class_name, enum_name, value):
        spaces = indent * self.level
        hexval = hex(value)
        self.print(f"{spaces}{enum_name:25} = ...  # {hexval if value >= 0 else value}")
        yield

    @contextmanager
    def attribute(self, attr_name, attr_value):
        spaces = indent * self.level
        # PYSIDE-2903: Use a fully qualified name in the type comment.
        full_name = f"{type(attr_value).__module__}.{type(attr_value).__qualname__}"
        self.print(f"{spaces}{attr_name:25} = ...  # type: {full_name}")
        yield

    @contextmanager
    def signal(self, class_name, sig_name, sig_str):
        spaces = indent * self.level
        self.print(f"{spaces}{sig_name:25}: typing.ClassVar[{class_name}] = ... # {sig_str}")
        yield


def is_inconsistent_overload(self, signatures):
    count = 0
    for sig in signatures:
        count += 1 if self.is_method() and "self" not in sig.parameters else 0
    return count != 0 and count != len(signatures)


def find_imports(text):
    return [imp for imp in PySide6.__all__ if f"PySide6.{imp}." in text]


FROM_IMPORTS = [
    (None, ["builtins"]),
    (None, ["os"]),
    (None, ["enum"]),
    (None, ["typing"]),
    ("collections.abc", ["Iterable"]),
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
    fmt.print(dedent(f'''\
        """
        This file contains the exact signatures for all functions in module
        {import_name}, except for defaults which are replaced by "...".

        # mypy: disable-error-code="override, overload-overlap"
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
                wr.print()
                wr.print()
                # We use it only in QtCore at the moment, but this
                # could be extended to other modules. (must import QObject then)
                if import_name == "PySide6.QtCore":
                    wr.print("PlaceHolderType = typing.TypeVar(\"PlaceHolderType\", "
                             "bound=PySide6.QtCore.QObject)")
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
