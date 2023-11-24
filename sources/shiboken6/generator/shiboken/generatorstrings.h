// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef GENERATORSTRINGS_H
#define GENERATORSTRINGS_H

#include <QtCore/QString>

QString CPP_ARG_N(int i);
QString CPP_ARG_REMOVED(int i);

constexpr auto CPP_RETURN_VAR = QLatin1StringView("cppResult");
constexpr auto CPP_SELF_VAR = QLatin1StringView("cppSelf");
constexpr auto CPP_ARG = QLatin1StringView("cppArg");
constexpr auto NULL_PTR = QLatin1StringView("nullptr");
constexpr auto PYTHON_ARG = QLatin1StringView("pyArg");
constexpr auto PYTHON_ARGS = QLatin1StringView("pyArgs");
constexpr auto PYTHON_OVERRIDE_VAR = QLatin1StringView("pyOverride");
constexpr auto PYTHON_RETURN_VAR = QLatin1StringView("pyResult");
constexpr auto PYTHON_SELF_VAR = QLatin1StringView("self");
constexpr auto PYTHON_TO_CPP_VAR = QLatin1StringView("pythonToCpp");

constexpr auto CONV_RULE_OUT_VAR_SUFFIX = QLatin1StringView("_out");
constexpr auto BEGIN_ALLOW_THREADS
    = QLatin1StringView("PyThreadState *_save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS");
constexpr auto END_ALLOW_THREADS
    = QLatin1StringView("PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS");

constexpr auto REPR_FUNCTION = QLatin1StringView("__repr__");

constexpr auto CPP_ARG0 = QLatin1StringView("cppArg0");

extern const char *const METHOD_DEF_SENTINEL;
extern const char *const PYTHON_TO_CPPCONVERSION_STRUCT;
extern const char *const openTargetExternC;
extern const char *const closeExternC;
extern const char *const richCompareComment;

#endif // GENERATORSTRINGS_H
