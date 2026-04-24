// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef SIGNATURE_IMPL_H
#define SIGNATURE_IMPL_H

#include "signature.h"

extern "C" {

// signature_globals.cpp

struct safe_globals_struc {
    // init part 1: get arg_dict
    PyObject *helper_module = nullptr;
    PyObject *arg_dict = nullptr;
    PyObject *map_dict = nullptr;
    PyObject *value_dict = nullptr;       // for writing signatures
    PyObject *feature_dict = nullptr;     // registry for PySide.support.__feature__
    PyObject *empty_dict = nullptr;
    // init part 2: run module
    PyObject *pyside_type_init_func = nullptr;
    PyObject *create_signature_func = nullptr;
    PyObject *seterror_argument_func = nullptr;
    PyObject *make_helptext_func = nullptr;
    PyObject *finish_import_func = nullptr;
    PyObject *feature_import_func = nullptr;
    PyObject *feature_imported_func = nullptr;
};

safe_globals_struc *signatureGlobals();
extern PyMethodDef signature_methods[];

void init_shibokensupport_module(void);

// signature.cpp

PyObject *GetTypeKey(PyObject *ob);

PyObject *GetSignature_Function(PyObject *, PyObject *);
PyObject *GetSignature_TypeMod(PyObject *, PyObject *);
PyObject *GetSignature_Wrapper(PyObject *, PyObject *);

LIBSHIBOKEN_API PyObject *get_signature_intern(PyObject *ob, PyObject *modifier);
PyObject *PySide_BuildSignatureProps(PyObject *class_mod);
PyObject *GetClassOrModOf(PyObject *ob);

// signature_extend.cpp
PyObject *pyside_cf_get___signature__(PyObject *func, PyObject *modifier);
PyObject *pyside_sm_get___signature__(PyObject *sm, PyObject *modifier);
PyObject *pyside_md_get___signature__(PyObject *ob_md, PyObject *modifier);
PyObject *pyside_wd_get___signature__(PyObject *ob, PyObject *modifier);
PyObject *pyside_tp_get___signature__(PyObject *obtype_mod, PyObject *modifier);

int PySide_PatchTypes(void);
PyObject *pyside_tp_get___doc__(PyObject *tp);

// signature_helper.cpp

int add_more_getsets(PyTypeObject *type, PyGetSetDef *gsp, PyObject **doc_descr);
PyObject *name_key_to_func(PyObject *ob);
int insert_snake_case_variants(PyObject *dict);
PyObject *_get_class_of_cf(PyObject *ob_cf);
PyObject *_get_class_of_sm(PyObject *ob_sm);
PyObject *_get_class_of_descr(PyObject *ob);
PyObject *_address_to_stringlist(PyObject *numkey);
PyObject *_address_ptr_to_stringlist(const char **sig_strings);
int _build_func_to_type(PyObject *obtype);
int _finish_nested_classes(PyObject *dict);

#ifdef PYPY_VERSION
// PyPy has a special builtin method.
PyObject *GetSignature_Method(PyObject *, PyObject *);
PyObject *pyside_bm_get___signature__(PyObject *func, PyObject *modifier);
PyObject *_get_class_of_bm(PyObject *ob_cf);
#endif

} // extern "C"

#endif // SIGNATURE_IMPL_H
