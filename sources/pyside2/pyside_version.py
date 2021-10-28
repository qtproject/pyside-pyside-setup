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

major_version = "5"
minor_version = "15"
patch_version = "7"

# For example: "a", "b", "rc"
# (which means "alpha", "beta", "release candidate").
# An empty string means the generated package will be an official release.
release_version_type = ""

# For example: "1", "2" (which means "beta1", "beta2", if type is "b").
pre_release_version = ""

if __name__ == '__main__':
    # Used by CMake.
    print('{0};{1};{2};{3};{4}'.format(major_version, minor_version, patch_version,
                                       release_version_type, pre_release_version))
