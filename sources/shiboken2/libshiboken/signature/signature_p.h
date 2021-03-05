/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:COMM$
**
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** $QT_END_LICENSE$
**
****************************************************************************/

#ifndef SIGNATURE_IMPL_H
#define SIGNATURE_IMPL_H

#include "signature.h"

extern "C" {

// signature_globals.cpp

typedef struct safe_globals_struc {
    // init part 1: get arg_dict
    PyObject *helper_module;
    PyObject *arg_dict;
    PyObject *map_dict;
    PyObject *value_dict;       // for writing signatures
    PyObject *feature_dict;     // registry for PySide.support.__feature__
    // init part 2: run module
    PyObject *pyside_type_init_func;
    PyObject *create_signature_func;
    PyObject *seterror_argument_func;
    PyObject *make_helptext_func;
    PyObject *finish_import_func;
} safe_globals_struc, *safe_globals;

extern safe_globals pyside_globals;
extern PyMethodDef signature_methods[];

void init_module_1(void);
void init_module_2(void);

// signature.cpp

PyObject *GetTypeKey(PyObject *ob);

PyObject *GetSignature_Function(PyObject *, PyObject *);
PyObject *GetSignature_TypeMod(PyObject *, PyObject *);
PyObject *GetSignature_Wrapper(PyObject *, PyObject *);

PyObject *get_signature_intern(PyObject *ob, PyObject *modifier);
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

PyObject *_get_qualname(PyObject *ob);
int add_more_getsets(PyTypeObject *type, PyGetSetDef *gsp, PyObject **doc_descr);
PyObject *name_key_to_func(PyObject *ob);
int insert_snake_case_variants(PyObject *dict);
PyObject *_get_class_of_cf(PyObject *ob_cf);
PyObject *_get_class_of_sm(PyObject *ob_sm);
PyObject *_get_class_of_descr(PyObject *ob);
PyObject *_address_to_stringlist(PyObject *numkey);
int _finish_nested_classes(PyObject *dict);

} // extern "C"

#endif // SIGNATURE_IMPL_H
