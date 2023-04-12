# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

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
                                       set_pyside_package_path,
                                       wheel_files_pyside_addons,
                                       wheel_files_pyside_essentials)
from build_scripts.utils import available_pyside_tools


PACKAGE_FOR_WHEELS = "package_for_wheels"


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
                if field in ("extra_dirs", "qml", "plugins"):
                    lines.append(f"graft PySide6/{line}")
                elif field == "qtlib" and sys.platform == "darwin":
                    lines.append(f"graft PySide6/{line}")
                else:
                    lines.append(f"include PySide6/{line}")
        lines.append("recursive-exclude PySide6 *qt.conf*")
        lines.append("")

    # Skip certain files if needed
    lines.append("recursive-exclude PySide6/Qt/qml *.debug")
    lines.append("prune PySide6/Qt/qml/QtQuick3D/MaterialEditor")

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


def wheel_pyside6_essentials(packaged_qt_tools_path: Path) -> Tuple[SetupData, List[ModuleData]]:
    set_pyside_package_path(packaged_qt_tools_path)
    _pyside_tools = available_pyside_tools(packaged_qt_tools_path, package_for_wheels=True)

    # replacing pyside6-android_deploy by pyside6-android-deploy for consistency
    # Also, the tool should not exist in any other platform than Linux
    _console_scripts = []
    if ("android_deploy" in _pyside_tools) and sys.platform.startswith("linux"):
        _console_scripts = ["pyside6-android-deploy = PySide6.scripts.pyside_tool:android_deploy"]
    _pyside_tools.remove("android_deploy")

    _console_scripts.extend([f"pyside6-{tool} = PySide6.scripts.pyside_tool:{tool}"
                            for tool in _pyside_tools])

    setup = SetupData(
        name="PySide6_Essentials",
        version=get_version_from_package("PySide6"),  # we use 'PySide6' here
        description="Python bindings for the Qt cross-platform application and UI framework (Essentials)",
        long_description="README.pyside6_essentials.md",
        console_scripts=_console_scripts
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


def venv_name():
    v = os.environ.get("VIRTUAL_ENV")
    return Path(v).name if v else None


def get_build_directory(options: Namespace):
    build_dir = Path("build")
    # Search for a "--env" option first", try postfix "a" for limited API or "d", debug
    venv = options.env if options.env else venv_name()
    if venv:
        for postfix in ("a", "d", ""):
            result = build_dir / f"{venv}{postfix}"
            if result.is_dir():
                return result
    if options.env:
        raise Exception(f'Invalid environment "{options.env}" passed')
    # Try explicit build-dir
    if options.build_dir and (Path(options.build_dir) / PACKAGE_FOR_WHEELS).is_dir():
        return Path(options.build_dir)
    # Fallback to existing dirs (skip "config.tests")
    for d in build_dir.glob("*"):
        if (d / PACKAGE_FOR_WHEELS).is_dir():
            print(
                "No valid environment or build directory was specified, so create_wheels is using "
                "the first valid directory it could find on its own. If this is not the one you "
                "want, use the --env or --build-dir options to provide it explicitly."
            )
            return d
    raise Exception("Unable to determine build directory, no matching virtual environment found")


if __name__ == "__main__":

    parser = ArgumentParser()
    # Command line option to find the build/<envname>a/package_for_wheels
    parser.add_argument(
        "--env", type=str, default=None,
        help="The env's name from which PySide was built such that the "
             "build directory is 'build/<envname>' (must contain a "
             "'package_for_wheels' folder"
    )
    # Alternatively, <build-dir> (must contain "package_for_wheels")
    parser.add_argument(
        "--build-dir", type=str, default=None,
        help="The directory where PySide was build (must contain a "
             "'package_for_wheels' folder"
    )
    options = parser.parse_args()

    build_directory = get_build_directory(options)

    verbose = False
    # Setup paths
    current_path = Path(__file__).resolve().parent
    artifacts_path = Path("wheel_artifacts/")
    # the extra 'a' is for compatibility with the build_scripts
    # notation that adds an 'a' when using limited-api
    package_path = build_directory / PACKAGE_FOR_WHEELS
    print(f'Using build dir "{build_directory.name}"')

    # Check for 'package_for_wheels' directory
    if not package_path.is_dir():
        print(f"Couldn't find the directory: {package_path}")
        print("Maybe your build used '--skip-packaging'?. Exiting")
        sys.exit(-1)

    setup_cfg_path = package_path / "setup.cfg"
    setup_py_path = package_path / "setup.py"

    base_files = [
        artifacts_path / "pyproject.toml",
        current_path / "LICENSES/GFDL-1.3-no-invariants-only.txt",
        current_path / "LICENSES/LicenseRef-Qt-Commercial.txt",
        current_path / "LICENSES/GPL-2.0-only.txt",
        current_path / "LICENSES/GPL-3.0-only.txt",
        current_path / "LICENSES/Qt-GPL-exception-1.0.txt",
        current_path / "LICENSES/LGPL-3.0-only.txt",
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
        setup, data = wheel_info() if not name=="PySide6_Essentials" else \
                      wheel_pyside6_essentials(package_path / "PySide6")

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
