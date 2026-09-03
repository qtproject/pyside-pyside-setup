# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
# Qt-Security score:significant reason:build-tool

import plistlib

from .ios_config import IOSConfig


def generate(cfg: IOSConfig) -> bytes:
    plist = {
        "CFBundleDisplayName": cfg.name,
        "CFBundleExecutable": "$(EXECUTABLE_NAME)",
        "CFBundleIdentifier": cfg.bundle_id,
        "CFBundleInfoDictionaryVersion": "6.0",
        "CFBundleName": cfg.name,
        "CFBundlePackageType": "APPL",
        "CFBundleShortVersionString": cfg.version,
        "CFBundleVersion": "1",
        "LSRequiresIPhoneOS": True,
        "UIApplicationSceneManifest": {
            "UIApplicationIsSceneMultitasking": True,
            "UISceneConfigurations": {
                "UIWindowSceneSessionRoleApplication": [
                    {"UISceneConfigurationName": "Default"},
                ],
            },
        },
        "UILaunchScreen": {},
        "UIRequiredDeviceCapabilities": ["arm64"],
        "UISupportedInterfaceOrientations": [
            "UIInterfaceOrientationPortrait",
            "UIInterfaceOrientationLandscapeLeft",
            "UIInterfaceOrientationLandscapeRight",
        ],
        "NSCameraUsageDescription": f"{cfg.name} uses the camera.",
        "NSMicrophoneUsageDescription": f"{cfg.name} uses the microphone.",
        "NSBluetoothAlwaysUsageDescription": f"{cfg.name} uses Bluetooth.",
        "NSContactsUsageDescription": f"{cfg.name} uses contacts.",
        "NSCalendarsUsageDescription": f"{cfg.name} uses the calendar.",
        "NSLocationWhenInUseUsageDescription": f"{cfg.name} uses your location.",
    }
    return plistlib.dumps(plist)
