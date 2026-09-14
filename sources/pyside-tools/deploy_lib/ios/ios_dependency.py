# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
# Qt-Security score:significant reason:default

import re
from pathlib import Path
from dataclasses import dataclass, field

from .ios_config import IOSConfig


# Platform + image/icon plugins are always linked. tls/sqldrivers/
# networkinformation are module-gated below instead.
#
# The six permissions/* plugins are unconditional too, but for a different
# reason: PySide6/glue/qtcore.cpp and qtpositioning.cpp always
# Q_IMPORT_PLUGIN them, so leaving one unlinked is a link error.
_QT_PLUGINS = [
    "plugins/platforms/libqios.a",
    "plugins/imageformats/libqgif.a",
    "plugins/imageformats/libqico.a",
    "plugins/imageformats/libqjpeg.a",
    "plugins/imageformats/libqsvg.a",
    "plugins/iconengines/libqsvgicon.a",
    "plugins/permissions/libqdarwincamerapermission.a",
    "plugins/permissions/libqdarwinmicrophonepermission.a",
    "plugins/permissions/libqdarwinbluetoothpermission.a",
    "plugins/permissions/libqdarwincontactspermission.a",
    "plugins/permissions/libqdarwincalendarpermission.a",
    "plugins/permissions/libqdarwinlocationpermission.a",
]


_QT_PLUGIN_MODULE_GATE: dict[str, tuple[str, ...]] = {
    "QtNetwork": ("plugins/tls/libqsecuretransportbackend.a",
                  "plugins/networkinformation/libqapplenetworkinformation.a"),
    "QtSql": ("plugins/sqldrivers/libqsqlite.a",),
}


def enabled_plugins(cfg: IOSConfig) -> list[str]:
    """Plugin archive paths to link: _QT_PLUGINS plus module-gated plugins
    from _QT_PLUGIN_MODULE_GATE."""
    plugins = list(_QT_PLUGINS)
    for module in cfg.qt_modules:
        plugins.extend(_QT_PLUGIN_MODULE_GATE.get(module, ()))
    return plugins


_PERMISSION_PLUGIN_PREFIX = "plugins/permissions/"

_PLUGIN_TARGETS_LOCATION_RE = re.compile(
    r'IMPORTED_LOCATION_RELEASE\s+"[^"]*?/(plugins/[^"]+)"'
)


def _plugin_class_name(cfg: IOSConfig, plugin_rel: str) -> str | None:
    """QT_PLUGIN_CLASS_NAME for a regular (non-QML) plugin, found by matching
    its archive path against IMPORTED_LOCATION_RELEASE across lib/cmake/,
    since each plugin's targets file lives under its own module's package."""
    for targets_release in (cfg.qt_ios / "lib" / "cmake").glob("*/*PluginTargets-release.cmake"):
        m = _PLUGIN_TARGETS_LOCATION_RE.search(targets_release.read_text())
        if not m or m.group(1) != plugin_rel:
            continue
        targets_file = targets_release.with_name(
            targets_release.name.replace("-release.cmake", ".cmake")
        )
        if not targets_file.is_file():
            return None
        cm = re.search(r'QT_PLUGIN_CLASS_NAME\s+"([^"]+)"', targets_file.read_text())
        return cm.group(1) if cm else None
    return None


def resolve_plugin_class_names(cfg: IOSConfig) -> list[str]:
    """Class names for Q_IMPORT_PLUGIN, for every enabled_plugins() entry
    except plugins/permissions/* (already registered by PySide6's glue
    code -- see _QT_PLUGINS above)."""
    names = []
    for plugin_rel in enabled_plugins(cfg):
        if plugin_rel.startswith(_PERMISSION_PLUGIN_PREFIX):
            continue
        name = _plugin_class_name(cfg, plugin_rel)
        if name is not None:
            names.append(name)
    return names


# Qt module dependency resolution (via .prl files)
# Each <name>.framework/<name>.prl's QMAKE_PRL_LIBS_FOR_CMAKE lists its
# dependencies (Qt modules, system frameworks, bundled libs, resource
# objects, linker flags) -- resolved recursively instead of hand-maintained.

@dataclass
class QtDependencies:
    frameworks: list[str] = field(default_factory=list)  # Qt module names, dependents before deps
    system_frameworks: list[str] = field(default_factory=list)  # iOS SDK frameworks
    bundled_libs: list[str] = field(default_factory=list)  # resolved .a paths
    resource_objects: list[str] = field(default_factory=list)  # resolved .o paths
    linker_flags: list[str] = field(default_factory=list)  # e.g. "-lz"


def _prl_tokens(prl_path: Path) -> list[tuple[str, str]]:
    """Parse QMAKE_PRL_LIBS_FOR_CMAKE into (kind, value) pairs, normalizing
    both '-framework X' forms (split or single-token) into ('framework', X)."""
    value = ""
    for line in prl_path.read_text().splitlines():
        line = line.strip()
        if line.startswith("QMAKE_PRL_LIBS_FOR_CMAKE"):
            _, _, value = line.partition("=")
            break

    tokens: list[tuple[str, str]] = []
    pending_framework = False
    for raw in (t for t in value.strip().split(";") if t):
        if pending_framework:
            tokens.append(("framework", raw))
            pending_framework = False
        elif raw == "-framework":
            pending_framework = True
        elif raw.startswith("-framework "):
            tokens.append(("framework", raw[len("-framework "):].strip()))
        else:
            tokens.append(("raw", raw))
    return tokens


def resolve_qt_dependencies(
    cfg: IOSConfig, modules: list[str], plugin_paths: list[str] | None = None
) -> QtDependencies:
    """Recursively resolve the full Qt module/framework/lib closure for the
    given modules and plugins, via their .prl files.
    """
    deps = QtDependencies()
    visited: set[str] = set()
    lib_dir = cfg.qt_ios / "lib"

    def absorb(prl_path: Path) -> None:
        for kind, value in _prl_tokens(prl_path):
            if kind == "framework":
                if (lib_dir / f"{value}.framework").is_dir():
                    visit(value)
                elif value not in deps.system_frameworks:
                    deps.system_frameworks.append(value)
                continue

            resolved = (
                value
                .replace("$$[QT_INSTALL_LIBS]", str(lib_dir))
                .replace("$$[QT_INSTALL_PLUGINS]", str(cfg.qt_ios / "plugins"))
                .replace("$$[QT_INSTALL_QML]", str(cfg.qt_ios / "qml"))
                .replace("$$[QT_INSTALL_PREFIX]", str(cfg.qt_ios))
            )
            if resolved.startswith("-F"):
                continue  # framework search path flag; handled separately
            elif resolved.endswith(".a"):
                if resolved not in deps.bundled_libs:
                    deps.bundled_libs.append(resolved)
            elif resolved.endswith(".o"):
                if resolved not in deps.resource_objects:
                    deps.resource_objects.append(resolved)
            elif resolved.startswith("-l") and resolved not in deps.linker_flags:
                deps.linker_flags.append(resolved)

    def visit(mod: str) -> None:
        if mod in visited:
            return
        visited.add(mod)
        prl_path = lib_dir / f"{mod}.framework" / f"{mod}.prl"
        if not prl_path.is_file():
            return

        # List the module itself before recursing, so a dependent always
        # precedes the dependencies whose symbols it references.
        deps.frameworks.append(mod)
        absorb(prl_path)

    for mod in modules:
        visit(mod)

    for plugin_rel in plugin_paths or []:
        prl_path = cfg.qt_ios / Path(plugin_rel).with_suffix(".prl")
        if prl_path.is_file():
            absorb(prl_path)

    # Drop a plugin's own archive from its resolved deps (its .prl often
    # references itself), so it isn't linked twice.
    own_plugin_paths = {str(cfg.qt_ios / p) for p in (plugin_paths or [])}
    deps.bundled_libs = [p for p in deps.bundled_libs if p not in own_plugin_paths]

    return deps


_QML_RESOURCE_PATH_RE = re.compile(
    r'\$\$\[QT_INSTALL_PREFIX\]/qml/([A-Za-z0-9_]+(?:/[A-Za-z0-9_]+)*)/objects-'
)

_QT_QUICK_CONTROLS_NON_STYLE_DIRS = {"impl", "designer"}


@dataclass
class QmlPlugin:
    subdir: str  # e.g. "QtQuick/Controls"
    archive_path: Path  # absolute path to the lib*.a
    class_name: str | None  # for Q_IMPORT_PLUGIN; None if undiscoverable


def _qml_plugin_archive(cfg: IOSConfig, subdir: str) -> Path | None:
    """The one lib*.a directly inside qt_ios/qml/<subdir>/"""
    qml_dir = cfg.qt_ios / "qml" / subdir
    candidates = [
        archive for archive in sorted(qml_dir.glob("lib*.a")) if "_debug" not in archive.stem
    ]
    return candidates[0] if candidates else None


def _qml_plugin_class_name(cfg: IOSConfig, archive_path: Path) -> str | None:
    """QT_PLUGIN_CLASS_NAME for Q_IMPORT_PLUGIN, read from the plugin's own
    CMake targets file under lib/cmake/Qt6Qml/QmlPlugins/."""
    plugin_name = archive_path.stem
    if plugin_name.startswith("lib"):
        plugin_name = plugin_name[3:]
    targets_file = (cfg.qt_ios / "lib" / "cmake" / "Qt6Qml" / "QmlPlugins"
                    / f"Qt6{plugin_name}Targets.cmake")
    if not targets_file.is_file():
        return None
    m = re.search(r'QT_PLUGIN_CLASS_NAME\s+"([^"]+)"', targets_file.read_text())
    return m.group(1) if m else None


def resolve_qml_plugins(cfg: IOSConfig, qml_modules: list[str]) -> list[QmlPlugin]:
    visited: set[str] = set()
    result: list[QmlPlugin] = []

    def visit(subdir: str) -> None:
        if subdir in visited:
            return

        visited.add(subdir)
        archive = _qml_plugin_archive(cfg, subdir)
        if archive is None:
            return

        result.append(QmlPlugin(subdir, archive, _qml_plugin_class_name(cfg, archive)))

        prl_path = archive.with_suffix(".prl")
        if not prl_path.is_file():
            return
        for kind, value in _prl_tokens(prl_path):
            if kind != "raw":
                continue
            m = _QML_RESOURCE_PATH_RE.search(value)
            if m and m.group(1) != subdir:
                visit(m.group(1))

    # e.g "QtQuick.Controls" -> qml/QtQuick/Controls
    for mod in qml_modules:
        visit(mod.replace(".", "/"))

    if "QtQuick/Controls" in visited:
        has_style = any(
            s.startswith("QtQuick/Controls/")
            and s.split("/")[2] not in _QT_QUICK_CONTROLS_NON_STYLE_DIRS
            for s in visited
        )
        if not has_style:
            # Qt's own default style depends on platform
            visit("QtQuick/Controls/iOS")

    return result
