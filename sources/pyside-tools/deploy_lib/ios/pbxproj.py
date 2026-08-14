# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
# Qt-Security score:significant reason:execute-external-code

import os
import re
from pathlib import Path

from .ios_config import IOSConfig
from .ios_dependency import QmlPlugin, QtDependencies, enabled_plugins


# Helpers

class _IdGen:
    def __init__(self):
        self._n = 0

    def next(self) -> str:
        self._n += 1
        return f"{self._n:024X}"


_BARE_IDENTIFIER = re.compile(r"[A-Za-z0-9_$./]+")


def _esc(s) -> str:
    """Quote and escape a string for safe use as a .pbxproj value.

    Bare (unquoted) tokens are only safe when they contain none of the
    format's special characters (quote, backslash, whitespace, `;`, braces,
    parens, comma). Anything else must be quoted, with `\\` and `"` escaped
    so the value can't break out of its quotes and inject additional
    key/value pairs -- values here may come from untrusted project config.
    """
    s = str(s)
    if s and _BARE_IDENTIFIER.fullmatch(s):
        return s
    escaped = (
        s.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\t", "\\t")
    )
    return f'"{escaped}"'


# Shell-script build phases

def _stdlib_script(cfg: IOSConfig) -> str:
    """Copy the Python stdlib via Python-Apple-support's own utils.sh
    (ships inside the xcframework at build/utils.sh)."""
    xcframework_rel = os.path.relpath(cfg.xcframework_path, cfg.output_dir)
    return (
        f'set -e\n'
        f'source "$PROJECT_DIR/{xcframework_rel}/build/utils.sh"\n'
        f'install_python "{xcframework_rel}"\n'
    )


def _pyside6_packages_script(cfg: IOSConfig) -> str:
    """Copy PySide6 and shiboken6 into <bundle>/packages/ -- needed on
    sys.path even though the C extensions are built-in via
    PyImport_AppendInittab. (shibokensupport is embedded inside
    libshiboken6.a itself at build time -- same as desktop -- so it isn't
    copied here as loose files.)"""
    lines = [
        'set -e',
        'PKG="$CODESIGNING_FOLDER_PATH/packages"',
        'mkdir -p "$PKG"',
        # PySide6 — exclude static libs, headers, pycache
        'rsync -a --delete \\',
        '    --exclude="*.a" --exclude="*.h" --exclude="include/" \\',
        '    --exclude="__pycache__/" --exclude="*.pyc" \\',
        f'    "{cfg.pyside6_dir}/" "$PKG/PySide6/"',
        # shiboken6 — same exclusions
        'rsync -a --delete \\',
        '    --exclude="*.a" --exclude="*.h" --exclude="__pycache__/" --exclude="*.pyc" \\',
        f'    "{cfg.shiboken_dir}/" "$PKG/shiboken6/"',
    ]
    return "\n".join(lines) + "\n"


def _packages_script(cfg: IOSConfig) -> str:
    """Copy the entry script and qml dirs declared in the config directly into
    the bundle root -- main_mm.py's runPythonApp() opens the entry script at
    <bundle>/<name>, and its sys.path setup expects sibling modules/qml dirs
    there too (see initPython()'s module_search_paths)."""
    lines = ["set -e"]
    for script in cfg.scripts:
        src = cfg.project_root / script
        lines.append(f'cp -f "{src}" "$CODESIGNING_FOLDER_PATH/"')
    # Copy app-local QML dirs next to the entry script, matching where
    # engine.addImportPath(Path(__file__).parent) expects them.
    for qml_dir in cfg.qml_dirs:
        src = cfg.project_root / qml_dir
        dest_name = Path(qml_dir).name
        lines.append(
            f'rsync -a --delete \\\n'
            f'    "{src}/" "$CODESIGNING_FOLDER_PATH/{dest_name}/"'
        )
    return "\n".join(lines) + "\n"


# Build-setting helpers

def _fw_search_paths(cfg: IOSConfig) -> list[str]:
    return [
        str(cfg.qt_ios / "lib"),  # Qt*.framework headers (Qt 6.x iOS)
    ]


def _header_search_paths(cfg: IOSConfig) -> list[str]:
    # Python.h needs an explicit path; Qt headers are covered by
    # FRAMEWORK_SEARCH_PATHS. $(BUILT_PRODUCTS_DIR)/Python.framework is
    # whichever slice Xcode resolves for the current build.
    paths = [
        "$(BUILT_PRODUCTS_DIR)/Python.framework/Headers",
        str(cfg.pyside6_dir / "include"),
    ]
    for hp in cfg.header_search_paths:
        paths.append(str(cfg.project_root / hp))
    return paths


# Main generator

def generate(cfg: IOSConfig, qml_plugins: list[QmlPlugin], qt_deps: QtDependencies) -> str:
    ids = _IdGen()

    # Each entry: (build_id, ref_id, name, settings_str | None)
    build_files: list[tuple[str, str, str, str | None]] = []
    # Each entry: (ref_id, name, path, file_type, source_tree)
    file_refs: list[tuple[str, str, str, str, str]] = []
    source_ids: list[str] = []   # Sources build phase
    framework_ids: list[str] = []   # Frameworks build phase
    framework_refs: list[tuple[str, str]] = []  # (ref_id, name) for the Frameworks PBXGroup
    embed_ids: list[str] = []   # Embed Frameworks phase
    # Dirs containing a linked .a archive -- Xcode still needs these in
    # LIBRARY_SEARCH_PATHS even for direct file references, or it reports
    # "Library not found". Derived from _add_framework() calls, not hand-kept.
    lib_search_dirs: set[str] = set()

    def _add_source(name: str, path: str, ftype: str):
        ref = ids.next()
        bid = ids.next()
        file_refs.append((ref, name, path, ftype, '"<group>"'))
        build_files.append((bid, ref, name, None))
        source_ids.append(bid)
        return ref

    def _add_framework(name: str, path: str, ftype: str,
                       src_tree: str = '"<group>"', embed: bool = False):
        ref = ids.next()
        bid = ids.next()
        file_refs.append((ref, name, path, ftype, src_tree))
        build_files.append((bid, ref, name, None))
        framework_ids.append(bid)
        framework_refs.append((ref, name))
        if ftype == "archive.ar":
            lib_search_dirs.add(str(Path(path).parent))
        if embed:
            ebid = ids.next()
            build_files.append(
                (ebid, ref, name,
                 "ATTRIBUTES = (CodeSignOnCopy, RemoveHeadersOnCopy, )")
            )
            embed_ids.append(ebid)
        return ref

    # -- main.mm (always in the output directory)
    main_mm_ref = _add_source("main.mm", "main.mm", "sourcecode.cpp.objcpp")

    # -- Python.xcframework: referenced as-is, not a fixed slice -- Xcode
    #    resolves device/simulator at build time.
    _add_framework(
        "Python.xcframework", str(cfg.xcframework_path),
        "wrapper.xcframework", embed=True,
    )

    # -- qt_deps is passed in (computed once by the caller and shared with
    #    main_mm.py); only the plain plugin path list is still needed here.
    plugins = enabled_plugins(cfg)

    # -- iOS system frameworks
    for fw_name in qt_deps.system_frameworks:
        _add_framework(
            f"{fw_name}.framework",
            f"System/Library/Frameworks/{fw_name}.framework",
            "wrapper.framework",
            src_tree="SDKROOT",
        )

    # -- Qt module archives (static; linked directly, keeps relocations
    #    in the same image as PySide6's own static archives)
    for fw_name in qt_deps.frameworks:
        p = cfg.qt_ios / "lib" / f"{fw_name}.framework" / fw_name
        if p.is_file():
            _add_framework(fw_name, str(p), "archive.ar")

    # -- Qt plugins
    for plugin_rel in plugins:
        p = cfg.qt_ios / plugin_rel
        if p.is_file():
            _add_framework(Path(plugin_rel).name, str(p), "archive.ar")

    # -- Qt QML plugins
    for qml_plugin in qml_plugins:
        if qml_plugin.archive_path.is_file():
            _add_framework(qml_plugin.archive_path.name, str(qml_plugin.archive_path), "archive.ar")

    # -- Qt bundled third-party libs (must follow Qt framework archives so the
    #    static linker can satisfy their undefined references in one pass)
    for lib_path in qt_deps.bundled_libs:
        if Path(lib_path).is_file():
            _add_framework(Path(lib_path).name, lib_path, "archive.ar")

    # -- Qt resource initializer object files (register :/... data at startup)
    for obj_path in qt_deps.resource_objects:
        _add_framework(Path(obj_path).name, obj_path, "compiled.mach-o.objfile")

    # -- QtEntryPoint provides qt_main_wrapper, which LD_ENTRY_POINT below
    #    points the binary's entry point at. It's not a dependency of any
    #    Qt module's .prl, so resolve_qt_dependencies() never finds it and
    #    it must be added explicitly.
    entry_point_lib = cfg.qt_ios / "lib" / "libQt6EntryPoint.a"
    if entry_point_lib.is_file():
        _add_framework(entry_point_lib.name, str(entry_point_lib), "archive.ar")

    # -- PySide6 module static archives. Uses qt_deps.frameworks (the full
    # transitive closure), not just cfg.qt_modules (direct imports only) --
    # same reasoning as main_mm.py's inittab loop: a directly-imported module
    # can pull in another PySide6-bound module transitively via its own .prl
    # (eg QtQml -> QtNetwork), and that module's archive must actually be
    # linked here for main_mm.py's corresponding PyInit_ symbol to resolve.
    # Filtered to real lib<mod>.a files for the same reason main_mm.py is --
    # qt_deps.frameworks also includes pure-C++ Qt internals with no
    # PySide6-bound archive at all (QtQmlModels, QtQmlWorkerScript, etc).
    static_dir = cfg.pyside6_dir
    for mod in qt_deps.frameworks:
        name = f"lib{mod}.a"
        if (static_dir / name).is_file():
            _add_framework(name, str(static_dir / name), "archive.ar")

    # -- Core PySide6 / shiboken static archives (always required)
    # Both libshiboken6.a/Shiboken.a and libpyside6.a sit directly at their
    # respective unpacked wheel roots.
    for name, dir_ in [
        ("libshiboken6.a", cfg.shiboken_dir),
        ("Shiboken.a", cfg.shiboken_dir),
        ("libpyside6.a", cfg.pyside6_dir),
    ]:
        _add_framework(name, str(dir_ / name), "archive.ar")

    # libpyside6qml.a only needed when QML modules are present
    if any(m in cfg.qt_modules for m in ("QtQml", "QtQuick")):
        _add_framework(
            "libpyside6qml.a", str(cfg.pyside6_dir / "libpyside6qml.a"), "archive.ar"
        )

    # -- Info.plist file reference (not in a build phase)
    info_ref = ids.next()
    file_refs.append((info_ref, "Info.plist", "Info.plist", "text.plist.xml", '"<group>"'))

    # -- Entitlements file reference (referenced via CODE_SIGN_ENTITLEMENTS;
    #    copied into place by ios_deploy.py's main()).
    entitlements_ref = None
    if cfg.entitlements:
        entitlements_name = Path(cfg.entitlements).name
        entitlements_ref = ids.next()
        file_refs.append((
            entitlements_ref, entitlements_name, entitlements_name,
            "text.plist.xml", '"<group>"'
        ))

    # -- App product reference
    product_name = cfg.name.replace(" ", "")
    product_ref = ids.next()
    file_refs.append((
        product_ref, f"{product_name}.app", f"{product_name}.app",
        "wrapper.application", "BUILT_PRODUCTS_DIR"
    ))

    # -- Groups
    main_group = ids.next()
    frameworks_group = ids.next()
    products_group = ids.next()

    # -- Build phases
    sources_phase = ids.next()
    frameworks_phase = ids.next()
    embed_phase = ids.next()
    resources_phase = ids.next()   # empty but needed for assets

    # -- Shell-script phases
    stdlib_phase_id = ids.next()
    pyside6_phase_id = ids.next()
    packages_phase_id = ids.next()
    shell_phases = [
        (stdlib_phase_id, "Process Python libraries", _stdlib_script(cfg)),
        (pyside6_phase_id, "Copy PySide6 Packages", _pyside6_packages_script(cfg)),
        (packages_phase_id, "Copy Python Packages", _packages_script(cfg)),
    ]

    # -- Configurations
    proj_debug_id = ids.next()
    proj_release_id = ids.next()
    proj_config_list = ids.next()
    tgt_debug_id = ids.next()
    tgt_release_id = ids.next()
    tgt_config_list = ids.next()

    # Build the .pbxproj text
    # -----------------------------------------------------------------------
    L: list[str] = []

    def w(line: str = ""):
        L.append(line)

    w("// !$*UTF8*$!")
    w("{")
    w("\tarchiveVersion = 1;")
    w("\tclasses = {")
    w("\t};")
    # 60 == Xcode 15.0, per the Xcodeproj gem's objectVersion table. This
    # gates the pbxproj format, not the SDK, so it doesn't need to track
    # Qt's iOS SDK floor (currently 18, i.e. Xcode 16+). Staying at 60
    # keeps the project openable by older tooling with no downside for iOS 18.
    w("\tobjectVersion = 60;")
    w("\tobjects = {")
    w()

    # PBXBuildFile
    w("/* Begin PBXBuildFile section */")
    for bf_id, ref_id, name, settings in build_files:
        if settings:
            w(
                f"\t\t{bf_id} /* {name} */ = {{isa = PBXBuildFile; fileRef = {ref_id}; "
                f"settings = {{{settings}; }}; }};"
            )
        else:
            w(f"\t\t{bf_id} /* {name} */ = {{isa = PBXBuildFile; fileRef = {ref_id}; }};")
    w("/* End PBXBuildFile section */")
    w()

    # PBXCopyFilesBuildPhase — Embed Frameworks
    w("/* Begin PBXCopyFilesBuildPhase section */")
    w(f"\t\t{embed_phase} /* Embed Frameworks */ = {{")
    w("\t\t\tisa = PBXCopyFilesBuildPhase;")
    w("\t\t\tbuildActionMask = 2147483647;")
    w('\t\t\tdstPath = "";')
    w("\t\t\tdstSubfolderSpec = 10;")
    w("\t\t\tfiles = (")
    for eid in embed_ids:
        w(f"\t\t\t\t{eid},")
    w("\t\t\t);")
    w('\t\t\tname = "Embed Frameworks";')
    w("\t\t\trunOnlyForDeploymentPostprocessing = 0;")
    w("\t\t};")
    w("/* End PBXCopyFilesBuildPhase section */")
    w()

    # PBXFileReference
    w("/* Begin PBXFileReference section */")
    for ref_id, name, path, ft, src_tree in file_refs:
        if src_tree == "BUILT_PRODUCTS_DIR":
            w(
                f'\t\t{ref_id} /* {name} */ = {{isa = PBXFileReference; explicitFileType = {ft}; '
                f'includeInIndex = 0; path = {_esc(name)}; sourceTree = BUILT_PRODUCTS_DIR; }};'
            )
        elif src_tree == "SDKROOT":
            w(
                f'\t\t{ref_id} /* {name} */ = {{isa = PBXFileReference; lastKnownFileType = {ft}; '
                f'name = {_esc(name)}; path = {_esc(path)}; sourceTree = SDKROOT; }};'
            )
        else:
            w(
                f'\t\t{ref_id} /* {name} */ = {{isa = PBXFileReference; lastKnownFileType = {ft}; '
                f'name = {_esc(name)}; path = {_esc(path)}; sourceTree = {src_tree}; }};'
            )
    w("/* End PBXFileReference section */")
    w()

    # PBXFrameworksBuildPhase
    w("/* Begin PBXFrameworksBuildPhase section */")
    w(f"\t\t{frameworks_phase} /* Frameworks */ = {{")
    w("\t\t\tisa = PBXFrameworksBuildPhase;")
    w("\t\t\tbuildActionMask = 2147483647;")
    w("\t\t\tfiles = (")
    for fid in framework_ids:
        w(f"\t\t\t\t{fid},")
    w("\t\t\t);")
    w("\t\t\trunOnlyForDeploymentPostprocessing = 0;")
    w("\t\t};")
    w("/* End PBXFrameworksBuildPhase section */")
    w()

    # PBXGroup
    w("/* Begin PBXGroup section */")
    # Main group
    w(f"\t\t{main_group} = {{")
    w("\t\t\tisa = PBXGroup;")
    w("\t\t\tchildren = (")
    w(f"\t\t\t\t{main_mm_ref} /* main.mm */,")
    w(f"\t\t\t\t{info_ref} /* Info.plist */,")
    if entitlements_ref is not None:
        w(f"\t\t\t\t{entitlements_ref} /* {Path(cfg.entitlements).name} */,")
    w(f"\t\t\t\t{frameworks_group} /* Frameworks */,")
    w(f"\t\t\t\t{products_group} /* Products */,")
    w("\t\t\t);")
    w('\t\t\tsourceTree = "<group>";')
    w("\t\t};")
    # Frameworks group
    w(f"\t\t{frameworks_group} /* Frameworks */ = {{")
    w("\t\t\tisa = PBXGroup;")
    w("\t\t\tchildren = (")
    for ref_id, name in framework_refs:
        w(f"\t\t\t\t{ref_id} /* {name} */,")
    w("\t\t\t);")
    w("\t\t\tname = Frameworks;")
    w('\t\t\tsourceTree = "<group>";')
    w("\t\t};")
    # Products group
    w(f"\t\t{products_group} /* Products */ = {{")
    w("\t\t\tisa = PBXGroup;")
    w("\t\t\tchildren = (")
    w(f"\t\t\t\t{product_ref} /* {product_name}.app */,")
    w("\t\t\t);")
    w("\t\t\tname = Products;")
    w('\t\t\tsourceTree = "<group>";')
    w("\t\t};")
    w("/* End PBXGroup section */")
    w()

    # PBXNativeTarget
    all_phases = [sources_phase, frameworks_phase, embed_phase, resources_phase]
    all_phases += [sp_id for sp_id, _, _ in shell_phases]
    w("/* Begin PBXNativeTarget section */")
    target_id = ids.next()
    w(f"\t\t{target_id} /* {product_name} */ = {{")
    w("\t\t\tisa = PBXNativeTarget;")
    w(f"\t\t\tbuildConfigurationList = {tgt_config_list};")
    w("\t\t\tbuildPhases = (")
    for pid in all_phases:
        w(f"\t\t\t\t{pid},")
    w("\t\t\t);")
    w("\t\t\tbuildRules = (")
    w("\t\t\t);")
    w("\t\t\tdependencies = (")
    w("\t\t\t);")
    w(f"\t\t\tname = {_esc(product_name)};")
    w(f"\t\t\tproductName = {_esc(product_name)};")
    w(f"\t\t\tproductReference = {product_ref};")
    w('\t\t\tproductType = "com.apple.product-type.application";')
    w("\t\t};")
    w("/* End PBXNativeTarget section */")
    w()

    # PBXProject
    project_id2 = ids.next()
    w("/* Begin PBXProject section */")
    w(f"\t\t{project_id2} /* Project object */ = {{")
    w("\t\t\tisa = PBXProject;")
    w("\t\t\tattributes = {")
    w("\t\t\t\tBuildIndependentTargetsInParallel = 1;")
    w("\t\t\t\tLastUpgradeCheck = 1500;")
    w("\t\t\t\tTargetAttributes = {")
    w(f"\t\t\t\t\t{target_id} = {{")
    w("\t\t\t\t\t\tCreatedOnToolsVersion = 15.0;")
    w("\t\t\t\t\t};")
    w("\t\t\t\t};")
    w("\t\t\t};")
    w(f"\t\t\tbuildConfigurationList = {proj_config_list};")
    w('\t\t\tcompatibilityVersion = "Xcode 14.0";')
    w("\t\t\tdevelopmentRegion = en;")
    w("\t\t\thasScannedForEncodings = 0;")
    w("\t\t\tknownRegions = (")
    w("\t\t\t\ten,")
    w("\t\t\t\tBase,")
    w("\t\t\t);")
    w(f"\t\t\tmainGroup = {main_group};")
    w(f"\t\t\tproductRefGroup = {products_group};")
    w('\t\t\tprojectDirPath = "";')
    w('\t\t\tprojectRoot = "";')
    w("\t\t\ttargets = (")
    w(f"\t\t\t\t{target_id},")
    w("\t\t\t);")
    w("\t\t};")
    w("/* End PBXProject section */")
    w()

    # PBXResourcesBuildPhase (empty — assets are handled via shell scripts)
    w("/* Begin PBXResourcesBuildPhase section */")
    w(f"\t\t{resources_phase} /* Resources */ = {{")
    w("\t\t\tisa = PBXResourcesBuildPhase;")
    w("\t\t\tbuildActionMask = 2147483647;")
    w("\t\t\tfiles = (")
    w("\t\t\t);")
    w("\t\t\trunOnlyForDeploymentPostprocessing = 0;")
    w("\t\t};")
    w("/* End PBXResourcesBuildPhase section */")
    w()

    # PBXShellScriptBuildPhase
    w("/* Begin PBXShellScriptBuildPhase section */")
    for sp_id, sp_name, sp_script in shell_phases:
        escaped = sp_script.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
        w(f'\t\t{sp_id} /* {sp_name} */ = {{')
        w("\t\t\tisa = PBXShellScriptBuildPhase;")
        w("\t\t\tbuildActionMask = 2147483647;")
        w("\t\t\tfiles = (")
        w("\t\t\t);")
        w("\t\t\tinputPaths = (")
        w("\t\t\t);")
        w(f'\t\t\tname = "{sp_name}";')
        w("\t\t\toutputPaths = (")
        w("\t\t\t);")
        w("\t\t\trunOnlyForDeploymentPostprocessing = 0;")
        w("\t\t\tshellPath = /bin/bash;")
        w(f'\t\t\tshellScript = "{escaped}";')
        w("\t\t};")
    w("/* End PBXShellScriptBuildPhase section */")
    w()

    # PBXSourcesBuildPhase
    w("/* Begin PBXSourcesBuildPhase section */")
    w(f"\t\t{sources_phase} /* Sources */ = {{")
    w("\t\t\tisa = PBXSourcesBuildPhase;")
    w("\t\t\tbuildActionMask = 2147483647;")
    w("\t\t\tfiles = (")
    for sid in source_ids:
        w(f"\t\t\t\t{sid},")
    w("\t\t\t);")
    w("\t\t\trunOnlyForDeploymentPostprocessing = 0;")
    w("\t\t};")
    w("/* End PBXSourcesBuildPhase section */")
    w()

    # XCBuildConfiguration
    fw_search = _fw_search_paths(cfg)
    hdr_search = _header_search_paths(cfg)
    lib_search = sorted(lib_search_dirs)

    w("/* Begin XCBuildConfiguration section */")
    # Project-level (shared settings)
    for conf_id, conf_name in [(proj_debug_id, "Debug"), (proj_release_id, "Release")]:
        w(f"\t\t{conf_id} /* {conf_name} */ = {{")
        w("\t\t\tisa = XCBuildConfiguration;")
        w("\t\t\tbuildSettings = {")
        w("\t\t\t\tALWAYS_SEARCH_USER_PATHS = NO;")
        w('\t\t\t\tCLANG_CXX_LANGUAGE_STANDARD = "c++17";')
        w("\t\t\t\tCLANG_ENABLE_ARC = YES;")
        w("\t\t\t\tCLANG_ENABLE_MODULES = YES;")
        w("\t\t\t\tENABLE_USER_SCRIPT_SANDBOXING = NO;")
        # -lresolv provides _res_9_* DNS symbols for QtNetwork -- not a
        # framework, so .prl parsing alone won't surface it.
        ld_flags = list(qt_deps.linker_flags)
        if "QtNetwork" in qt_deps.frameworks and "-lresolv" not in ld_flags:
            ld_flags.append("-lresolv")
        w(f'\t\t\t\tOTHER_LDFLAGS = "$(inherited) {" ".join(ld_flags)}";')
        # Set qt_main_wrapper as the binary entry point so Qt's iOS lifecycle
        # (UIApplicationMain + QIOSApplicationDelegate) runs before Python.
        w('\t\t\t\tLD_ENTRY_POINT = "_qt_main_wrapper";')
        # Disable the debug dylib split — keeps a single self-contained binary.
        w('\t\t\t\tENABLE_DEBUG_DYLIB = NO;')
        w(f"\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = {_esc(cfg.deployment_target)};")
        w("\t\t\t\tSDKROOT = iphoneos;")
        w('\t\t\t\tTARGETED_DEVICE_FAMILY = "1,2";')
        w("\t\t\t};")
        w(f"\t\t\tname = {conf_name};")
        w("\t\t};")

    # Target-level
    for conf_id, conf_name in [(tgt_debug_id, "Debug"), (tgt_release_id, "Release")]:
        w(f"\t\t{conf_id} /* {conf_name} */ = {{")
        w("\t\t\tisa = XCBuildConfiguration;")
        w("\t\t\tbuildSettings = {")
        w("\t\t\t\tASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;")
        w(f"\t\t\t\tCODE_SIGN_STYLE = {_esc(cfg.signing_style)};")
        if cfg.team_id:
            w(f"\t\t\t\tDEVELOPMENT_TEAM = {_esc(cfg.team_id)};")
        if cfg.entitlements:
            w(f'\t\t\t\tCODE_SIGN_ENTITLEMENTS = {_esc(Path(cfg.entitlements).name)};')
        w("\t\t\t\tFRAMEWORK_SEARCH_PATHS = (")
        w('\t\t\t\t\t"$(inherited)",')
        for p in fw_search:
            w(f"\t\t\t\t\t{_esc(p)},")
        w("\t\t\t\t);")
        w("\t\t\t\tHEADER_SEARCH_PATHS = (")
        w('\t\t\t\t\t"$(inherited)",')
        for p in hdr_search:
            w(f"\t\t\t\t\t{_esc(p)},")
        w("\t\t\t\t);")
        w("\t\t\t\tLIBRARY_SEARCH_PATHS = (")
        w('\t\t\t\t\t"$(inherited)",')
        for p in lib_search:
            w(f"\t\t\t\t\t{_esc(p)},")
        w("\t\t\t\t);")
        w("\t\t\t\tINFOPLIST_FILE = Info.plist;")
        w("\t\t\t\tLD_RUNPATH_SEARCH_PATHS = (")
        w('\t\t\t\t\t"$(inherited)",')
        w('\t\t\t\t\t"@executable_path/Frameworks",')
        w("\t\t\t\t);")
        if conf_name == "Debug":
            w('\t\t\t\tSWIFT_OPTIMIZATION_LEVEL = "-Onone";')
        w(f"\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = {_esc(cfg.bundle_id)};")
        w('\t\t\t\tPRODUCT_NAME = "$(TARGET_NAME)";')
        w("\t\t\t\tSWIFT_VERSION = 5.0;")
        w("\t\t\t};")
        w(f"\t\t\tname = {conf_name};")
        w("\t\t};")
    w("/* End XCBuildConfiguration section */")
    w()

    # XCConfigurationList
    w("/* Begin XCConfigurationList section */")
    w(f"\t\t{proj_config_list} = {{")
    w("\t\t\tisa = XCConfigurationList;")
    w("\t\t\tbuildConfigurations = (")
    w(f"\t\t\t\t{proj_debug_id},")
    w(f"\t\t\t\t{proj_release_id},")
    w("\t\t\t);")
    w("\t\t\tdefaultConfigurationIsVisible = 0;")
    w("\t\t\tdefaultConfigurationName = Release;")
    w("\t\t};")
    w(f"\t\t{tgt_config_list} = {{")
    w("\t\t\tisa = XCConfigurationList;")
    w("\t\t\tbuildConfigurations = (")
    w(f"\t\t\t\t{tgt_debug_id},")
    w(f"\t\t\t\t{tgt_release_id},")
    w("\t\t\t);")
    w("\t\t\tdefaultConfigurationIsVisible = 0;")
    w("\t\t\tdefaultConfigurationName = Release;")
    w("\t\t};")
    w("/* End XCConfigurationList section */")
    w()

    w("\t};")
    w(f"\trootObject = {project_id2};")
    w("}")
    w()

    return "\n".join(L)
