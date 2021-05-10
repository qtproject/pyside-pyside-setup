/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:LGPL$
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** GNU Lesser General Public License Usage
** Alternatively, this file may be used under the terms of the GNU Lesser
** General Public License version 3 as published by the Free Software
** Foundation and appearing in the file LICENSE.LGPL3 included in the
** packaging of this file. Please review the following information to
** ensure the GNU Lesser General Public License version 3 requirements
** will be met: https://www.gnu.org/licenses/lgpl-3.0.html.
**
** GNU General Public License Usage
** Alternatively, this file may be used under the terms of the GNU
** General Public License version 2.0 or (at your option) the GNU General
** Public license version 3 or any later version approved by the KDE Free
** Qt Foundation. The licenses are as published by the Free Software
** Foundation and appearing in the file LICENSE.GPL2 and LICENSE.GPL3
** included in the packaging of this file. Please review the following
** information to ensure the GNU General Public License requirements will
** be met: https://www.gnu.org/licenses/gpl-2.0.html and
** https://www.gnu.org/licenses/gpl-3.0.html.
**
** $QT_END_LICENSE$
**
****************************************************************************/

#include <Python.h> // Include before Qt headers due to 'slots' macro definition

#include "designercustomwidgets.h"

#include <QtCore/QCoreApplication>
#include <QtCore/QDebug>
#include <QtCore/QDir>
#include <QtCore/QFile>
#include <QtCore/QFileInfoList>
#include <QtCore/QLoggingCategory>
#include <QtCore/QOperatingSystemVersion>
#include <QtCore/QTextStream>
#include <QtCore/QVariant>

#include <string_view>

Q_LOGGING_CATEGORY(lcPySidePlugin, "qt.pysideplugin")

static const char pathVar[] = "PYSIDE_DESIGNER_PLUGINS";
static const char pythonPathVar[] = "PYTHONPATH";

// Find the static instance of 'QPyDesignerCustomWidgetCollection'
// registered as a dynamic property of QCoreApplication.
static QDesignerCustomWidgetCollectionInterface *findPyDesignerCustomWidgetCollection()
{
    static const char propertyName[] =  "__qt_PySideCustomWidgetCollection";
    if (auto coreApp = QCoreApplication::instance()) {
        const QVariant value = coreApp->property(propertyName);
        if (value.isValid() && value.canConvert<void *>())
            return reinterpret_cast<QDesignerCustomWidgetCollectionInterface *>(value.value<void *>());
    }
    return nullptr;
}

static QString pyStringToQString(PyObject *s)
{
    // PyUnicode_AsUTF8() is not available in the Limited API
    if (PyObject *bytesStr = PyUnicode_AsEncodedString(s, "utf8", nullptr))
        return QString::fromUtf8(PyBytes_AsString(bytesStr));
    return {};
}

// Return str() of a Python object
static QString pyStr(PyObject *o)
{
    PyObject *pstr = PyObject_Str(o);
    return pstr ? pyStringToQString(pstr) : QString();
}

static QString pyErrorMessage()
{
    QString result = QLatin1String("<error information not available>");
    PyObject *ptype = {};
    PyObject *pvalue = {};
    PyObject *ptraceback = {};
    PyErr_Fetch(&ptype, &pvalue, &ptraceback);
    if (pvalue)
        result = pyStr(pvalue);
    PyErr_Restore(ptype, pvalue, ptraceback);
    return result;
}


#ifdef Py_LIMITED_API
// Provide PyRun_String() for limited API (see libshiboken/pep384impl.cpp)
// Flags are ignored in these simple helpers.
PyObject *PyRun_String(const char *str, int start, PyObject *globals, PyObject *locals)
{
    PyObject *code = Py_CompileString(str, "pyscript", start);
    PyObject *ret = nullptr;

    if (code != nullptr) {
        ret = PyEval_EvalCode(code, globals, locals);
    }
    Py_XDECREF(code);
    return ret;
}
#endif // Py_LIMITED_API

static bool runPyScript(const char *script, QString *errorMessage)
{
    PyObject *main = PyImport_AddModule("__main__");
    if (main == nullptr) {
        *errorMessage = QLatin1String("Internal error: Cannot retrieve __main__");
        return false;
    }
    PyObject *globalDictionary = PyModule_GetDict(main);
    PyObject *localDictionary = PyDict_New();
    // Note: Limited API only has PyRun_String()
    PyObject *result = PyRun_String(script, Py_file_input, globalDictionary, localDictionary);
    const bool ok = result != nullptr;
    Py_DECREF(localDictionary);
    Py_XDECREF(result);
    if (!ok) {
        *errorMessage = pyErrorMessage();
        PyErr_Clear();
    }
    return ok;
}

static bool runPyScriptFile(const QString &fileName, QString *errorMessage)
{
    QFile file(fileName);
    if (!file.open(QIODevice::ReadOnly| QIODevice::Text)) {
        QTextStream(errorMessage) << "Cannot open "
            << QDir::toNativeSeparators(fileName) << " for reading: "
            << file.errorString();
        return false;
    }

    const QByteArray script = file.readAll();
    file.close();
    const bool ok = runPyScript(script.constData(), errorMessage);
    if (!ok && !errorMessage->isEmpty()) {
        errorMessage->prepend(QLatin1String("Error running ") + fileName
                              + QLatin1String(": "));
    }
    return ok;
}

static void initVirtualEnvironment()
{
    static const char virtualEnvVar[] = "VIRTUAL_ENV";
    // As of Python 3.8/Windows, Python is no longer able to run stand-alone in
    // a virtualenv due to missing libraries. Add the path to the modules
    // instead.
    bool ok;
    int majorVersion = qEnvironmentVariableIntValue("PY_MAJOR_VERSION", &ok);
    int minorVersion = qEnvironmentVariableIntValue("PY_MINOR_VERSION", &ok);
    if (!ok) {
        majorVersion = PY_MAJOR_VERSION;
        minorVersion = PY_MINOR_VERSION;
    }

    if (!qEnvironmentVariableIsSet(virtualEnvVar)
        || QOperatingSystemVersion::currentType() != QOperatingSystemVersion::Windows
        || (majorVersion == 3 && minorVersion < 8)) {
        return;
    }

    const QByteArray virtualEnvPath = qgetenv(virtualEnvVar);
    QByteArray pythonPath = qgetenv(pythonPathVar);
    if (!pythonPath.isEmpty())
        pythonPath.append(QDir::listSeparator().toLatin1());
    pythonPath.append(virtualEnvPath + R"(\Lib\site-packages)");
    qputenv(pythonPathVar, pythonPath);
}

static void initPython()
{
    // Py_SetProgramName() is considered harmful, it can break virtualenv.
    initVirtualEnvironment();

    Py_Initialize();
    qAddPostRoutine(Py_Finalize);
}

PyDesignerCustomWidgets::PyDesignerCustomWidgets(QObject *parent) : QObject(parent)
{
    qCDebug(lcPySidePlugin, "%s", __FUNCTION__);

    if (!qEnvironmentVariableIsSet(pathVar)) {
        qCWarning(lcPySidePlugin, "Environment variable %s is not set, bailing out.",
                  pathVar);
        return;
    }

    QStringList pythonFiles;
    const QString pathStr = qEnvironmentVariable(pathVar);
    const QChar listSeparator = QDir::listSeparator();
    const auto paths = pathStr.split(listSeparator);
    const QStringList oldPythonPaths =
        qEnvironmentVariable(pythonPathVar).split(listSeparator, Qt::SkipEmptyParts);
    QStringList pythonPaths = oldPythonPaths;
    // Scan for register*.py in the path
    for (const auto &p : paths) {
        QDir dir(p);
        if (dir.exists()) {
            const QFileInfoList matches =
                dir.entryInfoList({QStringLiteral("register*.py")}, QDir::Files,
                                  QDir::Name);
            for (const auto &fi : matches)
                pythonFiles.append(fi.absoluteFilePath());
            if (!matches.isEmpty()) {
                const QString dir =
                    QDir::toNativeSeparators(matches.constFirst().absolutePath());
                if (!oldPythonPaths.contains(dir))
                    pythonPaths.append(dir);
            }
        } else {
            qCWarning(lcPySidePlugin, "Directory '%s' as specified in %s does not exist.",
                      qPrintable(p), pathVar);
        }
    }
    if (pythonFiles.isEmpty()) {
        qCWarning(lcPySidePlugin, "No python files found in '%s'.", qPrintable(pathStr));
        return;
    }

    // Make modules available by adding them to the path
    if (pythonPaths != oldPythonPaths) {
        const QByteArray value = pythonPaths.join(listSeparator).toLocal8Bit();
        qCDebug(lcPySidePlugin) << "setting" << pythonPathVar << value;
        qputenv(pythonPathVar, value);
    }

    initPython();

    // Run all register*py files
    QString errorMessage;
    for (const auto &pythonFile : qAsConst(pythonFiles)) {
        qCDebug(lcPySidePlugin) << "running" << pythonFile;
        if (!runPyScriptFile(pythonFile, &errorMessage))
            qCWarning(lcPySidePlugin, "%s", qPrintable(errorMessage));
    }
}

PyDesignerCustomWidgets::~PyDesignerCustomWidgets()
{
    qCDebug(lcPySidePlugin, "%s", __FUNCTION__);
}

QList<QDesignerCustomWidgetInterface *> PyDesignerCustomWidgets::customWidgets() const
{
    if (auto collection = findPyDesignerCustomWidgetCollection())
        return collection->customWidgets();
    qCWarning(lcPySidePlugin, "No instance of QPyDesignerCustomWidgetCollection was found.");
    return {};
}
