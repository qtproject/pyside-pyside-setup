# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import logging
from pathlib import Path
from .. import run_command, BaseConfig, Config


class BuildozerConfig(BaseConfig):
    def __init__(self, buildozer_spec_file: Path, pysidedeploy_config: Config):
        super().__init__(buildozer_spec_file, comment_prefixes="#")
        self.set_value("app", "title", pysidedeploy_config.title)
        self.set_value("app", "package.name", pysidedeploy_config.title)
        self.set_value("app", "package.domain",
                       f"org.{pysidedeploy_config.title}")

        include_exts = self.get_value("app", "source.include_exts")
        include_exts = f"{include_exts},qml"
        self.set_value("app", "source.include_exts", include_exts, raise_warning=False)

        self.set_value("app", "requirements", "python3,shiboken6,PySide6")

        if pysidedeploy_config.ndk_path:
            self.set_value("app", "android.ndk_path", str(pysidedeploy_config.ndk_path))

        if pysidedeploy_config.sdk_path:
            self.set_value("app", "android.sdk_path", str(pysidedeploy_config.sdk_path))

        self.set_value("app", "android.add_jars", f"{str(pysidedeploy_config.jars_dir)}/*.jar")

        platform_map = {"aarch64": "arm64-v8a",
                        "armv7a": "armeabi-v7a",
                        "i686": "x86",
                        "x86_64": "x86_64"}
        arch = platform_map[pysidedeploy_config.arch]
        self.set_value("app", "android.archs", arch)

        # p4a changes
        logging.info("[DEPLOY] Using custom fork of python-for-android: "
                     "https://github.com/shyamnathp/python-for-android/tree/pyside_support")
        self.set_value("app", "p4a.fork", "shyamnathp")
        self.set_value("app", "p4a.branch", "pyside_support")
        self.set_value('app', "p4a.local_recipes", str(pysidedeploy_config.recipe_dir))
        self.set_value("app", "p4a.bootstrap", "qt")

        modules = ",".join(pysidedeploy_config.modules)
        local_libs = ",".join(pysidedeploy_config.local_libs)
        extra_args = (f"--qt-libs={modules} --load-local-libs={local_libs}")
        self.set_value("app", "p4a.extra_args", extra_args)

        # TODO: does not work atm. Seems like a bug with buildozer
        # change buildozer build_dir
        # self.set_value("buildozer", "build_dir", str(build_dir.relative_to(Path.cwd())))

        # change final apk/aab path
        self.set_value("buildozer", "bin_dir", str(pysidedeploy_config.exe_dir.resolve()))

        self.update_config()


class Buildozer:
    dry_run = False

    @staticmethod
    def initialize(pysidedeploy_config: Config):
        project_dir = Path(pysidedeploy_config.project_dir)
        buildozer_spec = project_dir / "buildozer.spec"
        if buildozer_spec.exists():
            logging.warning(f"[DEPLOY] buildozer.spec already present in {str(project_dir)}."
                            "Using it")
            return

        # creates buildozer.spec config file
        command = ["buildozer", "init"]
        run_command(command=command, dry_run=Buildozer.dry_run)
        if not Buildozer.dry_run:
            if not buildozer_spec.exists():
                raise RuntimeError(f"buildozer.spec not found in {Path.cwd()}")
            BuildozerConfig(buildozer_spec, pysidedeploy_config)

    @staticmethod
    def create_executable(mode: str):
        command = ["buildozer", "android", mode]
        run_command(command=command, dry_run=Buildozer.dry_run)
