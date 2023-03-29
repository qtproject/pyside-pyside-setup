# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

"""
    Extensive manual test of pyside6-android-deploy

    Note: Not to be added into the CI
"""

import logging
import unittest
import tempfile
import shutil
import sys
import os
import importlib
from pathlib import Path


class TestPySide6Deploy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pyside_root = Path(__file__).parents[5].resolve()
        example_root = cls.pyside_root / "examples"
        example_application = example_root / "gui" / "analogclock"
        cls.temp_dir = tempfile.mkdtemp()
        cls.temp_example = Path(
            shutil.copytree(example_application, Path(cls.temp_dir) / "analogclock")
        ).resolve()
        cls.current_dir = Path.cwd()

        sys.path.append(str(cls.pyside_root / "sources" / "pyside-tools"))
        cls.deploy_lib = importlib.import_module("deploy_lib")
        cls.android_deploy = importlib.import_module("android_deploy")
        sys.modules["android_deploy"] = cls.android_deploy

        if os.environ.get("WHEEL_PYSIDE") is not None:
            cls.pyside_wheel = Path(os.environ.get("WHEEL_PYSIDE")).resolve()
        else:
            raise Exception("Environment variable WHEEL_PYSIDE does not exist")

        if os.environ.get("WHEEL_SHIBOKEN") is not None:
            cls.shiboken_wheel = Path(os.environ.get("WHEEL_SHIBOKEN")).resolve()
        else:
            raise Exception("Environment variable WHEEL_SHIBOKEN does not exist")

    def setUp(self):
        os.chdir(self.temp_example)
        self.config_file = self.temp_example / "pysidedeploy.spec"

    def testDeployment(self):
        self.android_deploy.main(name="android_app", shiboken_wheel=self.shiboken_wheel,
                                 pyside_wheel=self.pyside_wheel, keep_deployment_files=True,
                                 loglevel=logging.INFO, force=True)

        print("Testing with config file")
        self.android_deploy.main(name="android_app", config_file=self.config_file,
                                 loglevel=logging.INFO, force=True)

    def testWithNdkSdk(self):
        if os.environ.get("ANDROID_SDK_ROOT") is not None:
            android_sdk_root = Path(os.environ.get("ANDROID_SDK_ROOT")).resolve()
        else:
            raise Exception("Environment variable ANDROID_SDK_ROOT does not exist")

        if os.environ.get("ANDROID_NDK_ROOT") is not None:
            android_ndk_root = Path(os.environ.get("ANDROID_NDK_ROOT")).resolve()
        else:
            raise Exception("Environment variable ANDROID_NDK_ROOT does not exist")

        self.android_deploy.main(name="android_app", shiboken_wheel=self.shiboken_wheel,
                                 pyside_wheel=self.pyside_wheel,
                                 ndk_path=android_ndk_root,
                                 sdk_path=android_sdk_root,
                                 keep_deployment_files=True,
                                 loglevel=logging.INFO, force=True)

    def tearDown(self) -> None:
        super().tearDown()
        os.chdir(self.current_dir)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(Path(cls.temp_dir))


if __name__ == "__main__":
    unittest.main()
