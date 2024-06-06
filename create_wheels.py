# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import os
import platform
import sys
import importlib
import json
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from pathlib import Path
from shutil import copy, rmtree, copytree
from typing import List, Optional, Tuple

import build  # type: ignore
import pyproject_hooks
import build_scripts.wheel_files
from build_scripts.wheel_files import (ModuleData,  # type: ignore
                                       set_pyside_package_path,
                                       wheel_files_pyside_addons,
                                       wheel_files_pyside_essentials)
from build_scripts.utils import available_pyside_tools


PACKAGE_FOR_WHEELS = "package_for_wheels"
PYSIDE_DESCRIPTION = "Python bindings for the Qt cross-platform application and UI framework"


@dataclass
class SetupData:
    name: str
    version: tuple[str, str]
    description: str
    readme: str
    console_scripts: List[str]


def get_version_from_package(name: str, package_path: Path) -> tuple[str, str]:
    # Get version from the already configured '__init__.py' file
    version = ""
    with open(package_path / name / "__init__.py") as f:
        for line in f:
            if line.strip().startswith("__version__"):
                version = line.split("=")[1].strip().replace('"', "")
                break
    return version, f"{name}.__init__.__version__"


def create_module_plugin_json(wheel_name: str, data: List[ModuleData], package_path: Path):
    all_plugins = {}

    for module in data:
        all_plugins[module.name] = getattr(module, "plugins")

    # write the dictionary modules->plugins dictionary to a .json file and include this .json file
    # This file is picked up by the deployment tool to figure out the plugin dependencies
    # of a PySide6 application
    if all_plugins:
        with open(f"{package_path}/PySide6/{wheel_name}.json", 'w') as fp:
            json.dump(all_plugins, fp, indent=4)


def get_manifest(wheel_name: str, data: List[ModuleData], package_path: Path) -> str:
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

    # adding PySide6_Essentials.json and PySide6_Addons.json
    lines.append(f"include PySide6/{wheel_name}.json")

    return "\n".join(lines)


def get_simple_manifest(name: str) -> str:
    if name == "PySide6":
        return f"prune {name}\n"
    elif name == "PySide6_Examples":
        return "prune PySide6\ngraft PySide6/examples\n"
    return f"graft {name}\n"


def get_platform_tag() -> str:
    _os = sys.platform
    arch = platform.machine()

    # as Qt6 we know it's GLIBC 2.28 on RHEL 8.4
    _tag = ""
    if _os == "linux":
        glibc = platform.libc_ver()[1].replace(".", "_")
        # Will generate manylinux_2_28_x86_64
        _tag = f"manylinux_{glibc}_{arch}"
    elif _os == "darwin":
        # find _config.py and load it to obtain __qt_macos_min_deployment_target__
        target = None
        config_py = package_path / "shiboken6" / "_config.py"
        if not config_py.exists():
            raise RuntimeError(f"Unable to find {str(config_py)}")

        module_name = config_py.name[:-3]
        _spec = importlib.util.spec_from_file_location(f"{module_name}", config_py)
        if _spec is None:
            raise RuntimeError(f"Unable to create ModuleSpec from {str(config_py)}")
        _module = importlib.util.module_from_spec(_spec)
        if _spec.loader is None:
            raise RuntimeError(f"ModuleSpec for {module_name} has no valid loader.")
        _spec.loader.exec_module(module=_module)
        target = _module.__qt_macos_min_deployment_target__

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

    return _tag


def generate_pyproject_toml(artifacts: Path, setup: SetupData) -> str:
    content = None

    _name = setup.name
    _tag = get_platform_tag()

    _console_scripts = ""
    if setup.console_scripts:
        _formatted_console_scripts = "\n".join(setup.console_scripts)
        _console_scripts = f"[project.scripts]\n{_formatted_console_scripts}"

    # Installing dependencies
    _dependencies = []
    if _name in ("PySide6", "PySide6_Examples"):
        _dependencies.append(f"shiboken6=={setup.version[0]}")
        _dependencies.append(f"PySide6_Essentials=={setup.version[0]}")
        _dependencies.append(f"PySide6_Addons=={setup.version[0]}")
    elif _name == "PySide6_Essentials":
        _dependencies.append(f"shiboken6=={setup.version[0]}")
    elif _name == "PySide6_Addons":
        _dependencies.append(f"shiboken6=={setup.version[0]}")
        _dependencies.append(f"PySide6_Essentials=={setup.version[0]}")
    elif _name == "shiboken6_generator":
        _dependencies.append(f"shiboken6=={setup.version[0]}")

    with open(artifacts / "pyproject.toml.base") as f:
        content = (
            f.read()
            .replace("PROJECT_NAME", f'"{setup.name}"')
            .replace("PROJECT_VERSION", f'"{setup.version[1]}"')
            .replace("PROJECT_DESCRIPTION", f'"{setup.description}"')
            .replace("PROJECT_README", f'"{setup.readme}"')
            .replace("PROJECT_TAG", f'"{_tag}"')
            .replace("PROJECT_SCRIPTS", _console_scripts)
            .replace("PROJECT_DEPENDENCIES", f"{_dependencies}")
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

    # For special wheels based on 'PySide6'
    # we force the name to be PySide6 for the package_name,
    # so we can take the files from that packaged-directory
    if setup.name in ("PySide6_Essentials", "PySide6_Addons", "PySide6_Examples"):
        _name = "PySide6"

    with open(artifacts / "setup.py.base") as f:
        content = f.read().format(
            name=_name,
            fake_ext=fext,
        )

    return content


def wheel_shiboken_generator(package_path: Path) -> Tuple[SetupData, None]:
    setup = SetupData(
        name="shiboken6_generator",
        version=get_version_from_package("shiboken6_generator", package_path),
        description="Python/C++ bindings generator",
        readme="README.shiboken6-generator.md",
        console_scripts=[
            'shiboken6 = "shiboken6_generator.scripts.shiboken_tool:main"',
            'shiboken6-genpyi = "shiboken6_generator.scripts.shiboken_tool:genpyi"',
        ],
    )

    return setup, None


def wheel_shiboken_module(package_path: Path) -> Tuple[SetupData, None]:
    setup = SetupData(
        name="shiboken6",
        version=get_version_from_package("shiboken6", package_path),
        description="Python/C++ bindings helper module",
        readme="README.shiboken6.md",
        console_scripts=[],
    )

    return setup, None


def wheel_pyside6_essentials(package_path: Path) -> Tuple[SetupData, List[ModuleData]]:
    packaged_qt_tools_path = package_path / "PySide6"
    set_pyside_package_path(packaged_qt_tools_path)
    _pyside_tools = available_pyside_tools(packaged_qt_tools_path, package_for_wheels=True)

    # replacing pyside6-android_deploy by pyside6-android-deploy for consistency
    # Also, the tool should not exist in any other platform than Linux and macOS
    _console_scripts = []
    if ("android_deploy" in _pyside_tools) and sys.platform in ("linux", "darwin"):
        _console_scripts = ['pyside6-android-deploy = "PySide6.scripts.pyside_tool:android_deploy"']
    _pyside_tools.remove("android_deploy")

    _console_scripts.extend([f'pyside6-{tool} = "PySide6.scripts.pyside_tool:{tool}"'
                            for tool in _pyside_tools])

    setup = SetupData(
        name="PySide6_Essentials",
        version=get_version_from_package("PySide6", package_path),  # we use 'PySide6' here
        description=f"{PYSIDE_DESCRIPTION} (Essentials)",
        readme="README.pyside6_essentials.md",
        console_scripts=_console_scripts
    )

    data = wheel_files_pyside_essentials()

    return setup, data


def wheel_pyside6_addons(package_path: Path) -> Tuple[SetupData, List[ModuleData]]:
    setup = SetupData(
        name="PySide6_Addons",
        version=get_version_from_package("PySide6", package_path),  # we use 'PySide6' here
        description=f"{PYSIDE_DESCRIPTION} (Addons)",
        readme="README.pyside6_addons.md",
        console_scripts=[],
    )

    data = wheel_files_pyside_addons()

    return setup, data


def wheel_pyside6(package_path: Path) -> Tuple[SetupData, Optional[List[ModuleData]]]:
    setup = SetupData(
        name="PySide6",
        version=get_version_from_package("PySide6", package_path),
        description=PYSIDE_DESCRIPTION,
        readme="README.pyside6.md",
        console_scripts=[],
    )

    return setup, None


def wheel_pyside6_examples(package_path: Path) -> Tuple[SetupData, Optional[List[ModuleData]]]:
    setup = SetupData(
        name="PySide6_Examples",
        version=get_version_from_package("PySide6", package_path),
        description="Examples for the Qt for Python project",
        readme="README.pyside6_examples.md",
        console_scripts=[],
    )

    return setup, None


def copy_examples_for_wheel(package_path: Path):
    # Copying examples
    try:
        copytree("examples", package_path / "PySide6" / "examples", dirs_exist_ok=True)
    except OSError as e:
        print("Error trying to copy the examples directory:", e, file=sys.stderr)
        sys.exit(-1)


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


def check_modules_consistency():
    available_functions = dir(build_scripts.wheel_files)
    functions = [i.replace("module_", "") for i in available_functions if i.startswith("module_")]

    sources = [i.stem for i in Path("sources/pyside6/PySide6/").glob("Qt*")]

    missing_modules = set(sources) - set(functions)

    if len(missing_modules):
        print("Warning: the following modules don't have a function "
              f"in 'build_scripts/wheel_files.py':\n  {missing_modules}")

    # Check READMEs
    readme_modules = set()
    for r in Path(".").glob("README.pyside6*"):
        with open(r) as f:
            for line in f:
                if line.startswith("* Qt"):
                    readme_modules.add(line.strip().replace("* ", ""))

    missing_modules_readme = set(sources) - readme_modules

    if len(missing_modules_readme):
        print("Warning: the following modules are not in READMEs :"
              f"\n  {missing_modules_readme}")


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

    # Sanity check between the available modules,
    # and the functions in build_scripts/wheel_files.py
    check_modules_consistency()

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

    setup_py_path = package_path / "setup.py"
    pyproject_toml_path = package_path / "pyproject.toml"

    base_files = [
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
        "PySide6_Examples": wheel_pyside6_examples,
    }

    for name, wheel_info in wheels.items():

        print(f"Starting process for: {name}")
        setup, data = wheel_info(package_path)

        # 1. Generate 'setup.py'
        print("-- Generating setup.py")
        setup_py_content = generate_setup_py(artifacts_path, setup)
        with open(setup_py_path, "w") as f:
            f.write(setup_py_content)

        # 2. Generate 'pyproject.toml'
        print("-- Generating pyproject.toml")
        pyproject_toml_content = generate_pyproject_toml(artifacts_path, setup)
        with open(pyproject_toml_path, "w") as f:
            f.write(pyproject_toml_content)

        # 3. Create PySide_Essentials.json and PySide_Addons.json
        # creates a json file mapping each Qt module to the possible plugin dependencies
        if data is not None:
            print(f"-- Creating {name}.json")
            create_module_plugin_json(name, data, package_path)

        # 4. Create the 'MANIFEST.in'
        # Special case for shiboken and shiboken_generator
        # so we copy the whole directory, only PySide and derivatives
        # will need to have specific information
        print("-- Creating MANIFEST.in")
        if data is None:
            manifest_content = get_simple_manifest(name)
        else:
            manifest_content = get_manifest(name, data, package_path)
        with open(package_path / "MANIFEST.in", "w") as f:
            f.write(manifest_content)

        # 5. copy configuration files to create the wheel
        print("-- Copy configuration files to create the wheel")
        if name == "PySide6_Examples":
            copy_examples_for_wheel(package_path)
        _files: List[Path] = base_files + [Path(setup.readme)]
        for fname in _files:
            copy(fname, package_path)

        # 6. call the build module to create the wheel
        print("-- Creating wheels")
        if not verbose:
            _runner = pyproject_hooks.quiet_subprocess_runner
        else:
            _runner = pyproject_hooks.default_subprocess_runner
        builder = build.ProjectBuilder(package_path, runner=_runner)
        builder.build("wheel", "dist")

        # 7. Copy wheels back
        print("-- Copying wheels to dist/")
        dist_path = Path("dist")
        if not dist_path.is_dir():
            dist_path.mkdir()
        for wheel in Path(package_path / "dist").glob("*.whl"):
            copy(wheel, dist_path / wheel.name)

        # 8. Remove leftover files
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
