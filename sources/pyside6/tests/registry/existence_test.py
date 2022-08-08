# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

"""
existence_test.py
-----------------

A test that checks all function signatures if they still exist.

Definition of the rules used:
=============================

Any entry
---------

    Exists in file      Exists in Binary     Result
            +               +                   ok
            +               -                   error
            -               +                   ok

List entry
----------

     Arity in file      Arity in Binary      Result
            n               n                   ok
            n               < n                 error
            n               > n                 ok

"""

import os
import re
import sys
from textwrap import dedent
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(True)

from init_platform import enum_all, generate_all
from util import (isolate_warnings, check_warnings, suppress_warnings, warn,
                  is_ci, qt_version, get_script_dir, get_effective_refpath,
                  get_refpath, import_refmodule)
from PySide6 import *

refPath = get_refpath()
effectiveRefPath = get_effective_refpath()
pyc = os.path.splitext(effectiveRefPath)[0] + ".pyc"
if os.path.exists(pyc) and not os.path.exists(effectiveRefPath):
    # on Python2 the pyc file would be imported
    os.unlink(pyc)

if refPath != effectiveRefPath:
    print("*** Falling back to ", effectiveRefPath, " since expected ",
        refPath, " does not exist")

script_dir = get_script_dir()
shortpath = os.path.relpath(effectiveRefPath, script_dir)
try:
    sig_exists = import_refmodule()
    print("found:", shortpath)
    have_refmodule = True
except ImportError:
    print("*** not found:", shortpath)
    have_refmodule = False
except SyntaxError:
    print("*** not a python file, removed:", shortpath)
    os.unlink(effectiveRefPath)
    have_refmodule = False
except NameError as e:
    if "recreate" in e.args[0]:
        print("*** explicit request to recreate:", shortpath)
    else:
        print("*** unexpected NameError:", e, "- creating", shortpath)
    os.unlink(effectiveRefPath)
    have_refmodule = False
dict_name = "sig_dict"
if have_refmodule and not hasattr(sig_exists, dict_name):
    print(f"*** wrong module without '{dict_name}', removed: {shortpath}")
    os.unlink(effectiveRefPath)
    have_refmodule = False


class TestUnrecognizedOffending(unittest.TestCase):
    """
    We run the signature generation on all modules and raise an error
    if a warning was issued. This is better than turning warnings into
    errors because that would stop early before we have all warnings.
    """
    def test_signatures_recognized(self):
        with isolate_warnings():
            found_sigs = enum_all()
            if check_warnings():
                raise RuntimeError("There are errors, see above.")


@unittest.skipIf(not have_refmodule,
                 "not activated for this platform or version")
class TestSignaturesExists(unittest.TestCase):
    """
    This is the current simple attempt to support a signature self test.
    You can activate it for your platform by supplying your own reference
    file. Simply run init_platform.py and add the generated file to the
    repository.
    """

    @staticmethod
    def _do_the_test(found_sigs):

        def multi_signature_msg(key, actual, expect):
            len_act = len(actual) if type(actual) is list else 1
            len_exp = len(expect) if type(expect) is list else 1
            return (f"multi-signature count mismatch for '{key}'. "
                    f"Actual {len_act} {actual} vs. expected {len_exp} {expect}")

        for key, value in sig_exists.sig_dict.items():
            name = key.rsplit(".", 1)[-1]
            if name in ("next", "__next__"):  # ignore problematic cases
                continue
            if "<" in key:
                # Skip over remaining crap in "<...>"
                continue
            if key.startswith("sample.SampleNamespace"):
                # We cannot work with sample namespaces after the change to __qualname__.
                continue
            if (key.startswith("smart.SharedPtr") or
                re.match(r"PySide6\..*?\.QSharedPointer_", key)):
                # These mangled names are not supported.
                # We should fix them.
                continue
            if key not in found_sigs:
                warn(f"missing key: '{key} value={value}'", stacklevel=3)
            else:
                found_val = found_sigs[key]
                if type(value) is list and (
                        type(found_val) is tuple or
                        len(found_val) < len(value)):
                    # We check that nothing got lost. But it is ok when an older
                    # registry file does not know all variants, yet!
                    warn(multi_signature_msg(key, found_val, value), stacklevel=3)

    def test_signatures(self):
        found_sigs = enum_all()
        with isolate_warnings():
            self._do_the_test(found_sigs)
            if is_ci and check_warnings():
                raise RuntimeError("There are errors, see above.")

    def test_error_is_raised(self):
        found_sigs = enum_all()
        # Make sure that errors are actually raised.
        search = list(found_sigs.keys())
        pos = 42  # arbitrary and historycal, could be 0 as well

        # We try all variants:
        while type(found_sigs[search[pos]]) is not tuple:
            pos += 1
        tuple_key = search[pos]
        while type(found_sigs[search[pos]]) is not list:
            pos += 1
        list_key = search[pos]

        test_sigs = found_sigs.copy()
        test_sigs.pop(tuple_key)
        with isolate_warnings(), suppress_warnings():
            self._do_the_test(test_sigs)
            self.assertTrue(check_warnings(), "you warn about too few entries")

        test_sigs = found_sigs.copy()
        test_sigs["whatnot"] = ("nothing", "real")
        with isolate_warnings(), suppress_warnings():
            self._do_the_test(test_sigs)
            self.assertFalse(check_warnings(), "you ignore too many entries")

        test_sigs = found_sigs.copy()
        repl = test_sigs[list_key]
        repl.pop(0)
        test_sigs[list_key] = repl
        with isolate_warnings(), suppress_warnings():
            self._do_the_test(test_sigs)
            # An arity that is now missing is an error.
            self.assertTrue(check_warnings(), "you warn when arity got smaller")

        test_sigs = found_sigs.copy()
        repl = test_sigs[list_key]
        repl = repl[0]
        assert type(repl) is tuple
        test_sigs[list_key] = repl
        with isolate_warnings(), suppress_warnings():
            self._do_the_test(test_sigs)
            # An arity that is now missing is an error.
            self.assertTrue(check_warnings(), "you warn when list degraded to tuple")

        test_sigs = found_sigs.copy()
        repl = test_sigs[list_key]
        repl = repl + repl
        test_sigs[list_key] = repl
        with isolate_warnings(), suppress_warnings():
            self._do_the_test(test_sigs)
            # More arities are ignored, because we might test an older version.
            self.assertFalse(check_warnings(), "you ignore when arity got bigger")


tested_versions = (5, 6), (5, 9), (5, 11), (5, 12), (5, 14)

if not have_refmodule and is_ci and qt_version()[:2] in tested_versions:
    class TestFor_CI_Init(unittest.TestCase):
        """
        This helper class generates the reference file for CI.
        It creates an output listing that can be used to check
        the result back in.
        """
        generate_all()
        sys.stderr.flush()
        print("BEGIN_FILE", shortpath, file=sys.stderr)
        with open(refPath) as f:
            print(f.read(), file=sys.stderr)
        print("END_FILE", shortpath, file=sys.stderr)
        sys.stderr.flush()
        raise RuntimeError(dedent("""
            {line}
            **  This is the initial call. You should check this file in:
            **  {}
            **""").format(shortpath, line=79 * "*"))

if __name__ == '__main__':
    unittest.main()
