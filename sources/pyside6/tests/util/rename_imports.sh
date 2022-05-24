#!/bin/bash
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

# Rename import statements from .py script to use a specific module name
set -e

if [ $# -lt 3 ]; then
	echo "Usage: $0 <old_name> <new_name> <directories...>"
	exit 1
fi

old_name=$1; shift
new_name=$1; shift

find "$@" -name "*.py" -exec sed -ri "s/(import|from) $old_name/\1 $new_name/" '{}' \;
