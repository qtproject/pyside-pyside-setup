#!/usr/bin/env python
# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2021 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of Qt for Python.
##
## $QT_BEGIN_LICENSE:COMM$
##
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## $QT_END_LICENSE$
##
#############################################################################
import sys
import os
import subprocess

def main():
    # The tools listed as entrypoints in setup.py are copied to 'scripts/..'
    cmd = os.path.join("..", os.path.basename(sys.argv[0]))
    command = [os.path.join(os.path.dirname(os.path.realpath(__file__)), cmd)]
    command.extend(sys.argv[1:])
    sys.exit(subprocess.call(command))

if __name__ == "__main__":
     main()
