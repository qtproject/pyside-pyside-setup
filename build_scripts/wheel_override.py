#############################################################################
##
## Copyright (C) 2018 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of Qt for Python.
##
## $QT_BEGIN_LICENSE:LGPL$
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## GNU Lesser General Public License Usage
## Alternatively, this file may be used under the terms of the GNU Lesser
## General Public License version 3 as published by the Free Software
## Foundation and appearing in the file LICENSE.LGPL3 included in the
## packaging of this file. Please review the following information to
## ensure the GNU Lesser General Public License version 3 requirements
## will be met: https://www.gnu.org/licenses/lgpl-3.0.html.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 2.0 or (at your option) the GNU General
## Public license version 3 or any later version approved by the KDE Free
## Qt Foundation. The licenses are as published by the Free Software
## Foundation and appearing in the file LICENSE.GPL2 and LICENSE.GPL3
## included in the packaging of this file. Please review the following
## information to ensure the GNU General Public License requirements will
## be met: https://www.gnu.org/licenses/gpl-2.0.html and
## https://www.gnu.org/licenses/gpl-3.0.html.
##
## $QT_END_LICENSE$
##
#############################################################################


wheel_module_exists = False

import os
import sys
from .options import DistUtilsCommandMixin, OPTION
from setuptools._distutils import log as logger
from email.generator import Generator
from .wheel_utils import get_package_version, get_qt_version, macos_plat_name

try:

    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel
    from wheel.bdist_wheel import safer_name as _safer_name
    from wheel.bdist_wheel import get_abi_tag, get_platform
    from packaging import tags
    from wheel import __version__ as wheel_version

    wheel_module_exists = True
except Exception as e:
    _bdist_wheel, wheel_version = type, ""  # dummy to make class statement happy
    logger.warn(f"***** Exception while trying to prepare bdist_wheel override class: {e}. "
          "Skipping wheel overriding.")


def get_bdist_wheel_override():
    return PysideBuildWheel if wheel_module_exists else None


class PysideBuildWheel(_bdist_wheel, DistUtilsCommandMixin):

    user_options = (_bdist_wheel.user_options + DistUtilsCommandMixin.mixin_user_options
                    if wheel_module_exists else None)

    def __init__(self, *args, **kwargs):
        self.command_name = "bdist_wheel"
        self._package_version = None
        _bdist_wheel.__init__(self, *args, **kwargs)
        DistUtilsCommandMixin.__init__(self)

    def finalize_options(self):
        DistUtilsCommandMixin.mixin_finalize_options(self)
        if sys.platform == 'darwin':
            # Override the platform name to contain the correct
            # minimum deployment target.
            # This is used in the final wheel name.
            self.plat_name = macos_plat_name()

        # When limited API is requested, notify bdist_wheel to
        # create a properly named package.
        limited_api_enabled = OPTION["LIMITED_API"] == 'yes'
        if limited_api_enabled:
            self.py_limited_api = "cp36.cp37.cp38.cp39.cp310"

        self._package_version = get_package_version()

        _bdist_wheel.finalize_options(self)

    @property
    def wheel_dist_name(self):
        # Slightly modified version of wheel's wheel_dist_name
        # method, to add the Qt version as well.
        # Example:
        #   PySide6-5.6-5.6.4-cp27-cp27m-macosx_10_10_intel.whl
        # The PySide6 version is "5.6".
        # The Qt version built against is "5.6.4".
        wheel_version = f"{self._package_version}-{get_qt_version()}"
        components = (_safer_name(self.distribution.get_name()), wheel_version)
        if self.build_number:
            components += (self.build_number,)
        return '-'.join(components)

    # Modify the returned wheel tag tuple to use correct python version
    # info when cross-compiling. We use the python info extracted from
    # the shiboken python config test.
    # setuptools / wheel don't support cross compiling out of the box
    # at the moment. Relevant discussion at
    # https://discuss.python.org/t/towards-standardizing-cross-compiling/10357
    def get_cross_compiling_tag_tuple(self, tag_tuple):
        (old_impl, old_abi_tag, plat_name) = tag_tuple

        # Compute tag from the python version that the build command
        # queried.
        build_command = self.get_finalized_command('build')
        python_target_info = build_command.python_target_info['python_info']

        impl = 'no-py-ver-impl-available'
        abi = 'no-abi-tag-info-available'
        py_version = python_target_info['version'].split('.')
        py_version_major = py_version[0]
        py_version_minor = py_version[1]

        so_abi = python_target_info['so_abi']
        if so_abi and so_abi.startswith('cpython-'):
            interpreter_name = so_abi.split('-')[0]
            impl_name = tags.INTERPRETER_SHORT_NAMES.get(interpreter_name) or interpreter_name
            impl_ver = f"{py_version_major}{py_version_minor}"
            impl = impl_name + impl_ver
            abi = 'cp' + so_abi.split('-')[1]
        tag_tuple = (impl, abi, plat_name)
        return tag_tuple

    # Adjust wheel tag for limited api and cross compilation.
    @staticmethod
    def adjust_cross_compiled_many_linux_tag(old_tag):
        (old_impl, old_abi_tag, old_plat_name) = old_tag

        new_plat_name = old_plat_name

        # TODO: Detect glibc version instead. We're abusing the
        # manylinux2014 tag here, just like we did with manylinux1
        # for x86_64 builds.
        many_linux_prefix = 'manylinux2014'
        linux_prefix = "linux_"
        if old_plat_name.startswith(linux_prefix):
            # Extract the arch suffix like -armv7l or -aarch64
            plat_name_arch_suffix = \
                old_plat_name[old_plat_name.index(linux_prefix) + len(linux_prefix):]

            new_plat_name = f"{many_linux_prefix}_{plat_name_arch_suffix}"

        tag = (old_impl, old_abi_tag, new_plat_name)
        return tag

    # Adjust wheel tag for limited api and cross compilation.
    def adjust_tag_and_supported_tags(self, old_tag, supported_tags):
        tag = old_tag
        (old_impl, old_abi_tag, old_plat_name) = old_tag

        # Get new tag for cross builds.
        if self.is_cross_compile:
            tag = self.get_cross_compiling_tag_tuple(old_tag)

        # Get new tag for manylinux builds.
        # To allow uploading to pypi, we need the wheel name
        # to contain 'manylinux1'.
        # The wheel which will be uploaded to pypi will be
        # built on RHEL_8_2, so it doesn't completely qualify for
        # manylinux1 support, but it's the minimum requirement
        # for building Qt. We only enable this for x64 limited
        # api builds (which are the only ones uploaded to pypi).
        # TODO: Add actual distro detection, instead of
        # relying on limited_api option if possible.
        if (old_plat_name in ('linux-x86_64', 'linux_x86_64')
                and sys.maxsize > 2147483647
                and self.py_limited_api):
            tag = (old_impl, old_abi_tag, 'manylinux1_x86_64')

        # Set manylinux tag for cross-compiled builds when targeting
        # limited api.
        if self.is_cross_compile and self.py_limited_api:
            tag = self.adjust_cross_compiled_many_linux_tag(tag)

        # Reset the abi name and python versions supported by this wheel
        # when targeting limited API. This is the same code that's
        # in get_tag(), but done later after our own customizations.
        if self.py_limited_api and old_impl.startswith('cp3'):
            (_, _, adjusted_plat_name) = tag
            impl = self.py_limited_api
            abi_tag = 'abi3'
            tag = (impl, abi_tag, adjusted_plat_name)

        # Adjust abi name on Windows for limited api. It needs to be
        # 'none' instead of 'abi3' because pip does not yet support
        # the "abi3" tag on Windows, leading to a installation failure.
        if self.py_limited_api and old_impl.startswith('cp3') and sys.platform == 'win32':
            tag = (old_impl, 'none', old_plat_name)

        # If building for limited API or we created a new tag, add it
        # to the list of supported tags.
        if tag != old_tag or self.py_limited_api:
            supported_tags.append(tag)
        return tag

    # A slightly modified copy of get_tag from bdist_wheel.py, to allow
    # adjusting the returned tag without triggering an assert. Otherwise
    # we would have to rename wheels manually.
    # Copy is up-to-date since commit
    # 0acd203cd896afec7f715aa2ff5980a403459a3b in the wheel repo.
    def get_tag(self):
        # bdist sets self.plat_name if unset, we should only use it for purepy
        # wheels if the user supplied it.
        if self.plat_name_supplied:
            plat_name = self.plat_name
        elif self.root_is_pure:
            plat_name = 'any'
        else:
            # macosx contains system version in platform name so need special handle
            if self.plat_name and not self.plat_name.startswith("macosx"):
                plat_name = self.plat_name
            else:
                # on macosx always limit the platform name to comply with any
                # c-extension modules in bdist_dir, since the user can specify
                # a higher MACOSX_DEPLOYMENT_TARGET via tools like CMake

                # on other platforms, and on macosx if there are no c-extension
                # modules, use the default platform name.
                plat_name = get_platform(self.bdist_dir)

            if plat_name in ('linux-x86_64', 'linux_x86_64') and sys.maxsize == 2147483647:
                plat_name = 'linux_i686'

        plat_name = plat_name.lower().replace('-', '_').replace('.', '_')

        if self.root_is_pure:
            if self.universal:
                impl = 'py2.py3'
            else:
                impl = self.python_tag
            tag = (impl, 'none', plat_name)
        else:
            impl_name = tags.interpreter_name()
            impl_ver = tags.interpreter_version()
            impl = impl_name + impl_ver
            # We don't work on CPython 3.1, 3.0.
            if self.py_limited_api and (impl_name + impl_ver).startswith('cp3'):
                impl = self.py_limited_api
                abi_tag = 'abi3'
            else:
                abi_tag = str(get_abi_tag()).lower()
            tag = (impl, abi_tag, plat_name)
            # issue gh-374: allow overriding plat_name
            supported_tags = [(t.interpreter, t.abi, plat_name)
                              for t in tags.sys_tags()]
            # PySide's custom override.
            tag = self.adjust_tag_and_supported_tags(tag, supported_tags)
            assert tag in supported_tags, (f"would build wheel with unsupported tag {tag}")
        return tag

    # Copy of get_tag from bdist_wheel.py, to write a triplet Tag
    # only once for the limited_api case.
    def write_wheelfile(self, wheelfile_base, generator='bdist_wheel (' + wheel_version + ')'):
        from email.message import Message
        msg = Message()
        msg['Wheel-Version'] = '1.0'  # of the spec
        msg['Generator'] = generator
        msg['Root-Is-Purelib'] = str(self.root_is_pure).lower()
        if self.build_number is not None:
            msg['Build'] = self.build_number

        # Doesn't work for bdist_wininst
        impl_tag, abi_tag, plat_tag = self.get_tag()
        # To enable pypi upload we are adjusting the wheel name
        pypi_ready = True if OPTION["LIMITED_API"] else False

        def writeTag(impl):
            for abi in abi_tag.split('.'):
                for plat in plat_tag.split('.'):
                    msg['Tag'] = '-'.join((impl, abi, plat))
        if pypi_ready:
            writeTag(impl_tag)
        else:
            for impl in impl_tag.split('.'):
                writeTag(impl)

        wheelfile_path = os.path.join(wheelfile_base, 'WHEEL')
        logger.info('creating %s', wheelfile_path)
        with open(wheelfile_path, 'w') as f:
            Generator(f, maxheaderlen=0).flatten(msg)


if not wheel_module_exists:
    del PysideBuildWheel
