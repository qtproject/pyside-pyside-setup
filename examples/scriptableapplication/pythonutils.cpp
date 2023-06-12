// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

#include "pythonutils.h"

#include <QtCore/QByteArray>
#include <QtCore/QCoreApplication>
#include <QtCore/QDebug>
#include <QtCore/QOperatingSystemVersion>
#include <QtCore/QStringList>
#include <QtCore/QTemporaryFile>
#include <QtCore/QDir>

#include <sbkpython.h>
#include <sbkconverter.h>
#include <sbkmodule.h>

/* from AppLib bindings */

extern "C" PyObject *PyInit_AppLib();
static const char moduleName[] = "AppLib";

// This variable stores all Python types exported by this module.
extern PyTypeObject **SbkAppLibTypes;

// This variable stores all type converters exported by this module.
extern SbkConverter **SbkAppLibTypeConverters;

namespace PythonUtils {

static State state = PythonUninitialized;

static void cleanup()
{
    if (state > PythonUninitialized) {
        Py_Finalize();
        state = PythonUninitialized;
    }
}

static const char virtualEnvVar[] = "VIRTUAL_ENV";

// If there is an active python virtual environment, use that environment's
// packages location.
static void initVirtualEnvironment()
{
    // As of Python 3.8, Python is no longer able to run stand-alone in a
    // virtualenv due to missing libraries. Add the path to the modules instead.
    if (QOperatingSystemVersion::currentType() == QOperatingSystemVersion::Windows
        && (PY_MAJOR_VERSION > 3 || (PY_MAJOR_VERSION == 3 && PY_MINOR_VERSION >= 8))) {
        const QByteArray virtualEnvPath = qgetenv(virtualEnvVar);
        qputenv("PYTHONPATH", virtualEnvPath + "\\Lib\\site-packages");
    }
}

State init()
{
    if (state > PythonUninitialized)
        return state;

    if (qEnvironmentVariableIsSet(virtualEnvVar))
        initVirtualEnvironment();

    if (PyImport_AppendInittab(moduleName, PyInit_AppLib) == -1) {
        qWarning("Failed to add the module '%s' to the table of built-in modules.", moduleName);
        return state;
    }

    Py_Initialize();
    qAddPostRoutine(cleanup);
    state = PythonInitialized;
    const bool pythonInitialized = PyInit_AppLib() != nullptr;
    const bool pyErrorOccurred = PyErr_Occurred() != nullptr;
    if (pythonInitialized && !pyErrorOccurred) {
        state = AppModuleLoaded;
    } else {
        if (pyErrorOccurred)
            PyErr_Print();
        qWarning("Failed to initialize the module.");
    }
    return state;
}

bool bindAppObject(const QString &moduleName, const QString &name,
                      int index, QObject *o)
{
    if (init() != AppModuleLoaded)
        return false;
    PyTypeObject *typeObject = SbkAppLibTypes[index];

    PyObject *po = Shiboken::Conversions::pointerToPython(typeObject, o);
    if (!po) {
        qWarning() << __FUNCTION__ << "Failed to create wrapper for" << o;
        return false;
    }
    Py_INCREF(po);

    PyObject *module = PyImport_AddModule(moduleName.toLocal8Bit().constData());
    if (!module) {
        Py_DECREF(po);
        if (PyErr_Occurred())
            PyErr_Print();
        qWarning() << __FUNCTION__ << "Failed to locate module" << moduleName;
        return false;
    }

    if (PyModule_AddObject(module, name.toLocal8Bit().constData(), po) < 0) {
        if (PyErr_Occurred())
            PyErr_Print();
        qWarning() << __FUNCTION__ << "Failed add object" << name << "to" << moduleName;
        return false;
    }

    return true;
}

bool runScript(const QString &script)
{
    if (init() == PythonUninitialized)
        return false;

    // Executing the whole script as one line
    bool result = true;
    const QByteArray line = script.toUtf8();
    if (PyRun_SimpleString(line.constData()) == -1) {
        if (PyErr_Occurred())
            PyErr_Print();
        result = false;
    }

    return result;
}

} // namespace PythonUtils
