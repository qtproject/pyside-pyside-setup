#############################################################################
##
## Copyright (C) 2022 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of Qt for Python.
##
## $QT_BEGIN_LICENSE:LGPL$
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## GNU Lesser General Public License Usage
## Alternatively, this file may be used under the terms of the GNU Lesser
## General Public License version 3 as published by the Free Software
## Foundation and appearing in the file LICENSE.LGPL3 included in the
## packaging of this file. Please review the following information to
## ensure the GNU Lesser General Public License version 3 requirements
## will be met: https://www.gnu.org/licenses/lgpl-3.0.html.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 2.0 or (at your option) the GNU General
## Public license version 3 or any later version approved by the KDE Free
## Qt Foundation. The licenses are as published by the Free Software
## Foundation and appearing in the file LICENSE.GPL2 and LICENSE.GPL3
## included in the packaging of this file. Please review the following
## information to ensure the GNU General Public License requirements will
## be met: https://www.gnu.org/licenses/gpl-2.0.html and
## https://www.gnu.org/licenses/gpl-3.0.html.
##
## $QT_END_LICENSE$
##
#############################################################################

import os
import platform
import sys
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from pathlib import Path
from shutil import copy, rmtree
from sysconfig import get_config_var
from typing import List, Optional, Tuple

import build  # type: ignore
from build_scripts.wheel_files import (ModuleData,  # type: ignore
                                       wheel_files_pyside_addons,
                                       wheel_files_pyside_essentials)


@dataclass
class SetupData:
    name: str
    version: str
    description: str
    long_description: str
    console_scripts: List[str]


def get_version_from_package(name: str) -> str:
    # Get version from the already configured '__init__.py' file
    version = ""
    with open(package_path / name / "__init__.py") as f:
        for line in f:
            if line.strip().startswith("__version__"):
                version = line.split("=")[1].strip().replace('"', "")
                break
    return version


def get_manifest(wheel_name: str, data: List[ModuleData]) -> str:
    lines = []

    for module in data:
        # It's crucial to have this adjust method here
        # because it include all the necessary modifications to make
        # our soltuion work on the three main platforms.
        module.adjusts_paths_and_extensions()

        for field in module.get_fields():
            if field == "name":
                lines.append(f"# {getattr(module, field)}")
                continue
            if field == "ext":
                continue
            for line in getattr(module, field):
                if field in ("examples", "extra_dirs", "qml", "plugins"):
                    lines.append(f"graft PySide6/{line}")
                elif field == "qtlib" and sys.platform == "darwin":
                    lines.append(f"graft PySide6/{line}")
                else:
                    lines.append(f"include PySide6/{line}")
        lines.append("recursive-exclude PySide6 *qt.conf*")
        lines.append("")

    # Skip certain files if needed
    lines.append("recursive-exclude PySide6/Qt/qml *.debug")

    return "\n".join(lines)


def generate_setup_cfg(artifacts: Path, setup: SetupData) -> str:
    content = None
    _os = sys.platform
    arch = platform.machine()

    # as Qt6 we know it's GLIBC 2.28 on RHEL 8.4
    _tag = ""
    if _os == "linux":
        glibc = platform.libc_ver()[1].replace(".", "_")
        # Will generate manylinux_2_28_x86_64
        _tag = f"manylinux_{glibc}_{arch}"
    elif _os == "darwin":
        target = get_config_var("MACOSX_DEPLOYMENT_TARGET")
        if not target:
            print("Error: couldn't get the value from MACOSX_DEPLOYMENT_TARGET. "
                  "Falling back to local platform version.")
            mac_ver, _, _ = platform.mac_ver()
            # We get 10.14.2 for example, and transform into 10_14
            target = "_".join(mac_ver.split(".")[:2])
        else:
            version = target.split(".")
            if len(version) > 1:
                target = "_".join(version)
            else:
                target = f"{version[0]}_0"
        # TODO: Make it general
        # To check if is compatible with 64bit on multi-arch systems
        # is_64bits = sys.maxsize > 2**32
        #
        # We know the CI builds universal2 wheels
        _tag = f"macosx_{target}_universal2"
    elif _os == "win32":
        win_arch = platform.architecture()[0]
        msvc_arch = "x86" if win_arch.startswith("32") else "amd64"
        _tag = f"win_{msvc_arch}"

    with open(artifacts / "setup.cfg.base") as f:
        content = f.read().format(
            name=setup.name,
            version=setup.version,
            description=setup.description,
            long_description=setup.long_description,
            tag=_tag,
        )

    return content


def generate_setup_py(artifacts: Path, setup: SetupData):
    content = None
    _name = setup.name

    # To get the 'abi3' tag on the wheel name, we need to use
    # a fake extension to activate the limited-api option.
    # Because of the order of copying, we will use a name of a real
    # module for each package, so it gets overwrited.
    if _name == "PySide6":
        fext = "PySide6/QtCore"
    elif _name == "PySide6_Addons":
        fext = "PySide6/Qt3DCore"
    else:
        fext = "Shiboken"

    # Installing dependencies
    install_requires = []
    if name == "PySide6":
        install_requires.append(f"shiboken6=={setup.version}")
        install_requires.append(f"PySide6_Essentials=={setup.version}")
        install_requires.append(f"PySide6_Addons=={setup.version}")
    elif _name == "PySide6_Essentials":
        install_requires.append(f"shiboken6=={setup.version}")
    elif _name == "PySide6_Addons":
        install_requires.append(f"shiboken6=={setup.version}")
        install_requires.append(f"PySide6_Essentials=={setup.version}")

    # For special wheels based on 'PySide6'
    # we force the name to be PySide6 for the package_name,
    # so we can take the files from that packaged-directory
    if setup.name in ("PySide6_Essentials", "PySide6_Addons"):
        _name = "PySide6"

    with open(artifacts / "setup.py.base") as f:
        content = f.read().format(
            name=_name,
            fake_ext=fext,
            install=install_requires,
            console_scripts={"console_scripts": setup.console_scripts},
        )

    return content


def wheel_shiboken_generator() -> Tuple[SetupData, None]:
    setup = SetupData(
        name="shiboken6_generator",
        version=get_version_from_package("shiboken6_generator"),
        description="Python/C++ bindings generator",
        long_description="README.shiboken6-generator.md",
        console_scripts=[
            "shiboken6 = shiboken6_generator.scripts.shiboken_tool:main",
            "shiboken6-genpyi = shiboken6_generator.scripts.shiboken_tool:genpyi",
        ],
    )

    return setup, None


def wheel_shiboken_module() -> Tuple[SetupData, None]:
    setup = SetupData(
        name="shiboken6",
        version=get_version_from_package("shiboken6"),
        description="Python/C++ bindings helper module",
        long_description="README.shiboken6.md",
        console_scripts=[],
    )

    return setup, None


def wheel_pyside6_essentials() -> Tuple[SetupData, List[ModuleData]]:
    setup = SetupData(
        name="PySide6_Essentials",
        version=get_version_from_package("PySide6"),  # we use 'PySide6' here
        description="Python bindings for the Qt cross-platform application and UI framework (Essentials)",
        long_description="README.pyside6_essentials.md",
        console_scripts=[
            "pyside6-uic = PySide6.scripts.pyside_tool:uic",
            "pyside6-rcc = PySide6.scripts.pyside_tool:rcc",
            "pyside6-assistant = PySide6.scripts.pyside_tool:assistant",
            "pyside6-designer= PySide6.scripts.pyside_tool:designer",
            "pyside6-linguist = PySide6.scripts.pyside_tool:linguist",
            "pyside6-lupdate = PySide6.scripts.pyside_tool:lupdate",
            "pyside6-lrelease = PySide6.scripts.pyside_tool:lrelease",
            "pyside6-genpyi = PySide6.scripts.pyside_tool:genpyi",
            "pyside6-metaobjectdump = PySide6.scripts.pyside_tool:metaobjectdump",
            "pyside6-qmltyperegistrar = PySide6.scripts.pyside_tool:qmltyperegistrar",
            "pyside6-qmllint = PySide6.scripts.pyside_tool:qmllint",
        ],
    )

    data = wheel_files_pyside_essentials()

    return setup, data


def wheel_pyside6_addons() -> Tuple[SetupData, List[ModuleData]]:
    setup = SetupData(
        name="PySide6_Addons",
        version=get_version_from_package("PySide6"),  # we use 'PySide6' here
        description="Python bindings for the Qt cross-platform application and UI framework (Addons)",
        long_description="README.pyside6_addons.md",
        console_scripts=[],
    )

    data = wheel_files_pyside_addons()

    return setup, data


def wheel_pyside6() -> Tuple[SetupData, Optional[List[ModuleData]]]:
    setup = SetupData(
        name="PySide6",
        version=get_version_from_package("PySide6"),
        description="Python bindings for the Qt cross-platform application and UI framework",
        long_description="README.pyside6.md",
        console_scripts=[],
    )

    return setup, None


def get_build_directory(options: Namespace):
    _venv = ""
    _directories = list(Path("build").glob("qfp*"))
    # Search for a "--env" option first"
    if options.env is not None:
        _venv = f"{options.env}a"
    # Search for a 'qfp' directory second
    elif _directories and len(_directories) > 0:
        # Take the first 'qfp' directory
        _venv = _directories[0].name
    # Fall back to the virtual environment name
    else:
        # Check if we are using a virtual environment
        try:
            _venv = os.environ["VIRTUAL_ENV"]
            if not _venv:
                raise Exception("No virtual environment found")
            _venv = f"{_venv}a"
        except Exception as e:
            print(f"{type(e).__name__} : {e}")
            sys.exit(-1)

    return Path(_venv)


if __name__ == "__main__":

    # Command line option to find the build/<envname>a/package_for_wheels
    parser = ArgumentParser()
    parser.add_argument("--env", type=str, default=None)
    options = parser.parse_args()

    venv = get_build_directory(options)

    verbose = False
    # Setup paths
    current_path = Path(__file__).resolve().parent
    artifacts_path = Path("wheel_artifacts/")
    # the extra 'a' is for compatibility with the build_scripts
    # notation that adds an 'a' when using limited-api
    package_path = Path("build") / venv.name / "package_for_wheels"

    # Check for 'package_for_wheels' directory
    if not package_path.is_dir():
        print(f"Couldn't find the directory: {package_path}")
        print("Maybe your build used '--skip-packaging'?. Exiting")
        sys.exit(-1)

    setup_cfg_path = package_path / "setup.cfg"
    setup_py_path = package_path / "setup.py"

    base_files = [
        artifacts_path / "pyproject.toml",
        current_path / "LICENSE.COMMERCIAL",
        current_path / "LICENSE.FDL",
        current_path / "LICENSE.GPL2",
        current_path / "LICENSE.GPLv3",
        current_path / "LICENSE.GPLv3-EXCEPT",
        current_path / "LICENSE.LGPLv3",
    ]

    # Main generation
    wheels = {
        "shiboken6": wheel_shiboken_module,
        "shiboken6_generator": wheel_shiboken_generator,
        "PySide6_Essentials": wheel_pyside6_essentials,
        "PySide6_Addons": wheel_pyside6_addons,
        "PySide6": wheel_pyside6,
    }

    for name, wheel_info in wheels.items():

        print(f"Starting process for: {name}")
        setup, data = wheel_info()

        # 1. Generate 'setup.cfg'
        print("-- Generating setup.cfg")
        setup_cfg_content = generate_setup_cfg(artifacts_path, setup)
        with open(setup_cfg_path, "w") as f:
            f.write(setup_cfg_content)

        # 2. Generate 'setup.py'
        print("-- Generating setup.py")
        setup_py_content = generate_setup_py(artifacts_path, setup)
        with open(setup_py_path, "w") as f:
            f.write(setup_py_content)

        # 3. Create the 'MANIFEST.in'
        # Special case for shiboken and shiboken_generator
        # so we copy the whole directory, only PySide and derivatives
        # will need to have specific information
        print("-- Creating MANIFEST.in")
        if not data:
            if name == "PySide6":
                with open(package_path / "MANIFEST.in", "w") as f:
                    f.write(f"purge {name}\n")
            else:
                with open(package_path / "MANIFEST.in", "w") as f:
                    f.write(f"graft {name}\n")
        else:
            manifest_content = get_manifest(name, data)
            with open(package_path / "MANIFEST.in", "w") as f:
                f.write(manifest_content)

        # 4. copy configuration files to create the wheel
        print("-- Copy configuration files to create the wheel")
        _files: List[Path] = base_files + [Path(setup.long_description)]
        for fname in _files:
            copy(fname, package_path)

        # 5. call the build module to create the wheel
        # print("-- Creating wheel")
        # os.chdir(package_path)
        if not verbose:
            _runner = build.pep517.wrappers.quiet_subprocess_runner
        else:
            _runner = build.pep517.wrappers.default_subprocess_runner
        builder = build.ProjectBuilder(package_path, runner=_runner)
        builder.build("wheel", "dist_new")
        # os.chdir(current_path)

        # 6. Copy wheels back
        print("-- Copying wheels to dist_new/")
        dist_path = Path("dist_new")
        if not dist_path.is_dir():
            dist_path.mkdir()
        for wheel in Path(package_path / "dist_new").glob("*.whl"):
            copy(wheel, dist_path / wheel.name)

        # 7. Remove leftover files
        print("-- Removing leftover files")
        all_files = set(package_path.glob("*"))
        files_to_remove = all_files - {
            package_path / i for i in ("PySide6", "shiboken6", "shiboken6_generator")
        }
        for _f in files_to_remove:
            if _f.is_dir():
                rmtree(_f)
            elif _f.is_file():
                _f.unlink()
