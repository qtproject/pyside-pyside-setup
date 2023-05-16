// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

////////////////////////////////////////////////////////////////////////////
//
// signature_global.cpp
//
// This file contains the global data structures and init code.
//

#include "autodecref.h"
#include "sbkstring.h"
#include "sbkstaticstrings.h"
#include "sbkstaticstrings_p.h"
#include "sbkenum.h"

#include "signature_p.h"

using namespace Shiboken;

extern "C" {

static const char *PySide_CompressedSignaturePackage[] = {
#include "embed/signature_inc.h"
    };

static const unsigned char PySide_SignatureLoader[] = {
#include "embed/signature_bootstrap_inc.h"
    };

static safe_globals_struc *init_phase_1()
{
    do {
        auto *p = reinterpret_cast<safe_globals_struc *>
                                    (malloc(sizeof(safe_globals_struc)));
        if (p == nullptr)
            break;
        /*
         * Initializing module signature_bootstrap.
         * Since we now have an embedding script, we can do this without any
         * Python strings in the C code.
         */
#if defined(Py_LIMITED_API) || defined(SHIBOKEN_NO_EMBEDDING_PYC)
        // We must work for multiple versions or we are cross-building for a different
        // Python version interpreter, so use source code.
#else
        AutoDecRef marshal_module(PyImport_Import(PyName::marshal()));      // builtin
        AutoDecRef loads(PyObject_GetAttr(marshal_module, PyName::loads()));
        if (loads.isNull())
            break;
#endif
        char *bytes_cast = reinterpret_cast<char *>(
                                       const_cast<unsigned char *>(PySide_SignatureLoader));
        AutoDecRef bytes(PyBytes_FromStringAndSize(bytes_cast, sizeof(PySide_SignatureLoader)));
        if (bytes.isNull())
            break;
#if defined(Py_LIMITED_API) || defined(SHIBOKEN_NO_EMBEDDING_PYC)
        PyObject *builtins = PyEval_GetBuiltins();
        PyObject *compile = PyDict_GetItem(builtins, PyName::compile());
        if (compile == nullptr)
            break;
        AutoDecRef code_obj(PyObject_CallFunction(compile, "Oss",
                                bytes.object(), "signature_bootstrap.py", "exec"));
#else
        AutoDecRef code_obj(PyObject_CallFunctionObjArgs(
                                loads, bytes.object(), nullptr));
#endif
        if (code_obj.isNull())
            break;
        p->helper_module = PyImport_ExecCodeModule("signature_bootstrap", code_obj);
        if (p->helper_module == nullptr)
            break;
        // Initialize the module
        PyObject *mdict = PyModule_GetDict(p->helper_module);
        if (PyDict_SetItem(mdict, PyMagicName::builtins(), PyEval_GetBuiltins()) < 0)
            break;

        /*********************************************************************
         *
         * Attention!
         * ----------
         *
         * We are unpacking an embedded ZIP file with more signature modules.
         * They will be loaded later with the zipimporter.
         * The file `signature_bootstrap.py` does the unpacking and starts the
         * loader. See `init_phase_2`.
         *
         * Due to MSVC's limitation to 64k strings, we needed to assemble pieces.
         */
        auto **block_ptr = reinterpret_cast<const char **>(PySide_CompressedSignaturePackage);
        PyObject *piece{};
        AutoDecRef zipped_string_sequence(PyList_New(0));
        for (; **block_ptr != 0; ++block_ptr) {
            // we avoid the string/unicode dilemma by not using PyString_XXX:
            piece = Py_BuildValue("s", *block_ptr);
            if (piece == nullptr || PyList_Append(zipped_string_sequence, piece) < 0)
                break;
        }
        if (PyDict_SetItemString(mdict, "zipstring_sequence", zipped_string_sequence) < 0)
            break;

        // build a dict for diverse mappings
        p->map_dict = PyDict_New();

        // build a dict for the prepared arguments
        p->arg_dict = PyDict_New();
        if (PyObject_SetAttrString(p->helper_module, "pyside_arg_dict", p->arg_dict) < 0)
            break;

        // build a dict for assigned signature values
        p->value_dict = PyDict_New();

        // PYSIDE-1019: build a __feature__ dict
        p->feature_dict = PyDict_New();
        if (PyObject_SetAttrString(p->helper_module, "pyside_feature_dict", p->feature_dict) < 0)
            break;

        // This function will be disabled until phase 2 is done.
        p->finish_import_func = nullptr;

        return p;

    } while (0);

    PyErr_Print();
    Py_FatalError("could not initialize part 1");
    return nullptr;
}

static int init_phase_2(safe_globals_struc *p, PyMethodDef *methods)
{
    do {
        PyMethodDef *ml;

        // The single function to be called, but maybe more to come.
        for (ml = methods; ml->ml_name != nullptr; ml++) {
            PyObject *v = PyCFunction_NewEx(ml, nullptr, nullptr);
            if (v == nullptr
                || PyObject_SetAttrString(p->helper_module, ml->ml_name, v) != 0)
                break;
            Py_DECREF(v);
        }
        // The first entry is __feature_import__, add documentation.
        PyObject *builtins = PyEval_GetBuiltins();
        PyObject *imp_func = PyDict_GetItemString(builtins, "__import__");
        PyObject *imp_doc = PyObject_GetAttrString(imp_func, "__doc__");
        signature_methods[0].ml_doc = String::toCString(imp_doc);

        PyObject *bootstrap_func = PyObject_GetAttrString(p->helper_module, "bootstrap");
        if (bootstrap_func == nullptr)
            break;

        /*********************************************************************
         *
         * Attention!
         * ----------
         *
         * This is the entry point where everything in folder
         * `shibokensupport` becomes initialized. It starts with
         * `signature_bootstrap.py` and continues from there to `loader.py`.
         *
         * The return value of the bootstrap function is the loader module.
         */
        PyObject *loader = PyObject_CallFunctionObjArgs(bootstrap_func, nullptr);
        if (loader == nullptr)
            break;

        // now the loader should be initialized
        p->pyside_type_init_func = PyObject_GetAttrString(loader, "pyside_type_init");
        if (p->pyside_type_init_func == nullptr)
            break;
        p->create_signature_func = PyObject_GetAttrString(loader, "create_signature");
        if (p->create_signature_func == nullptr)
            break;
        p->seterror_argument_func = PyObject_GetAttrString(loader, "seterror_argument");
        if (p->seterror_argument_func == nullptr)
            break;
        p->make_helptext_func = PyObject_GetAttrString(loader, "make_helptext");
        if (p->make_helptext_func == nullptr)
            break;
        p->finish_import_func = PyObject_GetAttrString(loader, "finish_import");
        if (p->finish_import_func == nullptr)
            break;
        p->feature_import_func = PyObject_GetAttrString(loader, "feature_import");
        if (p->feature_import_func == nullptr)
            break;
        p->feature_imported_func = PyObject_GetAttrString(loader, "feature_imported");
        if (p->feature_imported_func == nullptr)
            break;

        // We call stuff like the feature initialization late,
        // after all the function pointers are in place.
        PyObject *post_init_func = PyObject_GetAttrString(loader, "post_init");
        if (post_init_func == nullptr)
            break;
        PyObject *ret = PyObject_CallFunctionObjArgs(post_init_func, nullptr);
        if (ret == nullptr)
            break;

        return 0;

    } while (0);

    PyErr_Print();
    Py_FatalError("could not initialize part 2");
    return -1;
}

#ifndef _WIN32
////////////////////////////////////////////////////////////////////////////
// a stack trace for linux-like platforms
#include <cstdio>
#if defined(__GLIBC__)
#  include <execinfo.h>
#endif
#include <signal.h>
#include <cstdlib>
#include <unistd.h>

static void handler(int sig) {
#if defined(__GLIBC__)
    void *array[30];
    size_t size;

    // get void *'s for all entries on the stack
    size = backtrace(array, 30);

    // print out all the frames to stderr
#endif
    std::fprintf(stderr, "Error: signal %d:\n", sig);
#if defined(__GLIBC__)
    backtrace_symbols_fd(array, size, STDERR_FILENO);
#endif
    exit(1);
}

////////////////////////////////////////////////////////////////////////////
#endif // _WIN32

safe_globals pyside_globals = nullptr;

void init_shibokensupport_module(void)
{
    static int init_done = 0;

    if (!init_done) {
        pyside_globals = init_phase_1();
        if (pyside_globals != nullptr)
            init_done = 1;

#ifndef _WIN32
        // We enable the stack trace in CI, only.
        const char *testEnv = getenv("QTEST_ENVIRONMENT");
        if (testEnv && strstr(testEnv, "ci"))
            signal(SIGSEGV, handler);   // install our handler
#endif // _WIN32

        init_phase_2(pyside_globals, signature_methods);
        // Enum must be initialized when signatures exist, not earlier.
        init_enum();
    }
}

} // extern "C"
