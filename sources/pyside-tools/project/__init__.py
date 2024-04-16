# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

from dataclasses import dataclass

QTPATHS_CMD = "qtpaths6"
MOD_CMD = "pyside6-metaobjectdump"

PROJECT_FILE_SUFFIX = ".pyproject"
QMLDIR_FILE = "qmldir"

QML_IMPORT_NAME = "QML_IMPORT_NAME"
QML_IMPORT_MAJOR_VERSION = "QML_IMPORT_MAJOR_VERSION"
QML_IMPORT_MINOR_VERSION = "QML_IMPORT_MINOR_VERSION"
QT_MODULES = "QT_MODULES"

METATYPES_JSON_SUFFIX = "metatypes.json"
TRANSLATION_SUFFIX = ".ts"
SHADER_SUFFIXES = ".vert", ".frag"


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


@dataclass(frozen=True)
class ClOptions(metaclass=Singleton):
    """
    Dataclass to store the cl options that needs to be passed as arguments.
    """
    dry_run: bool
    quiet: bool
    force: bool
    qml_module: bool


from .utils import (run_command, requires_rebuild, remove_path, package_dir, qtpaths,
                    qt_metatype_json_dir, resolve_project_file)
from .project_data import (is_python_file, ProjectData, QmlProjectData,
                           check_qml_decorators)
from .newproject import new_project, ProjectType
