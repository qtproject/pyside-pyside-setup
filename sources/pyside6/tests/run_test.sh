#!/bin/sh
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

# This is a nasty workaround of a CTest limitation
# of setting the environment variables for the test.

# $1: LD_LIBRARY_PATH
# $2: $PYTHONPATH
# $3: python executable
# $4: test file

export LD_LIBRARY_PATH=$1:$LD_LIBRARY_PATH
export PYTHONPATH=$2:$PYTHONPATH
$3 $4
