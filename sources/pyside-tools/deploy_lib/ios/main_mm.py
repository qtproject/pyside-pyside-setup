# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
# Qt-Security score:significant reason:build-tool

from .ios_config import IOSConfig
from .ios_dependency import QmlPlugin, QtDependencies, resolve_plugin_class_names

_TEMPLATE = """\
{header_comment}
#pragma push_macro("slots")
#undef slots
#include <Python.h>
#pragma pop_macro("slots")

#import <UIKit/UIKit.h>

#include <QtCore/QtPlugin>

{plugin_imports}
{qml_plugin_imports}

// PyInit declarations for the modules used by this app.
#ifdef __cplusplus
extern "C" {{
#endif
{extern_decls}
#ifdef __cplusplus
}}
#endif

static void appendSysPath(PyConfig *config, NSString *path)
{{
    wchar_t *decoded = Py_DecodeLocale([path UTF8String], NULL);
    PyStatus status = PyWideStringList_Append(&config->module_search_paths, decoded);
    PyMem_RawFree(decoded);

    if (PyStatus_Exception(status)) {{
        NSLog(@"Failed to add %@ to sys.path: %s", path, status.err_msg);
        PyConfig_Clear(config);
        Py_ExitStatusException(status);
    }}
}}

static void initPython(int argc, char *argv[])
{{
    NSString *bundlePath = [[NSBundle mainBundle] resourcePath];
    NSString *pythonHome = [bundlePath stringByAppendingPathComponent:@"python"];
    NSString *stdlibPath = [pythonHome stringByAppendingPathComponent:@"{stdlib_relpath}"];
    NSString *dynloadPath = [stdlibPath stringByAppendingPathComponent:@"lib-dynload"];
    NSString *packagesPath = [bundlePath stringByAppendingPathComponent:@"packages"];

    // Register all PySide6 modules before Py_Initialize.
{inittab_calls}

    // UTF-8 mode must be set before Py_Initialize touches locale state.
    PyPreConfig preconfig;
    PyPreConfig_InitIsolatedConfig(&preconfig);
    preconfig.utf8_mode = 1;
    PyStatus preStatus = Py_PreInitialize(&preconfig);
    if (PyStatus_Exception(preStatus)) {{
        NSLog(@"Python pre-init failed: %s", preStatus.err_msg);
        Py_ExitStatusException(preStatus);
    }}

    PyConfig config;
    PyConfig_InitIsolatedConfig(&config);
    config.write_bytecode = 0;
    config.buffered_stdio = 0;
    config.install_signal_handlers = 1;
    config.home = Py_DecodeLocale([pythonHome UTF8String], NULL);

    // Pass argc/argv so sys.argv is set correctly for QApplication(sys.argv).
    PyStatus status = PyConfig_SetBytesArgv(&config, argc, argv);
    if (PyStatus_Exception(status)) {{
        NSLog(@"Failed to set sys.argv: %s", status.err_msg);
        PyConfig_Clear(&config);
        Py_ExitStatusException(status);
    }}

    config.module_search_paths_set = 1;
    appendSysPath(&config, stdlibPath);
    appendSysPath(&config, dynloadPath);
    appendSysPath(&config, packagesPath);
    appendSysPath(&config, bundlePath);

    status = Py_InitializeFromConfig(&config);
    PyConfig_Clear(&config);
    if (PyStatus_Exception(status)) {{
        NSLog(@"Python init failed: %s", status.err_msg);
        Py_ExitStatusException(status);
    }}
    NSLog(@"Python %s initialized", Py_GetVersion());
}}

static void runPythonApp()
{{
    NSString *bundlePath = [[NSBundle mainBundle] resourcePath];
    NSString *scriptPath = [bundlePath stringByAppendingPathComponent:@"{entry_script}"];

    FILE *fp = fopen([scriptPath UTF8String], "r");
    if (!fp) {{
        NSLog(@"Failed to open %@", scriptPath);
        return;
    }}
    int result = PyRun_SimpleFile(fp, [scriptPath UTF8String]);
    fclose(fp);
    if (result != 0) {{
        NSLog(@"Python script failed (code %d)", result);
        if (PyErr_Occurred()) PyErr_Print();
    }}
}}


int main(int argc, char *argv[])
{{
    @autoreleasepool {{
        initPython(argc, argv);
        runPythonApp();
        return 0;
    }}
}}
"""


def generate(cfg: IOSConfig, qml_plugins: list[QmlPlugin], qt_deps: QtDependencies) -> str:
    extern_lines: list[str] = []
    inittab_lines: list[str] = []

    # Register every PySide6-bound module actually linked into the binary --
    # not just cfg.qt_modules (what the app's own Python source directly
    # imports). A directly-imported module can transitively pull in another
    # one via its own .prl (eg QtQml needs QtNetwork) that gets linked but
    # never registered, causing "libshiboken: could not import module" at
    # runtime even though the app's own code never imports it. Filtered
    # against an actual lib<mod>.a existing, since qt_deps.frameworks also
    # includes pure-C++ Qt internals (QtQmlModels etc) with no PyInit_ symbol.
    for mod in qt_deps.frameworks:
        if not (cfg.pyside6_dir / f"lib{mod}.a").is_file():
            continue
        extern_lines.append(f"PyObject *PyInit_{mod}(void);")
        inittab_lines.append(
            f'    PyImport_AppendInittab("PySide6.{mod}", PyInit_{mod});'
        )

    extern_lines.append("PyObject *PyInit_Shiboken(void);")
    inittab_lines.append(
        '    PyImport_AppendInittab("shiboken6.Shiboken", PyInit_Shiboken);'
    )

    entry_script = cfg.scripts[0]

    plugin_imports = "\n".join(
        f"Q_IMPORT_PLUGIN({name})" for name in resolve_plugin_class_names(cfg)
    )

    qml_plugin_imports = "\n".join(
        f"Q_IMPORT_PLUGIN({p.class_name})"
        for p in qml_plugins
        if p.class_name is not None
    )

    header_comment = "// Generated by pyside6-ios-deploy. Do not edit."

    return _TEMPLATE.format(
        header_comment=header_comment,
        extern_decls="\n".join(extern_lines),
        inittab_calls="\n".join(inittab_lines),
        stdlib_relpath=f"lib/python{cfg.python_version}",
        entry_script=entry_script,
        plugin_imports=plugin_imports,
        qml_plugin_imports=qml_plugin_imports,
    )
