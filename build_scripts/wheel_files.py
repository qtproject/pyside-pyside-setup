# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only


import json
import sys
from dataclasses import Field, dataclass, field
from typing import Dict, List


_pyside_package_path = None
_module_json_file_path = None


def set_pyside_package_path(p):
    global _pyside_package_path, _module_json_file_path
    _pyside_package_path = p
    qt_path = p
    if sys.platform != "win32":
        qt_path /= "Qt"
    _module_json_file_path = qt_path / "modules"


def get_module_json_data(module):
    """Read the JSON module data."""
    json_path = _module_json_file_path / f"{module}.json"
    json_data = None
    if not json_path.is_file():  # Wayland is Linux only
        print(f"Skipping {json_path}", file=sys.stderr)
        return None
    with json_path.open(encoding="utf-8") as json_file:
        json_data = json.load(json_file)
    return json_data


def get_module_plugins(json_data):
    """Return the plugins from the JSON module data."""
    if json_data:
        plugins = json_data.get("plugin_types")
        if plugins:
            return plugins
    return []


# This dataclass is in charge of holding the file information
# that each Qt module needs to have to be packaged in a wheel
@dataclass
class ModuleData:
    name: str
    ext: str = ""
    # Libraries not related to Qt modules
    lib: List[str] = field(default_factory=list)
    # Libraries related to Qt modules
    qtlib: List[str] = field(default_factory=list)
    # Files from the Qt/qml directory
    qml: List[str] = field(default_factory=list)
    pyi: List[str] = field(default_factory=list)
    translations: List[str] = field(default_factory=list)
    typesystems: List[str] = field(default_factory=list)
    include: List[str] = field(default_factory=list)
    glue: List[str] = field(default_factory=list)
    metatypes: List[str] = field(default_factory=list)
    plugins: List[str] = field(default_factory=list)

    # For special cases when a file/directory doesn't fall into
    # the previous categories.
    extra_dirs: List[str] = field(default_factory=list)
    extra_files: List[str] = field(default_factory=list)

    # Once the object is created, this method will be executed
    # and automatically will initialize some of the files that are
    # common for each module.
    # Note: The goal of this list is to be used for a MANIFEST.in
    #       meaning that in case a file gets added and it doesn't
    #       exist, the wheel creation process will only throw a
    #       warning, but it will not interrupt the packaging process.
    def __post_init__(self) -> None:
        if not self.ext:
            self.ext = self.get_extension_from_platform(sys.platform)
        _lo = self.name.lower()

        self.lib.append(f"Qt{self.name}")
        self.qtlib.append(f"libQt6{self.name}")
        if not len(self.qml):
            self.qml.append(f"Qt{self.name}")
        self.pyi.append(f"Qt{self.name}.pyi")
        self.typesystems.append(f"typesystem_{_lo}.xml")
        self.include.append(f"Qt{self.name}/*.h")
        self.glue.append(f"qt{_lo}.cpp")
        if not len(self.metatypes):
            self.metatypes.append(f"qt6{_lo}_relwithdebinfo_metatypes.json")

    # The PySide6 directory that gets packaged by the build_scripts
    # 'prepare_packages()' has a certain structure that depends on
    # the platform. Because that directory is the base for the wheel
    # packaging to work, we use the relative paths that are included
    # on each file.
    # Note: The MANIFEST.in file doesn't need to have '\' or other
    #       separator, and respect the '/' even on Windows.
    def adjusts_paths_and_extensions(self) -> None:
        if sys.platform == "win32":
            self.lib = [f"{i}.*{self.ext}".replace("lib", "") for i in self.lib]
            self.qtlib = [f"{i}.*dll".replace("lib", "") for i in self.qtlib]
            self.qml = [f"qml/{i}" for i in self.qml]
            self.translations = [f"translations/{i}" for i in self.translations]
            self.metatypes = [
                f"metatypes/{i}".replace("_relwithdebinfo", "") for i in self.metatypes
            ]
            self.plugins = [f"plugins/{i}" for i in self.plugins]
        else:
            if sys.platform == "darwin":
                self.qtlib = [f"Qt/lib/{i.replace('libQt6', 'Qt')}.framework" for i in self.qtlib]
                self.lib = [self.macos_pyside_wrappers_lib(i) for i in self.lib]
            else:
                self.lib = [f"{i}.*{self.ext}*" for i in self.lib]
                self.qtlib = [f"Qt/lib/{i}.*{self.ext}*" for i in self.qtlib]
            self.qml = [f"Qt/qml/{i}" for i in self.qml]
            self.translations = [f"Qt/translations/{i}" for i in self.translations]
            self.metatypes = [f"Qt/metatypes/{i}" for i in self.metatypes]
            self.plugins = [f"Qt/plugins/{i}" for i in self.plugins]

        self.typesystems = [f"typesystems/{i}" for i in self.typesystems]
        self.include = [f"include/{i}" for i in self.include]
        self.glue = [f"glue/{i}" for i in self.glue]

    def macos_pyside_wrappers_lib(self, s):
        if s.startswith("Qt"):
            return f"{s}.*so*"
        else:
            return f"{s}.*{self.ext}*"

    @classmethod
    def get_fields(cls) -> Dict[str, Field]:
        return cls.__dataclass_fields__

    @staticmethod
    def get_extension_from_platform(platform: str) -> str:
        if platform == "linux":
            return "so"
        elif platform == "darwin":
            return "dylib"
        elif platform == "win32":
            return "pyd"
        else:
            print(f"Platform '{platform}' not supported. Exiting")
            sys.exit(-1)


# Wheels auxiliary functions to return the ModuleData objects
# for each module that will be included in the wheel.

# PySide wheel
def wheel_files_pyside_essentials() -> List[ModuleData]:
    files = [
        module_QtCore(),
        module_QtGui(),
        module_QtWidgets(),
        module_QtHelp(),
        module_QtNetwork(),
        module_QtConcurrent(),
        module_QtDBus(),
        module_QtDesigner(),
        module_QtOpenGL(),
        module_QtOpenGLWidgets(),
        module_QtPrintSupport(),
        module_QtQml(),
        module_QtQuick(),
        module_QtQuickControls2(),
        module_QtQuickTest(),
        module_QtQuickWidgets(),
        module_QtXml(),
        module_QtTest(),
        module_QtSql(),
        module_QtSvg(),
        module_QtSvgWidgets(),
        module_QtUiTools(),
        module_QtExampleIcons(),
        # Only for plugins
        module_QtWayland(),
        # there are no bindings for these modules, but their binaries are
        # required for qmlls
        module_QtLanguageServer(),
        module_QtJsonRpc(),
    ]
    return files


# PySide Addons wheel
def wheel_files_pyside_addons() -> List[ModuleData]:
    files = [
        module_Qt3DAnimation(),
        module_Qt3DCore(),
        module_Qt3DExtras(),
        module_Qt3DInput(),
        module_Qt3DLogic(),
        module_Qt3DRender(),
        module_QtAxContainer(),
        module_QtBluetooth(),
        module_QtCharts(),
        module_QtDataVisualization(),
        module_QtGraphs(),
        module_QtMultimedia(),
        module_QtMultimediaWidgets(),
        module_QtNetworkAuth(),
        module_QtNfc(),
        module_QtPdf(),
        module_QtPdfWidgets(),
        module_QtPositioning(),
        module_QtQuick3D(),
        module_QtRemoteObjects(),
        module_QtScxml(),
        module_QtSensors(),
        module_QtSerialPort(),
        module_QtSerialBus(),
        module_QtSpatialAudio(),
        module_QtStateMachine(),
        module_QtTextToSpeech(),
        module_QtVirtualKeyboard(),
        module_QtWebChannel(),
        module_QtWebEngineCore(),
        module_QtWebEngineQuick(),
        module_QtWebEngineWidgets(),
        module_QtWebSockets(),
        module_QtHttpServer(),
        module_QtLocation(),
        module_QtAsyncio(),
    ]
    return files


# Functions that hold the information of all the files that needs
# to be included for the module to work, including Qt libraries,
# typesystems, glue, etc.
def module_QtCore() -> ModuleData:
    # QtCore
    data = ModuleData("Core")

    _typesystems = [
        "common.xml",
        "core_common.xml",
        "typesystem_core_common.xml",
        "typesystem_core_win.xml"
    ]

    data.typesystems.extend(_typesystems)
    data.include.append("*.h")
    if sys.platform == "win32":
        data.qtlib.append("pyside6.*")
        data.extra_files.append("qt.conf")
        data.extra_files.append("rcc.exe")
        data.extra_files.append("qtdiag.exe")
        data.extra_files.append("pyside6.*.lib")
        data.extra_files.append("resources/icudtl.dat")
        from build_scripts.platforms.windows_desktop import msvc_redist
        data.extra_files.extend(msvc_redist)
    else:
        data.lib.append("libpyside6.*")
        data.extra_files.append("Qt/libexec/rcc")
        data.extra_files.append("Qt/libexec/qt.conf")

    # *.py
    data.extra_dirs.append("support")

    # pyside-tools with python backend
    # Including the 'scripts' folder would include all the tools into the
    # PySide6_Essentials wheel. The moment when we add a tool that has a
    # dependency on a module in PySide6_AddOns, then we should split out
    # the following line into individual subfolder and files, to better
    # control which tool goes into which wheel
    data.extra_dirs.append("scripts")

    data.extra_dirs.append("typesystems/glue")

    data.extra_files.append("__feature__.pyi")
    data.extra_files.append("__init__.py")
    data.extra_files.append("_git_pyside_version.py")
    data.extra_files.append("_config.py")
    data.extra_files.append("py.typed")

    # Assistant
    if sys.platform == "darwin":
        data.extra_dirs.append("Assistant.app")
    else:
        data.extra_files.append("assistant*")
    data.translations.append("assistant_*")

    # Linguist
    if sys.platform == "darwin":
        data.extra_dirs.append("Linguist.app")
    else:
        data.extra_files.append("linguist*")
        data.extra_files.append("lconvert*")
    data.translations.append("linguist_*")

    data.extra_files.append("lrelease*")
    data.extra_files.append("lupdate*")

    # General translations
    data.translations.append("qtbase_*")
    data.translations.append("qt_help_*")
    data.translations.append("qt_*")

    # Extra libraries
    data.qtlib.append("libicudata*")
    data.qtlib.append("libicui18n*")
    data.qtlib.append("libicule*")
    data.qtlib.append("libiculx*")
    data.qtlib.append("libicutest*")
    data.qtlib.append("libicutu*")
    data.qtlib.append("libicuuc*")
    data.qtlib.append("libicuio*")

    return data


def module_QtGui() -> ModuleData:
    data = ModuleData("Gui")
    _typesystems = [
        "gui_common.xml",
        "typesystem_gui_common.xml",
        "typesystem_gui_mac.xml",
        "typesystem_gui_win.xml",
        "typesystem_gui_x11.xml",
        "typesystem_gui_rhi.xml"
    ]

    _metatypes = [
        "qt6eglfsdeviceintegrationprivate_relwithdebinfo_metatypes.json",
        "qt6eglfskmssupportprivate_relwithdebinfo_metatypes.json",
        "qt6kmssupportprivate_relwithdebinfo_metatypes.json",
        "qt6xcbqpaprivate_relwithdebinfo_metatypes.json",
    ]

    _qtlib = [
        "libQt6EglFSDeviceIntegration",
        "libQt6EglFsKmsSupport",
        "libQt6XcbQpa",
    ]

    data.typesystems.extend(_typesystems)
    data.metatypes.extend(_metatypes)
    data.qtlib.extend(_qtlib)

    json_data = get_module_json_data("Gui")
    data.plugins = get_module_plugins(json_data)
    data.extra_files.append("Qt/plugins/platforms/libqeglfs*")

    return data


def module_QtWidgets() -> ModuleData:
    data = ModuleData("Widgets")
    data.typesystems.append("widgets_common.xml")
    data.typesystems.append("typesystem_widgets_common.xml")

    if sys.platform == "win32":
        data.extra_files.append("uic.exe")
    else:
        data.extra_files.append("Qt/libexec/uic")
    json_data = get_module_json_data("Widgets")
    data.plugins = get_module_plugins(json_data)

    return data


def module_QtHelp() -> ModuleData:
    data = ModuleData("Help")

    return data


def module_QtNetwork() -> ModuleData:
    data = ModuleData("Network")
    json_data = get_module_json_data("Network")
    data.plugins = get_module_plugins(json_data)

    return data


def module_QtBluetooth() -> ModuleData:
    data = ModuleData("Bluetooth")
    data.translations.append("qtconnectivity_*")

    return data


def module_QtConcurrent() -> ModuleData:
    data = ModuleData("Concurrent")

    return data


def module_QtDBus() -> ModuleData:
    data = ModuleData("DBus")

    return data


def module_QtDesigner() -> ModuleData:
    data = ModuleData("Designer")
    data.qtlib.append("libQt6DesignerComponents")
    data.metatypes.append("qt6designercomponentsprivate_relwithdebinfo_metatypes.json")
    json_data = get_module_json_data("Designer")
    data.plugins = get_module_plugins(json_data)
    data.extra_files.append("Qt/plugins/assetimporters/libuip*")

    # Designer
    if sys.platform == "darwin":
        data.extra_dirs.append("Designer.app")
    else:
        data.extra_files.append("designer*")
    data.translations.append("designer_*")

    return data


def module_QtNfc() -> ModuleData:
    data = ModuleData("Nfc")

    return data


def module_QtPdf() -> ModuleData:
    data = ModuleData("Pdf")
    data.qtlib.append("libQt6PdfQuick")

    return data


def module_QtPdfWidgets() -> ModuleData:
    data = ModuleData("PdfWidgets")

    return data


def module_QtPrintSupport() -> ModuleData:
    data = ModuleData("PrintSupport")
    data.typesystems.append("typesystem_printsupport_common.xml")
    json_data = get_module_json_data("PrintSupport")
    data.plugins = get_module_plugins(json_data)

    return data


def module_QtQml() -> ModuleData:
    data = ModuleData("Qml")
    json_data = get_module_json_data("Qml")
    data.plugins = get_module_plugins(json_data)
    json_data = get_module_json_data("QmlCompilerPrivate")
    data.plugins += get_module_plugins(json_data)

    _qtlib = [
        "libQt6LabsAnimation",
        "libQt6LabsFolderListModel",
        "libQt6LabsQmlModels*",
        "libQt6LabsSettings",
        "libQt6LabsSharedImage",
        "libQt6LabsWavefrontMesh",
        "libQt6QmlCore",
        "libQt6QmlLocalStorage",
        "libQt6QmlModels",
        "libQt6QmlNetwork",
        "libQt6QmlWorkerScript",
        "libQt6QmlXmlListModel",
        "libQt6QmlCompiler"
    ]

    _include = [
        "pysideqml.h",
        "pysideqmlmacros.h",
        "pysideqmlregistertype.h",
    ]

    _metatypes = [
        "qt6labsanimation_relwithdebinfo_metatypes.json",
        "qt6labsfolderlistmodel_relwithdebinfo_metatypes.json",
        "qt6labsqmlmodels_relwithdebinfo_metatypes.json",
        "qt6labssettings_relwithdebinfo_metatypes.json",
        "qt6labssharedimage_relwithdebinfo_metatypes.json",
        "qt6labswavefrontmesh_relwithdebinfo_metatypes.json",
        "qt6packetprotocolprivate_relwithdebinfo_metatypes.json",
        "qt6qmlcompilerprivate_relwithdebinfo_metatypes.json",
        "qt6qmlcompilerplusprivate_relwithdebinfo_metatypes.json",
        "qt6qmlcore_relwithdebinfo_metatypes.json",
        "qt6qmldebugprivate_relwithdebinfo_metatypes.json",
        "qt6qmldomprivate_relwithdebinfo_metatypes.json",
        "qt6qmllintprivate_relwithdebinfo_metatypes.json",
        "qt6qmllocalstorage_relwithdebinfo_metatypes.json",
        "qt6qmlmodels_relwithdebinfo_metatypes.json",
        "qt6qmlworkerscript_relwithdebinfo_metatypes.json",
        "qt6qmlxmllistmodel_relwithdebinfo_metatypes.json",
    ]

    _qml = [
        "Qt/labs/animation",
        "Qt/labs/folderlistmodel",
        "Qt/labs/sharedimage",
        "Qt/labs/wavefrontmesh",
        "Qt/labs/qmlmodels",
        "Qt/labs/platform",
        "Qt/labs/settings",
    ]

    data.lib.append("libpyside6qml")
    json_data = get_module_json_data("Qml")
    data.plugins = get_module_plugins(json_data)
    data.translations.append("qtdeclarative_*")
    if sys.platform == "win32":
        data.extra_files.append("pyside6qml.*.lib")
        data.extra_files.append("pyside6qml.*.dll")
        data.extra_files.append("qml/builtins.qmltypes")
        data.extra_files.append("qml/jsroot.qmltypes")
        data.extra_files.append("qmlimportscanner.exe")
        data.extra_files.append("qmltyperegistrar.exe")
        data.extra_files.append("qmlcachegen.exe")
    else:
        data.extra_files.append("Qt/qml/builtins.qmltypes")
        data.extra_files.append("Qt/qml/jsroot.qmltypes")
        data.extra_files.append("Qt/libexec/qmlimportscanner")
        data.extra_files.append("Qt/libexec/qmltyperegistrar")
        data.extra_files.append("Qt/libexec/qmlcachegen")

    data.qtlib.extend(_qtlib)
    data.include.extend(_include)
    data.metatypes.extend(_metatypes)
    data.qml.extend(_qml)

    data.extra_files.append("qmllint*")
    data.extra_files.append("qmlformat*")
    data.extra_files.append("qmlls*")

    return data


def module_QtQuick() -> ModuleData:
    data = ModuleData("Quick")
    _metatypes = [
        "qt6quickcontrolstestutilsprivate_relwithdebinfo_metatypes.json",
        "qt6quickdialogs2_relwithdebinfo_metatypes.json",
        "qt6quickdialogs2quickimpl_relwithdebinfo_metatypes.json",
        "qt6quickdialogs2utils_relwithdebinfo_metatypes.json",
        "qt6quickeffectsprivate_relwithdebinfo_metatypes.json",
        "qt6quicketest_relwithdebinfo_metatypes.json",
        "qt6quicketestutilsprivate_relwithdebinfo_metatypes.json",
        "qt6quicklayouts_relwithdebinfo_metatypes.json",
        "qt6quickparticlesprivate_relwithdebinfo_metatypes.json",
        "qt6quickshapesprivate_relwithdebinfo_metatypes.json",
        "qt6quicktemplates2_relwithdebinfo_metatypes.json",
        "qt6quicktest_relwithdebinfo_metatypes.json",
        "qt6quicktestutilsprivate_relwithdebinfo_metatypes.json",
        "qt6quicktimeline_relwithdebinfo_metatypes.json",
    ]
    _qtlib = [
        "libQt6QuickEffects",
        "libQt6QuickDialogs2",
        "libQt6QuickDialogs2QuickImpl",
        "libQt6QuickDialogs2Utils",
        "libQt6QuickLayouts",
        "libQt6QuickParticles",
        "libQt6QuickShapes",
        "libQt6QuickTemplates2",
        "libQt6QuickTest",
        "libQt6QuickTimeline",
        "libQt6QuickTimelineBlendTrees",
    ]

    # Adding GraphicalEffects files
    data.qml.append("Qt5Compat/GraphicalEffects")

    data.qtlib.extend(_qtlib)
    data.metatypes.extend(_metatypes)
    json_data = get_module_json_data("Quick")
    data.plugins = get_module_plugins(json_data)

    return data


def module_QtQuickControls2() -> ModuleData:
    data = ModuleData("QuickControls2")
    data.qtlib.append("libQt6QuickControls2")
    data.qtlib.append("libQt6QuickControls2Basic")
    data.qtlib.append("libQt6QuickControls2BasicStyleImpl")
    data.qtlib.append("libQt6QuickControls2Fusion")
    data.qtlib.append("libQt6QuickControls2FusionStyleImpl")
    data.qtlib.append("libQt6QuickControls2Imagine")
    data.qtlib.append("libQt6QuickControls2ImagineStyleImpl")
    data.qtlib.append("libQt6QuickControls2Impl")
    data.qtlib.append("libQt6QuickControls2Material")
    data.qtlib.append("libQt6QuickControls2MaterialStyleImpl")
    data.qtlib.append("libQt6QuickControls2Universal")
    data.qtlib.append("libQt6QuickControls2UniversalStyleImpl")
    if sys.platform == "win32":
        data.qtlib.append("libQt6QuickControls2WindowsStyleImpl")
    elif sys.platform == "darwin":
        data.qtlib.append("libQt6QuickControls2IOSStyleImpl")
        data.qtlib.append("libQt6QuickControls2MacOSStyleImpl")

    data.metatypes.append("qt6quickcontrols2impl_relwithdebinfo_metatypes.json")

    return data


def module_QtQuickTest() -> ModuleData:
    data = ModuleData("QuickTest")

    return data


def module_QtQuickWidgets() -> ModuleData:
    data = ModuleData("QuickWidgets")
    return data


def module_QtXml() -> ModuleData:
    data = ModuleData("Xml")
    return data


def module_QtTest() -> ModuleData:
    data = ModuleData("Test")
    return data


def module_QtSql() -> ModuleData:
    data = ModuleData("Sql")
    json_data = get_module_json_data("Sql")
    data.plugins = get_module_plugins(json_data)

    return data


def module_QtSvg() -> ModuleData:
    data = ModuleData("Svg")

    return data


def module_QtSvgWidgets() -> ModuleData:
    data = ModuleData("SvgWidgets")

    return data


def module_QtTextToSpeech() -> ModuleData:
    data = ModuleData("TextToSpeech")
    json_data = get_module_json_data("TextToSpeech")
    data.plugins = get_module_plugins(json_data)

    return data


def module_QtUiTools() -> ModuleData:
    data = ModuleData("UiTools")

    return data


def module_QtWayland() -> ModuleData:
    data = ModuleData("Wayland")

    _qtlib = [
        "libQt6WaylandClient",
        "libQt6WaylandCompositor",
        "libQt6WaylandEglClientHwIntegration",
        "libQt6WaylandEglCompositorHwIntegration",
        "libQt6WlShellIntegration",
    ]

    _metatypes = [
        "qt6waylandclient_relwithdebinfo_metatypes.json",
        "qt6waylandeglclienthwintegrationprivate_relwithdebinfo_metatypes.json",
        "qt6wlshellintegrationprivate_relwithdebinfo_metatypes.json",
    ]

    data.qtlib.extend(_qtlib)
    data.metatypes.extend(_metatypes)
    json_data = get_module_json_data("WaylandClient")
    data.plugins = get_module_plugins(json_data)
    json_data = get_module_json_data("WaylandCompositor")
    data.plugins += get_module_plugins(json_data)
    return data


def module_Qt3DCore() -> ModuleData:
    data = ModuleData("3DCore", qml=["Qt3D/Core"])

    return data


def module_Qt3DAnimation() -> ModuleData:
    data = ModuleData("3DAnimation", qml=["Qt3D/Animation"])

    return data


def module_Qt3DExtras() -> ModuleData:
    data = ModuleData("3DExtras", qml=["Qt3D/Extras"])

    return data


def module_Qt3DInput() -> ModuleData:
    data = ModuleData("3DInput", qml=["Qt3D/Input"])
    json_data = get_module_json_data("3DInput")
    data.plugins = get_module_plugins(json_data)

    return data


def module_Qt3DLogic() -> ModuleData:
    data = ModuleData("3DLogic", qml=["Qt3D/Logic"])

    return data


def module_Qt3DRender() -> ModuleData:
    data = ModuleData("3DRender", qml=["Qt3D/Render"])
    json_data = get_module_json_data("3DRender")
    data.plugins = get_module_plugins(json_data)

    return data


def module_QtQuick3D() -> ModuleData:
    data = ModuleData("Quick3D")

    _qtlib = [
        "libQt6Quick3DAssetImport",
        "libQt6Quick3DAssetUtils",
        "libQt6Quick3DEffects",
        "libQt6Quick3DGlslParser",
        "libQt6Quick3DHelpers",
        "libQt6Quick3DHelpersImpl",
        "libQt6Quick3DIblBaker",
        "libQt6Quick3DParticleEffects",
        "libQt6Quick3DParticles",
        "libQt6Quick3DPhysics",
        "libQt6Quick3DPhysicsHelpers",
        "libQt6Quick3DRuntimeRender",
        "libQt6Quick3DSpatialAudio",
        "libQt6Quick3DUtils",
        "libQt6ShaderTools",
        "libQt63DQuick",
        "libQt63DQuickAnimation",
        "libQt63DQuickExtras",
        "libQt63DQuickExtras",
        "libQt63DQuickInput",
        "libQt63DQuickRender",
        "libQt63DQuickScene2D",
    ]

    _metatypes = [
        "qt63dquick_relwithdebinfo_metatypes.json",
        "qt63dquickanimation_relwithdebinfo_metatypes.json",
        "qt63dquickextras_relwithdebinfo_metatypes.json",
        "qt63dquickinput_relwithdebinfo_metatypes.json",
        "qt63dquickrender_relwithdebinfo_metatypes.json",
        "qt63dquickscene2d_relwithdebinfo_metatypes.json",
        "qt6quick3dassetimport_relwithdebinfo_metatypes.json",
        "qt6quick3dassetutils_relwithdebinfo_metatypes.json",
        "qt6quick3deffects_relwithdebinfo_metatypes.json",
        "qt6quick3dglslparserprivate_relwithdebinfo_metatypes.json",
        "qt6quick3dhelpers_relwithdebinfo_metatypes.json",
        "qt6quick3diblbaker_relwithdebinfo_metatypes.json",
        "qt6quick3dparticleeffects_relwithdebinfo_metatypes.json",
        "qt6quick3dparticles_relwithdebinfo_metatypes.json",
        "qt6quick3druntimerender_relwithdebinfo_metatypes.json",
        "qt6quick3dutils_relwithdebinfo_metatypes.json",
        "qt6shadertools_relwithdebinfo_metatypes.json",
    ]

    json_data = get_module_json_data("Quick3DAssetImport")
    data.plugins = get_module_plugins(json_data)
    data.qtlib.extend(_qtlib)
    data.metatypes.extend(_metatypes)
    data.extra_files.append("Qt/plugins/assetimporters/libassimp*")

    return data


def module_QtAxContainer() -> ModuleData:
    data = ModuleData("AxContainer")
    if sys.platform == "win32":
        data.metatypes.append("qt6axbaseprivate_metatypes.json")
        data.metatypes.append("qt6axserver_metatypes.json")

    return data


def module_QtWebEngineCore() -> ModuleData:
    data = ModuleData("WebEngineCore", qml=["QtWebEngine"])
    data.translations.append("qtwebengine_locales/*")
    data.translations.append("qtwebengine_*")
    data.extra_dirs.append("Qt/resources")
    if sys.platform == "win32":
        data.extra_files.append("resources/qtwebengine*.pak")
        data.extra_files.append("resources/v8_context_snapshot*.*")
        data.extra_files.append("QtWebEngineProcess.exe")
    else:
        data.extra_files.append("Qt/libexec/QtWebEngineProcess")

    return data


def module_QtWebEngineWidgets() -> ModuleData:
    data = ModuleData("WebEngineWidgets")

    return data


def module_QtWebEngineQuick() -> ModuleData:
    data = ModuleData("WebEngineQuick")
    data.qtlib.append("libQt6WebEngineQuickDelegatesQml")
    data.metatypes.append("qt6webenginequickdelegatesqml_relwithdebinfo_metatypes.json")

    return data


def module_QtCharts() -> ModuleData:
    data = ModuleData("Charts")
    data.qtlib.append("libQt6ChartsQml")
    data.metatypes.append("qt6chartsqml_relwithdebinfo_metatypes.json")

    return data


def module_QtDataVisualization() -> ModuleData:
    data = ModuleData("DataVisualization")
    data.qtlib.append("libQt6DataVisualizationQml")
    data.metatypes.append("qt6datavisualizationqml_relwithdebinfo_metatypes.json")
    data.typesystems.append("datavisualization_common.xml")

    return data


def module_QtGraphs() -> ModuleData:
    data = ModuleData("Graphs")

    return data


def module_QtMultimedia() -> ModuleData:
    data = ModuleData("Multimedia")
    data.qtlib.append("libQt6MultimediaQuick")
    data.metatypes.append("qt6multimediaquickprivate_relwithdebinfo_metatypes.json")

    json_data = get_module_json_data("Multimedia")
    data.translations.append("qtmultimedia_*")
    data.plugins = get_module_plugins(json_data)

    return data


def module_QtMultimediaWidgets() -> ModuleData:
    data = ModuleData("MultimediaWidgets")

    return data


def module_QtNetworkAuth() -> ModuleData:
    data = ModuleData("NetworkAuth")

    return data


def module_QtPositioning() -> ModuleData:
    data = ModuleData("Positioning")
    data.qtlib.append("libQt6PositioningQuick")
    data.metatypes.append("qt6positioningquick_relwithdebinfo_metatypes.json")
    json_data = get_module_json_data("Positioning")
    data.plugins = get_module_plugins(json_data)

    return data


def module_QtRemoteObjects() -> ModuleData:
    data = ModuleData("RemoteObjects")
    data.qtlib.append("libQt6RemoteObjectsQml")
    data.metatypes.append("qt6remoteobjectsqml_relwithdebinfo_metatypes.json")

    return data


def module_QtSensors() -> ModuleData:
    data = ModuleData("Sensors")
    data.qtlib.append("libQt6SensorsQuick")
    data.metatypes.append("qt6sensorsquick_relwithdebinfo_metatypes.json")
    json_data = get_module_json_data("Sensors")
    data.plugins = get_module_plugins(json_data)

    return data


def module_QtSerialPort() -> ModuleData:
    data = ModuleData("SerialPort")
    data.translations.append("qtserialport_*")

    return data


def module_QtSpatialAudio() -> ModuleData:
    data = ModuleData("SpatialAudio")
    data.metatypes.append("qt6spatialaudio_debug_metatypes.json")

    return data


def module_QtStateMachine() -> ModuleData:
    data = ModuleData("StateMachine")
    data.qtlib.append("libQt6StateMachineQml")
    data.metatypes.append("qt6statemachineqml_relwithdebinfo_metatypes.json")

    return data


def module_QtScxml() -> ModuleData:
    data = ModuleData("Scxml")
    data.qtlib.append("libQt6ScxmlQml")
    data.metatypes.append("qt6scxmlqml_relwithdebinfo_metatypes.json")
    json_data = get_module_json_data("Scxml")
    data.plugins = get_module_plugins(json_data)

    return data


def module_QtWebChannel() -> ModuleData:
    data = ModuleData("WebChannel")
    data.qtlib.append("libQt6WebChannelQuick")

    return data


def module_QtWebSockets() -> ModuleData:
    data = ModuleData("WebSockets")
    data.translations.append("qtwebsockets_*")

    return data


def module_QtOpenGL() -> ModuleData:
    data = ModuleData("OpenGL")
    _typesystems = [
        "opengl_common.xml",
        "typesystem_glgeti_v_includes.xml",
        "typesystem_glgeti_v_modifications.xml",
        "typesystem_glgetv_includes.xml",
        "typesystem_glgetv_modifications.xml",
        "typesystem_opengl_modifications1_0.xml",
        "typesystem_opengl_modifications1_0_compat.xml",
        "typesystem_opengl_modifications1_1.xml",
        "typesystem_opengl_modifications1_1_compat.xml",
        "typesystem_opengl_modifications1_2_compat.xml",
        "typesystem_opengl_modifications1_3_compat.xml",
        "typesystem_opengl_modifications1_4.xml",
        "typesystem_opengl_modifications1_4_compat.xml",
        "typesystem_opengl_modifications2_0.xml",
        "typesystem_opengl_modifications2_0_compat.xml",
        "typesystem_opengl_modifications2_1.xml",
        "typesystem_opengl_modifications3_0.xml",
        "typesystem_opengl_modifications3_3.xml",
        "typesystem_opengl_modifications3_3a.xml",
        "typesystem_opengl_modifications4_0.xml",
        "typesystem_opengl_modifications4_1.xml",
        "typesystem_opengl_modifications4_3.xml",
        "typesystem_opengl_modifications4_4.xml",
        "typesystem_opengl_modifications4_4_core.xml",
        "typesystem_opengl_modifications4_5.xml",
        "typesystem_opengl_modifications4_5_core.xml",
        "typesystem_opengl_modifications_va.xml",
    ]

    data.typesystems.extend(_typesystems)
    if sys.platform == "win32":
        data.extra_files.append("opengl32*.dll")

    return data


def module_QtOpenGLWidgets() -> ModuleData:
    data = ModuleData("OpenGLWidgets")
    return data


def module_QtSerialBus() -> ModuleData:
    data = ModuleData("SerialBus")
    json_data = get_module_json_data("SerialBus")
    data.plugins = get_module_plugins(json_data)
    return data


def module_QtVirtualKeyboard() -> ModuleData:
    data = ModuleData("VirtualKeyboard")
    data.plugins.append("virtualkeyboard")
    return data


def module_QtHttpServer() -> ModuleData:
    data = ModuleData("HttpServer")
    return data


def module_QtLanguageServer() -> ModuleData:
    data = ModuleData("LanguageServer")
    data.metatypes.append("qt6languageserverprivate_relwithdebinfo_metatypes.json")
    return data


def module_QtJsonRpc() -> ModuleData:
    data = ModuleData("JsonRpc")
    data.metatypes.append("qt6jsonrpcprivate_relwithdebinfo_metatypes.json")
    return data


def module_QtLocation() -> ModuleData:
    data = ModuleData("Location")
    json_data = get_module_json_data("Location")
    data.plugins = get_module_plugins(json_data)
    data.translations.append("qtlocation_*")
    return data


def module_QtAsyncio() -> ModuleData:
    data = ModuleData("Asyncio")
    data.extra_dirs.append("QtAsyncio")
    return data


def module_QtExampleIcons() -> ModuleData:
    data = ModuleData("ExampleIcons")
    return data
