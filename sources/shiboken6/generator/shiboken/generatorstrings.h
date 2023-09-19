// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef GENERATORSTRINGS_H
#define GENERATORSTRINGS_H

#include <QtCore/QString>

QString CPP_ARG(int i);
QString CPP_ARG_REMOVED(int i);

extern const QString CPP_RETURN_VAR;
extern const QString CPP_SELF_VAR;
extern const QString NULL_PTR;
extern const QString PYTHON_ARG;
extern const QString PYTHON_ARGS;
extern const QString PYTHON_OVERRIDE_VAR;
extern const QString PYTHON_RETURN_VAR;
extern const QString PYTHON_TO_CPP_VAR;

extern const QString CONV_RULE_OUT_VAR_SUFFIX;
extern const QString BEGIN_ALLOW_THREADS;
extern const QString END_ALLOW_THREADS;

extern const QString REPR_FUNCTION;

extern const QString CPP_ARG0;
extern const char *const METHOD_DEF_SENTINEL;
extern const char *const PYTHON_TO_CPPCONVERSION_STRUCT;
extern const char *const openTargetExternC;
extern const char *const closeExternC;
extern const char *const richCompareComment;

#endif // GENERATORSTRINGS_H
