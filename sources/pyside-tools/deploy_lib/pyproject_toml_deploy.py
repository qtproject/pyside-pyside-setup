# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
# Qt-Security score:significant reason:build-tool
from __future__ import annotations

import logging
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ModuleNotFoundError:
        tomllib = None  # type: ignore[assignment]

# Mapping from [tool.pyside6.deploy] TOML key → (spec section, spec key).
# Only user-intent keys are listed here;
# auto-derived fields (modules, plugins, qml_files, python_path, ...) are intentionally
# excluded because they are generated during the deployment process
_TOML_TO_SPEC: dict[str, tuple[str, str]] = {
    "title": ("app", "title"),
    "input_file": ("app", "input_file"),
    "icon": ("app", "icon"),
    "exec_directory": ("app", "exec_directory"),
    "mode": ("nuitka", "mode"),
    "extra_args": ("nuitka", "extra_args"),
    "macos_permissions": ("nuitka", "macos.permissions"),
}


def read_deploy_section(project_dir: Path) -> dict[tuple[str, str], str]:
    if tomllib is None:
        return {}

    pyproject_toml = project_dir / "pyproject.toml"
    if not pyproject_toml.exists():
        return {}

    try:
        root = tomllib.loads(pyproject_toml.read_text(encoding="utf-8"))
    except Exception as exc:
        logging.warning(f"[DEPLOY] Could not parse {pyproject_toml}: {exc}")
        return {}

    deploy_section = root.get("tool", {}).get("pyside6", {}).get("deploy", {})
    if not deploy_section:
        return {}

    logging.info(f"[DEPLOY] Reading deploy configuration from {pyproject_toml}")

    overrides: dict[tuple[str, str], str] = {}
    for toml_key, spec_location in _TOML_TO_SPEC.items():
        if toml_key in deploy_section:
            overrides[spec_location] = str(deploy_section[toml_key])
    return overrides
