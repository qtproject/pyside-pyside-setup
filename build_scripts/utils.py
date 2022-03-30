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

import errno
import fnmatch
import glob
import itertools
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import urllib.request as urllib
from collections import defaultdict
from pathlib import Path

try:
    # Using the distutils implementation within setuptools
    from setuptools._distutils import log
    from setuptools._distutils.errors import DistutilsSetupError
except ModuleNotFoundError:
    # This is motivated by our CI using an old version of setuptools
    # so then the coin_build_instructions.py script is executed, and
    # import from this file, it was failing.
    from distutils import log
    from distutils.errors import DistutilsSetupError

try:
    WindowsError
except NameError:
    WindowsError = None


def is_64bit():
    return sys.maxsize > 2147483647


def filter_match(name, patterns):
    for pattern in patterns:
        if pattern is None:
            continue
        if fnmatch.fnmatch(name, pattern):
            return True
    return False


def update_env_path(newpaths):
    paths = os.environ['PATH'].lower().split(os.pathsep)
    for path in newpaths:
        if not path.lower() in paths:
            log.info(f"Inserting path '{path}' to environment")
            paths.insert(0, path)
            os.environ['PATH'] = f"{path}{os.pathsep}{os.environ['PATH']}"


def get_numpy_location():
    for p in sys.path:
        if 'site-' in p:
            numpy = Path(p).resolve() / 'numpy'
            if numpy.is_dir():
                return os.fspath(numpy / 'core' / 'include')
    return None


def winsdk_setenv(platform_arch, build_type):
    from setuptools._distutils import msvc9compiler as msvc9

    sdk_version_map = {
        "v6.0a": 9.0,
        "v6.1": 9.0,
        "v7.0": 9.0,
        "v7.0a": 10.0,
        "v7.1": 10.0
    }

    log.info(f"Searching Windows SDK with MSVC compiler version {msvc9.VERSION}")
    setenv_paths = []
    for base in msvc9.HKEYS:
        sdk_versions = msvc9.Reg.read_keys(base, msvc9.WINSDK_BASE)
        if sdk_versions:
            for sdk_version in sdk_versions:
                installationfolder = msvc9.Reg.get_value(f"{msvc9.WINSDK_BASE}\\{sdk_version}",
                                                         "installationfolder")
                # productversion = msvc9.Reg.get_value(
                #                      "{}\\{}".format(msvc9.WINSDK_BASE, sdk_version),
                #                      "productversion")
                setenv_path = os.path.join(installationfolder, os.path.join('bin', 'SetEnv.cmd'))
                if not os.path.exists(setenv_path):
                    continue
                if sdk_version not in sdk_version_map:
                    continue
                if sdk_version_map[sdk_version] != msvc9.VERSION:
                    continue
                setenv_paths.append(setenv_path)
    if len(setenv_paths) == 0:
        raise DistutilsSetupError("Failed to find the Windows SDK with MSVC compiler "
                                  f"version {msvc9.VERSION}")
    for setenv_path in setenv_paths:
        log.info(f"Found {setenv_path}")

    # Get SDK env (use latest SDK version installed on system)
    setenv_path = setenv_paths[-1]
    log.info(f"Using {setenv_path} ")
    build_arch = "/x86" if platform_arch.startswith("32") else "/x64"
    build_type = "/Debug" if build_type.lower() == "debug" else "/Release"
    setenv_cmd = [setenv_path, build_arch, build_type]
    setenv_env = get_environment_from_batch_command(setenv_cmd)
    _setenv_paths = [setenv_env[k] for k in setenv_env if k.upper() == 'PATH']
    setenv_env_paths = os.pathsep.join(_setenv_paths).split(os.pathsep)
    setenv_env_without_paths = dict([(k, setenv_env[k]) for k in setenv_env if k.upper() != 'PATH'])

    # Extend os.environ with SDK env
    log.info("Initializing Windows SDK env...")
    update_env_path(setenv_env_paths)
    for k in sorted(setenv_env_without_paths):
        v = setenv_env_without_paths[k]
        log.info(f"Inserting '{k} = {v}' to environment")
        os.environ[k] = v
    log.info("Done initializing Windows SDK env")


def find_vcdir(version):
    """
    This is the customized version of
    setuptools._distutils.msvc9compiler.find_vcvarsall method
    """
    from setuptools._distutils import msvc9compiler as msvc9
    vsbase = msvc9.VS_BASE % version
    try:
        productdir = msvc9.Reg.get_value(rf"{vsbase}\Setup\VC", "productdir")
    except KeyError:
        productdir = None

    # trying Express edition
    if productdir is None:
        try:
            hasattr(msvc9, VSEXPRESS_BASE)
        except AttributeError:
            pass
        else:
            vsbase = VSEXPRESS_BASE % version
            try:
                productdir = msvc9.Reg.get_value(rf"{vsbase}\Setup\VC", "productdir")
            except KeyError:
                productdir = None
                log.debug("Unable to find productdir in registry")

    if not productdir or not os.path.isdir(productdir):
        toolskey = f"VS{version:0.0f}0COMNTOOLS"
        toolsdir = os.environ.get(toolskey, None)

        if toolsdir and os.path.isdir(toolsdir):
            productdir = os.path.join(toolsdir, os.pardir, os.pardir, "VC")
            productdir = os.path.abspath(productdir)
            if not os.path.isdir(productdir):
                log.debug(f"{productdir} is not a valid directory")
                return None
        else:
            log.debug(f"Env var {toolskey} is not set or invalid")
    if not productdir:
        log.debug("No productdir found")
        return None
    return productdir


def init_msvc_env(platform_arch, build_type):
    from setuptools._distutils import msvc9compiler as msvc9

    log.info(f"Searching MSVC compiler version {msvc9.VERSION}")
    vcdir_path = find_vcdir(msvc9.VERSION)
    if not vcdir_path:
        raise DistutilsSetupError(f"Failed to find the MSVC compiler version {msvc9.VERSION} on "
                                  "your system.")
    else:
        log.info(f"Found {vcdir_path}")

    log.info(f"Searching MSVC compiler {msvc9.VERSION} environment init script")
    if platform_arch.startswith("32"):
        vcvars_path = os.path.join(vcdir_path, "bin", "vcvars32.bat")
    else:
        vcvars_path = os.path.join(vcdir_path, "bin", "vcvars64.bat")
        if not os.path.exists(vcvars_path):
            vcvars_path = os.path.join(vcdir_path, "bin", "amd64", "vcvars64.bat")
            if not os.path.exists(vcvars_path):
                vcvars_path = os.path.join(vcdir_path, "bin", "amd64", "vcvarsamd64.bat")

    if not os.path.exists(vcvars_path):
        # MSVC init script not found, try to find and init Windows SDK env
        log.error("Failed to find the MSVC compiler environment init script "
                  "(vcvars.bat) on your system.")
        winsdk_setenv(platform_arch, build_type)
        return
    else:
        log.info(f"Found {vcvars_path}")

    # Get MSVC env
    log.info(f"Using MSVC {msvc9.VERSION} in {vcvars_path}")
    msvc_arch = "x86" if platform_arch.startswith("32") else "amd64"
    log.info(f"Getting MSVC env for {msvc_arch} architecture")
    vcvars_cmd = [vcvars_path, msvc_arch]
    msvc_env = get_environment_from_batch_command(vcvars_cmd)
    _msvc_paths = [msvc_env[k] for k in msvc_env if k.upper() == 'PATH']
    msvc_env_paths = os.pathsep.join(_msvc_paths).split(os.pathsep)
    msvc_env_without_paths = dict([(k, msvc_env[k]) for k in msvc_env if k.upper() != 'PATH'])

    # Extend os.environ with MSVC env
    log.info("Initializing MSVC env...")
    update_env_path(msvc_env_paths)
    for k in sorted(msvc_env_without_paths):
        v = msvc_env_without_paths[k]
        log.info(f"Inserting '{k} = {v}' to environment")
        os.environ[k] = v
    log.info("Done initializing MSVC env")


def platform_cmake_options(as_tuple_list=False):
    result = []
    if sys.platform == 'win32':
        # Prevent cmake from auto-detecting clang if it is in path.
        if as_tuple_list:
            result.append(("CMAKE_C_COMPILER", "cl.exe"))
            result.append(("CMAKE_CXX_COMPILER", "cl.exe"))
        else:
            result.append("-DCMAKE_C_COMPILER=cl.exe")
            result.append("-DCMAKE_CXX_COMPILER=cl.exe")
    return result


def copyfile(src, dst, force=True, vars=None, force_copy_symlink=False,
             make_writable_by_owner=False):
    if vars is not None:
        src = src.format(**vars)
        dst = dst.format(**vars)

    if not os.path.exists(src) and not force:
        log.info(f"**Skipping copy file\n  {src} to\n  {dst}\n  Source does not exist")
        return

    if not os.path.islink(src) or force_copy_symlink:
        if os.path.isfile(dst):
            src_stat = os.stat(src)
            dst_stat = os.stat(dst)
            if (src_stat.st_size == dst_stat.st_size
                    and src_stat.st_mtime <= dst_stat.st_mtime):
                log.info(f"{dst} is up to date.")
                return dst

        log.info(f"Copying file\n  {src} to\n  {dst}.")
        shutil.copy2(src, dst)
        if make_writable_by_owner:
            make_file_writable_by_owner(dst)

        return dst

    link_target_path = os.path.realpath(src)
    if os.path.dirname(link_target_path) == os.path.dirname(src):
        link_target = os.path.basename(link_target_path)
        link_name = os.path.basename(src)
        current_directory = os.getcwd()
        try:
            target_dir = dst if os.path.isdir(dst) else os.path.dirname(dst)
            os.chdir(target_dir)
            if os.path.exists(link_name):
                if (os.path.islink(link_name)
                        and os.readlink(link_name) == link_target):
                    log.info(f"Symlink already exists\n  {link_name} ->\n  {link_target}")
                    return dst
                os.remove(link_name)
            log.info(f"Symlinking\n  {link_name} ->\n  {link_target} in\n  {target_dir}")
            os.symlink(link_target, link_name)
        except OSError:
            log.error(f"Error creating symlink\n  {link_name} ->\n  {link_target}")
        finally:
            os.chdir(current_directory)
    else:
        log.error(f"{src} -> {link_target_path}: Can only create symlinks within the same "
                  "directory")

    return dst


def makefile(dst, content=None, vars=None):
    if vars is not None:
        if content is not None:
            content = content.format(**vars)
        dst = dst.format(**vars)

    log.info(f"Making file {dst}.")

    dstdir = os.path.dirname(dst)
    if not os.path.exists(dstdir):
        os.makedirs(dstdir)

    with open(dst, "wt") as f:
        if content is not None:
            f.write(content)


def copydir(src, dst, filter=None, ignore=None, force=True, recursive=True, vars=None,
            dir_filter_function=None, file_filter_function=None, force_copy_symlinks=False):

    if vars is not None:
        src = src.format(**vars)
        dst = dst.format(**vars)
        if filter is not None:
            for i in range(len(filter)):
                filter[i] = filter[i].format(**vars)
        if ignore is not None:
            for i in range(len(ignore)):
                ignore[i] = ignore[i].format(**vars)

    if not os.path.exists(src) and not force:
        log.info(f"**Skipping copy tree\n  {src} to\n  {dst}\n  Source does not exist. "
                 f"filter={filter}. ignore={ignore}.")
        return []

    log.info(f"Copying tree\n  {src} to\n  {dst}. filter={filter}. ignore={ignore}.")

    names = os.listdir(src)

    results = []
    copy_errors = []
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if os.path.isdir(srcname):
                if (dir_filter_function and not dir_filter_function(name, src, srcname)):
                    continue
                if recursive:
                    results.extend(copydir(srcname, dstname, filter, ignore, force, recursive,
                                           vars, dir_filter_function, file_filter_function,
                                           force_copy_symlinks))
            else:
                if ((file_filter_function is not None and not file_filter_function(name, srcname))
                        or (filter is not None and not filter_match(name, filter))
                        or (ignore is not None and filter_match(name, ignore))):
                    continue
                if not os.path.exists(dst):
                    os.makedirs(dst)
                results.append(copyfile(srcname, dstname, True, vars, force_copy_symlinks))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except shutil.Error as err:
            copy_errors.extend(err.args[0])
        except EnvironmentError as why:
            copy_errors.append((srcname, dstname, str(why)))
    try:
        if os.path.exists(dst):
            shutil.copystat(src, dst)
    except OSError as why:
        if WindowsError is not None and isinstance(why, WindowsError):
            # Copying file access times may fail on Windows
            pass
        else:
            copy_errors.extend((src, dst, str(why)))
    if copy_errors:
        raise EnvironmentError(copy_errors)
    return results


def make_file_writable_by_owner(path):
    current_permissions = stat.S_IMODE(os.lstat(path).st_mode)
    os.chmod(path, current_permissions | stat.S_IWUSR)


def rmtree(dirname, ignore=False):
    def handle_remove_readonly(func, path, exc):
        excvalue = exc[1]
        if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
            os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
            func(path)
        else:
            raise IOError
    shutil.rmtree(dirname, ignore_errors=ignore, onerror=handle_remove_readonly)


def run_process_output(args, initial_env=None):
    if initial_env is None:
        initial_env = os.environ
    result = []
    with subprocess.Popen(args, env=initial_env, universal_newlines=1,
                          stdout=subprocess.PIPE) as p:
        for raw_line in p.stdout.readlines():
            result.append(raw_line.rstrip())
        p.stdout.close()
    return result


def run_process(args, initial_env=None):
    """
    Run process until completion and return the process exit code.
    No output is captured.
    """
    command = " ".join([(" " in x and f'"{x}"' or x) for x in args])
    log.info(f"In directory {os.getcwd()}:\n\tRunning command:  {command}")

    if initial_env is None:
        initial_env = os.environ

    kwargs = {}
    kwargs['env'] = initial_env

    exit_code = subprocess.call(args, **kwargs)
    return exit_code


def get_environment_from_batch_command(env_cmd, initial=None):
    """
    Take a command (either a single command or list of arguments)
    and return the environment created after running that command.
    Note that if the command must be a batch file or .cmd file, or the
    changes to the environment will not be captured.

    If initial is supplied, it is used as the initial environment passed
    to the child process.
    """

    def validate_pair(ob):
        if len(ob) != 2:
            log.error(f"Unexpected result: {ob}")
            return False
        return True

    def consume(iter):
        try:
            while True:
                next(iter)
        except StopIteration:
            pass

    if not isinstance(env_cmd, (list, tuple)):
        env_cmd = [env_cmd]
    # construct the command that will alter the environment
    env_cmd = subprocess.list2cmdline(env_cmd)
    # create a tag so we can tell in the output when the proc is done
    tag = 'Done running command'
    # construct a cmd.exe command to do accomplish this
    cmd = f'cmd.exe /E:ON /V:ON /s /c "{env_cmd} && echo "{tag}" && set"'
    # launch the process
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=initial)
    # parse the output sent to stdout
    lines = proc.stdout
    # make sure the lines are strings
    lines = map(lambda s: s.decode(), lines)
    # consume whatever output occurs until the tag is reached
    consume(itertools.takewhile(lambda l: tag not in l, lines))
    # define a way to handle each KEY=VALUE line
    # parse key/values into pairs
    pairs = map(lambda l: l.rstrip().split('=', 1), lines)
    # make sure the pairs are valid
    valid_pairs = filter(validate_pair, pairs)
    # construct a dictionary of the pairs
    result = dict(valid_pairs)
    # let the process finish
    proc.communicate()
    return result


def back_tick(cmd, ret_err=False):
    """
    Run command `cmd`, return stdout, or stdout, stderr,
    return_code if `ret_err` is True.

    Parameters
    ----------
    cmd : str
        command to execute
    ret_err : bool, optional
        If True, return stderr and return_code in addition to stdout.
        If False, just return stdout

    Returns
    -------
    out : str or tuple
        If `ret_err` is False, return stripped string containing stdout from
        `cmd`.
        If `ret_err` is True, return tuple of (stdout, stderr, return_code)
        where ``stdout`` is the stripped stdout, and ``stderr`` is the stripped
        stderr, and ``return_code`` is the process exit code.

    Raises
    ------
    Raises RuntimeError if command returns non-zero exit code when ret_err
    isn't set.
    """
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = proc.communicate()
    if not isinstance(out, str):
        # python 3
        out = out.decode()
        err = err.decode()
    retcode = proc.returncode
    if retcode is None and not ret_err:
        proc.terminate()
        raise RuntimeError(f"{cmd} process did not terminate")
    if retcode != 0 and not ret_err:
        raise RuntimeError(f"{cmd} process returned code {retcode}\n*** {err}")
    out = out.strip()
    if not ret_err:
        return out
    return out, err.strip(), retcode


MACOS_OUTNAME_RE = re.compile(r'\(compatibility version [\d.]+, current version [\d.]+\)')


def macos_get_install_names(libpath):
    """
    Get macOS library install names from library `libpath` using ``otool``

    Parameters
    ----------
    libpath : str
        path to library

    Returns
    -------
    install_names : list of str
        install names in library `libpath`
    """
    out = back_tick(f"otool -L {libpath}")
    libs = [line for line in out.split('\n')][1:]
    return [MACOS_OUTNAME_RE.sub('', lib).strip() for lib in libs]


MACOS_RPATH_RE = re.compile(r"path (.+) \(offset \d+\)")


def macos_get_rpaths(libpath):
    """ Get rpath load commands from library `libpath` using ``otool``

    Parameters
    ----------
    libpath : str
        path to library

    Returns
    -------
    rpaths : list of str
        rpath values stored in ``libpath``

    Notes
    -----
    See ``man dyld`` for more information on rpaths in libraries
    """
    lines = back_tick(f"otool -l {libpath}").split('\n')
    ctr = 0
    rpaths = []
    while ctr < len(lines):
        line = lines[ctr].strip()
        if line != 'cmd LC_RPATH':
            ctr += 1
            continue
        assert lines[ctr + 1].strip().startswith('cmdsize')
        rpath_line = lines[ctr + 2].strip()
        match = MACOS_RPATH_RE.match(rpath_line)
        if match is None:
            raise RuntimeError(f"Unexpected path line: {rpath_line}")
        rpaths.append(match.groups()[0])
        ctr += 3
    return rpaths


def macos_add_rpath(rpath, library_path):
    back_tick(f"install_name_tool -add_rpath {rpath} {library_path}")


def macos_fix_rpaths_for_library(library_path, qt_lib_dir):
    """ Adds required rpath load commands to given library.

    This is a necessary post-installation step, to allow loading PySide
    modules without setting DYLD_LIBRARY_PATH or DYLD_FRAMEWORK_PATH.
    The CMake rpath commands which are added at build time are used only
    for testing (make check), and they are stripped once the equivalent
    of make install is executed (except for shiboken, which currently
    uses CMAKE_INSTALL_RPATH_USE_LINK_PATH, which might be necessary to
    remove in the future).

    Parameters
    ----------
    library_path : str
        path to library for which to set rpaths.
    qt_lib_dir : str
        rpath to installed Qt lib directory.
    """

    install_names = macos_get_install_names(library_path)
    existing_rpath_commands = macos_get_rpaths(library_path)

    needs_loader_path = False
    for install_name in install_names:
        # Absolute path, skip it.
        if install_name[0] == '/':
            continue

        # If there are dynamic library install names that contain
        # @rpath tokens, we will provide an rpath load command with the
        # value of "@loader_path". This will allow loading dependent
        # libraries from within the same directory as 'library_path'.
        if install_name[0] == '@':
            needs_loader_path = True
            break

    if needs_loader_path and "@loader_path" not in existing_rpath_commands:
        macos_add_rpath("@loader_path", library_path)

    # If the library depends on a Qt library, add an rpath load comment
    # pointing to the Qt lib directory.
    macos_add_qt_rpath(library_path, qt_lib_dir, existing_rpath_commands, install_names)


def macos_add_qt_rpath(library_path, qt_lib_dir, existing_rpath_commands=[],
                       library_dependencies=[]):
    """
    Adds an rpath load command to the Qt lib directory if necessary

    Checks if library pointed to by 'library_path' has Qt dependencies,
    and adds an rpath load command that points to the Qt lib directory
    (qt_lib_dir).
    """
    if not existing_rpath_commands:
        existing_rpath_commands = macos_get_rpaths(library_path)

    # Return early if qt rpath is already present.
    if qt_lib_dir in existing_rpath_commands:
        return

    # Check if any library dependencies are Qt libraries (hacky).
    if not library_dependencies:
        library_dependencies = macos_get_install_names(library_path)

    needs_qt_rpath = False
    for library in library_dependencies:
        if 'Qt' in library:
            needs_qt_rpath = True
            break

    if needs_qt_rpath:
        macos_add_rpath(qt_lib_dir, library_path)


# Find an executable specified by a glob pattern ('foo*') in the OS path
def find_glob_in_path(pattern):
    result = []
    if sys.platform == 'win32':
        pattern += '.exe'

    for path in os.environ.get('PATH', '').split(os.pathsep):
        for match in glob.glob(os.path.join(path, pattern)):
            result.append(match)
    return result


# Expand the __ARCH_ place holder in the CLANG environment variables
def expand_clang_variables(target_arch):
    for var in 'LLVM_INSTALL_DIR', 'CLANG_INSTALL_DIR':
        value = os.environ.get(var)
        if value and '_ARCH_' in value:
            value = value.replace('_ARCH_', target_arch)
            os.environ[var] = value
            print(f"{var} = {value}")


# Add Clang to path for Windows for the shiboken ApiExtractor tests.
# Revisit once Clang is bundled with Qt.
def detect_clang():
    source = 'LLVM_INSTALL_DIR'
    clang_dir = os.environ.get(source, None)
    if not clang_dir:
        source = 'CLANG_INSTALL_DIR'
        clang_dir = os.environ.get(source, None)
        if not clang_dir:
            raise OSError("clang not found")
    return (clang_dir, source)


_7z_binary = None


def download_and_extract_7z(fileurl, target):
    """ Downloads 7z file from fileurl and extract to target  """
    info = ""
    localfile = None
    for i in range(1, 10):
        try:
            log.info(f"Downloading fileUrl {fileurl}, attempt #{i}")
            localfile, info = urllib.urlretrieve(fileurl)
            break
        except urllib.URLError:
            pass
    if not localfile:
        log.error(f"Error downloading {fileurl} : {info}")
        raise RuntimeError(f" Error downloading {fileurl}")

    try:
        global _7z_binary
        outputDir = f"-o{target}"
        if not _7z_binary:
            if sys.platform == "win32":
                candidate = "c:\\Program Files\\7-Zip\\7z.exe"
                if os.path.exists(candidate):
                    _7z_binary = candidate
            if not _7z_binary:
                _7z_binary = '7z'
        log.info(f"calling {_7z_binary} x {localfile} {outputDir}")
        subprocess.call([_7z_binary, "x", "-y", localfile, outputDir])
    except (subprocess.CalledProcessError, OSError):
        raise RuntimeError(f"Error extracting {localfile}")


def split_and_strip(sinput):
    lines = [s.strip() for s in sinput.splitlines()]
    return lines


def ldd_get_dependencies(executable_path):
    """
    Returns a dictionary of dependencies that `executable_path`
    depends on.

    The keys are library names and the values are the library paths.

    """
    output = ldd(executable_path)
    lines = split_and_strip(output)
    pattern = re.compile(r"\s*(.*?)\s+=>\s+(.*?)\s+\(.*\)")
    dependencies = {}
    for line in lines:
        match = pattern.search(line)
        if match:
            dependencies[match.group(1)] = match.group(2)
    return dependencies


def ldd_get_paths_for_dependencies(dependencies_regex, executable_path=None, dependencies=None):
    """
    Returns file paths to shared library dependencies that match given
    `dependencies_regex` against given `executable_path`.

    The function retrieves the list of shared library dependencies using
    ld.so for the given `executable_path` in order to search for
    libraries that match the `dependencies_regex`, and then returns a
    list of absolute paths of the matching libraries.

    If no matching library is found in the list of dependencies,
    an empty list is returned.
    """

    if not dependencies and not executable_path:
        return None

    if not dependencies:
        dependencies = ldd_get_dependencies(executable_path)

    pattern = re.compile(dependencies_regex)

    paths = []
    for key in dependencies:
        match = pattern.search(key)
        if match:
            paths.append(dependencies[key])

    return paths


def _ldd_ldd(executable_path):
    """Helper for ldd():
       Returns ldd output of shared library dependencies for given
       `executable_path`.

    Parameters
    ----------
    executable_path : str
        path to executable or shared library.

    Returns
    -------
    output : str
        the raw output retrieved from the dynamic linker.
    """

    output = ''
    error = ''
    try:
        output_lines = run_process_output(['ldd', executable_path])
        output = '\n'.join(output_lines)
    except Exception as e:
        error = str(e)
    if not output:
        message = (f"ldd failed to query for dependent shared libraries of {executable_path}: "
                   f"{error}")
        raise RuntimeError(message)
    return output


def _ldd_ldso(executable_path):
    """
    Helper for ldd():
    Returns ld.so output of shared library dependencies for given
    `executable_path`.

    This is a partial port of /usr/bin/ldd from bash to Python for
    systems that do not have ldd.
    The dependency list is retrieved by setting the
    LD_TRACE_LOADED_OBJECTS=1 environment variable, and executing the
    given path via the dynamic loader ld.so.

    Only works on Linux.
    This is because ldd (on Ubuntu) is shipped in the libc-bin package
    that, which might have a
    minuscule percentage of not being installed.

    Parameters
    ----------
    executable_path : str
        path to executable or shared library.

    Returns
    -------
    output : str
        the raw output retrieved from the dynamic linker.
    """

    chosen_rtld = None
    # List of ld's considered by ldd on Ubuntu (here's hoping it's the
    # same on all distros).
    rtld_list = ["/lib/ld-linux.so.2", "/lib64/ld-linux-x86-64.so.2", "/libx32/ld-linux-x32.so.2"]

    # Choose appropriate runtime dynamic linker.
    for rtld in rtld_list:
        if os.path.isfile(rtld) and os.access(rtld, os.X_OK):
            (_, _, code) = back_tick(rtld, True)
            # Code 127 is returned by ld.so when called without any
            # arguments (some kind of sanity check I guess).
            if code == 127:
                (_, _, code) = back_tick(f"{rtld} --verify {executable_path}", True)
                # Codes 0 and 2 mean given executable_path can be
                # understood by ld.so.
                if code in [0, 2]:
                    chosen_rtld = rtld
                    break

    if not chosen_rtld:
        raise RuntimeError("Could not find appropriate ld.so to query for dependencies.")

    # Query for shared library dependencies.
    rtld_env = "LD_TRACE_LOADED_OBJECTS=1"
    rtld_cmd = f"{rtld_env} {chosen_rtld} {executable_path}"
    (out, _, return_code) = back_tick(rtld_cmd, True)
    if return_code == 0:
        return out
    else:
        raise RuntimeError("ld.so failed to query for dependent shared "
                           f"libraries of {executable_path}")


def ldd(executable_path):
    """
    Returns ldd output of shared library dependencies for given `executable_path`,
    using either ldd or ld.so depending on availability.

    Parameters
    ----------
    executable_path : str
        path to executable or shared library.

    Returns
    -------
    output : str
        the raw output retrieved from the dynamic linker.
    """
    result = ''
    try:
        result = _ldd_ldd(executable_path)
    except RuntimeError as e:
        message = f"ldd: Falling back to ld.so ({str(e)})"
        log.warn(message)
    if not result:
        result = _ldd_ldso(executable_path)
    return result


def find_files_using_glob(path, pattern):
    """ Returns list of files that matched glob `pattern` in `path`. """
    final_pattern = os.path.join(path, pattern)
    maybe_files = glob.glob(final_pattern)
    return maybe_files


def find_qt_core_library_glob(lib_dir):
    """ Returns path to the QtCore library found in `lib_dir`. """
    maybe_file = find_files_using_glob(lib_dir, "libQt6Core.so.?")
    if len(maybe_file) == 1:
        return maybe_file[0]
    return None


# @TODO: Possibly fix ICU library copying on macOS and Windows.
# This would require to implement the equivalent of the custom written
# ldd for the specified platforms.
# This has less priority because ICU libs are not used in the default
# Qt configuration build.
def copy_icu_libs(patchelf, destination_lib_dir):
    """
    Copy ICU libraries that QtCore depends on,
    to given `destination_lib_dir`.
    """
    qt_core_library_path = find_qt_core_library_glob(destination_lib_dir)

    if not qt_core_library_path or not os.path.exists(qt_core_library_path):
        raise RuntimeError(f"QtCore library does not exist at path: {qt_core_library_path}. "
                           "Failed to copy ICU libraries.")

    dependencies = ldd_get_dependencies(qt_core_library_path)

    icu_regex = r"^libicu.+"
    icu_compiled_pattern = re.compile(icu_regex)
    icu_required = False
    for dependency in dependencies:
        match = icu_compiled_pattern.search(dependency)
        if match:
            icu_required = True
            break

    if icu_required:
        paths = ldd_get_paths_for_dependencies(icu_regex, dependencies=dependencies)
        if not paths:
            raise RuntimeError("Failed to find the necessary ICU libraries required by QtCore.")
        log.info('Copying the detected ICU libraries required by QtCore.')

        if not os.path.exists(destination_lib_dir):
            os.makedirs(destination_lib_dir)

        for path in paths:
            basename = os.path.basename(path)
            destination = os.path.join(destination_lib_dir, basename)
            copyfile(path, destination, force_copy_symlink=True)
            # Patch the ICU libraries to contain the $ORIGIN rpath
            # value, so that only the local package libraries are used.
            linux_set_rpaths(patchelf, destination, '$ORIGIN')

        # Patch the QtCore library to find the copied over ICU libraries
        # (if necessary).
        log.info("Checking if QtCore library needs a new rpath to make it work with ICU libs.")
        linux_prepend_rpath(patchelf, qt_core_library_path, '$ORIGIN')


def linux_run_read_elf(executable_path):
    cmd = f"readelf -d {executable_path}"
    (out, err, code) = back_tick(cmd, True)
    if code != 0:
        raise RuntimeError(f"Running `readelf -d {executable_path}` failed with error "
                           f"output:\n {err}. ")
    lines = split_and_strip(out)
    return lines


def linux_set_rpaths(patchelf, executable_path, rpath_string):
    """ Patches the `executable_path` with a new rpath string. """

    cmd = [patchelf, '--set-rpath', rpath_string, executable_path]

    if run_process(cmd) != 0:
        raise RuntimeError(f"Error patching rpath in {executable_path}")


def linux_prepend_rpath(patchelf, executable_path, new_path):
    """ Prepends a path to the rpaths of the executable unless it has ORIGIN. """
    rpaths = linux_get_rpaths(executable_path)
    if not rpaths or not rpaths_has_origin(rpaths):
        rpaths.insert(0, new_path)
        new_rpaths_string = ":".join(rpaths)
        linux_set_rpaths(patchelf, executable_path, new_rpaths_string)


def linux_patch_executable(patchelf, executable_path):
    """ Patch an executable to run with the Qt libraries. """
    linux_prepend_rpath(patchelf, executable_path, '$ORIGIN/../lib')


def linux_get_dependent_libraries(executable_path):
    """
    Returns a list of libraries that executable_path depends on.
    """

    lines = linux_run_read_elf(executable_path)
    pattern = re.compile(r"^.+?\(NEEDED\).+?\[(.+?)\]$")

    library_lines = []
    for line in lines:
        match = pattern.search(line)
        if match:
            library_line = match.group(1)
            library_lines.append(library_line)

    return library_lines


def linux_get_rpaths(executable_path):
    """
    Returns a list of run path values embedded in the executable or just
    an empty list.
    """

    lines = linux_run_read_elf(executable_path)
    pattern = re.compile(r"^.+?\(RUNPATH\).+?\[(.+?)\]$")

    rpath_line = None
    for line in lines:
        match = pattern.search(line)
        if match:
            rpath_line = match.group(1)
            break

    rpaths = []

    if rpath_line:
        rpaths = rpath_line.split(':')

    return rpaths


def rpaths_has_origin(rpaths):
    """
    Return True if the specified list of rpaths has an "$ORIGIN" value
    (aka current dir).
    """
    if not rpaths:
        return False

    pattern = re.compile(r"^\$ORIGIN(/)?$")
    for rpath in rpaths:
        match = pattern.search(rpath)
        if match:
            return True
    return False


def linux_needs_qt_rpath(executable_path):
    """
    Returns true if library_path depends on Qt libraries.
    """

    dependencies = linux_get_dependent_libraries(executable_path)

    # Check if any library dependencies are Qt libraries (hacky).
    needs_qt_rpath = False
    for dep in dependencies:
        if 'Qt' in dep:
            needs_qt_rpath = True
            break
    return needs_qt_rpath


def linux_fix_rpaths_for_library(patchelf, executable_path, qt_rpath, override=False):
    """
    Adds or overrides required rpaths in given executable / library.
    """
    rpaths = ['$ORIGIN/']
    existing_rpaths = []
    if not override:
        existing_rpaths = linux_get_rpaths(executable_path)
        rpaths.extend(existing_rpaths)

    if linux_needs_qt_rpath(executable_path) and qt_rpath not in existing_rpaths:
        rpaths.append(qt_rpath)

    rpaths_string = ':'.join(rpaths)
    linux_set_rpaths(patchelf, executable_path, rpaths_string)


def memoize(function):
    """
    Decorator to wrap a function with a memoizing callable.
    It returns cached values when the wrapped function is called with
    the same arguments.
    """
    memo = {}

    def wrapper(*args):
        if args in memo:
            return memo[args]
        else:
            rv = function(*args)
            memo[args] = rv
            return rv
    return wrapper


def get_python_dict(python_script_path):
    try:
        with open(python_script_path) as f:
            python_dict = {}
            code = compile(f.read(), python_script_path, 'exec')
            exec(code, {}, python_dict)
            return python_dict
    except IOError as e:
        print(f"get_python_dict: Couldn't get dict from python "
              f"file: {python_script_path}. {e}")
        raise


def install_pip_package_from_url_specifier(env_pip, url, upgrade=True):
    args = [env_pip, "install", url]
    if upgrade:
        args.append("--upgrade")
    args.append(url)
    run_instruction(args, f"Failed to install {url}")


def install_pip_dependencies(env_pip, packages, upgrade=True):
    for p in packages:
        args = [env_pip, "install"]
        if upgrade:
            args.append("--upgrade")
        args.append(p)
        run_instruction(args, f"Failed to install {p}")


def get_qtci_virtualEnv(python_ver, host, hostArch, targetArch):
    _pExe = "python"
    _env = f"env{python_ver}"
    env_python = f"{_env}/bin/python"
    env_pip = f"{_env}/bin/pip"

    if host == "Windows":
        log.info("New virtualenv to build {targetArch} in {hostArch} host")
        _pExe = "python.exe"
        # With windows we are creating building 32-bit target in 64-bit host
        if hostArch == "X86_64" and targetArch == "X86":
            if python_ver.startswith("3"):
                var = f"PYTHON{python_ver}-32_PATH"
                log.info(f"Try to find python from {var} env variable")
                _path = os.getenv(var, "")
                _pExe = os.path.join(_path, "python.exe")
                if not os.path.isfile(_pExe):
                    log.warn(f"Can't find python.exe from {_pExe}, using default python3")
                    _pExe = os.path.join(os.getenv("PYTHON3_32_PATH"), "python.exe")
            else:
                _pExe = os.path.join(os.getenv("PYTHON2_32_PATH"), "python.exe")
        else:
            if python_ver.startswith("3"):
                var = f"PYTHON{python_ver}-64_PATH"
                log.info(f"Try to find python from {var} env variable")
                _path = os.getenv(var, "")
                _pExe = os.path.join(_path, "python.exe")
                if not os.path.isfile(_pExe):
                    log.warn(f"Can't find python.exe from {_pExe}, using default python3")
                    _pExe = os.path.join(os.getenv("PYTHON3_PATH"), "python.exe")
        env_python = f"{_env}\\Scripts\\python.exe"
        env_pip = f"{_env}\\Scripts\\pip.exe"
    else:
        _pExe = f"python{python_ver}"
        try:
            run_instruction([_pExe, "--version"], f"Failed to guess python version {_pExe}")
        except Exception as e:
            print(f"Exception {type(e).__name__}: {e}")
            _pExe = "python3"
    return(_pExe, _env, env_pip, env_python)


def run_instruction(instruction, error, initial_env=None):
    if initial_env is None:
        initial_env = os.environ
    log.info(f"Running Coin instruction: {' '.join(str(e) for e in instruction)}")
    result = subprocess.call(instruction, env=initial_env)
    if result != 0:
        log.error(f"ERROR : {error}")
        exit(result)


def acceptCITestConfiguration(hostOS, hostOSVer, targetArch, compiler):
    # Disable unsupported CI configs for now
    # NOTE: String must match with QT CI's storagestruct thrift
    if (hostOSVer in ["WinRT_10", "WebAssembly", "Ubuntu_18_04", "Android_ANY"]
            or hostOSVer.startswith("SLES_")):
        log.info("Disabled {hostOSVer} from Coin configuration")
        return False
    # With 5.11 CI will create two sets of release binaries,
    # one with msvc 2015 and one with msvc 2017
    # we shouldn't release the 2015 version.
    # BUT, 32 bit build is done only on msvc 2015...
    if compiler in ["MSVC2015"] and targetArch in ["X86_64"]:
        log.warn(f"Disabled {compiler} to {targetArch} from Coin configuration")
        return False
    return True


def get_ci_qtpaths_path(ci_install_dir, ci_host_os):
    qtpaths_path = f"--qtpaths={ci_install_dir}"
    if ci_host_os == "MacOS":
        return f"{qtpaths_path}/bin/qtpaths"
    elif ci_host_os == "Windows":
        return f"{qtpaths_path}\\bin\\qtpaths.exe"
    else:
        return f"{qtpaths_path}/bin/qtpaths"


def get_ci_qmake_path(ci_install_dir, ci_host_os):
    qmake_path = f"--qmake={ci_install_dir}"
    if ci_host_os == "MacOS":
        return f"{qmake_path}/bin/qmake"
    elif ci_host_os == "Windows":
        return f"{qmake_path}\\bin\\qmake.exe"
    else:
        return f"{qmake_path}/bin/qmake"


def parse_cmake_conf_assignments_by_key(source_dir):
    """
        Parses a .cmake.conf file that contains set(foo "bar") assignments
        and returns a dict with those assignments transformed to keys and
        values.
    """

    d = {}
    contents = (Path(source_dir) / ".cmake.conf").read_text()
    matches = re.findall(r'set\((.+?) "(.*?)"\)', contents)
    for m in matches:
        key = m[0]
        value = m[1]
        if key and value:
            d[key] = value
    return d


def configure_cmake_project(project_path,
                            cmake_path,
                            build_path=None,
                            temp_prefix_build_path=None,
                            cmake_args=None,
                            cmake_cache_args=None,
                            ):
    clean_temp_dir = False
    if not build_path:
        # Ensure parent dir exists.
        if temp_prefix_build_path:
            os.makedirs(temp_prefix_build_path, exist_ok=True)

        project_name = Path(project_path).name
        build_path = tempfile.mkdtemp(prefix=f"{project_name}_", dir=temp_prefix_build_path)

        if 'QFP_SETUP_KEEP_TEMP_FILES' not in os.environ:
            clean_temp_dir = True

    cmd = [cmake_path, '-G', 'Ninja', '-S', project_path, '-B', build_path]

    if cmake_args:
        cmd.extend(cmake_args)

    for arg, value in cmake_cache_args:
        cmd.extend([f'-D{arg}={value}'])

    cmd_string = ' '.join(cmd)
    # FIXME Python 3.7: Use subprocess.run()
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=False,
                            cwd=build_path,
                            universal_newlines=True)
    output, error = proc.communicate()
    proc.wait()
    return_code = proc.returncode

    if return_code != 0:
        raise RuntimeError(f"\nFailed to configure CMake project \n "
                           f"'{project_path}' \n with error: \n {error}\n "
                           f"Return code: {return_code}\n"
                           f"Configure args were:\n  {cmd_string}")

    if clean_temp_dir:
        rmtree(build_path)

    return output


def parse_cmake_project_message_info(output):
    # Parse the output for anything prefixed
    # '-- qfp:<category>:<key>: <value>' as created by the message()
    # calls in a given CMake project and store it in a python dict.
    result = defaultdict(lambda: defaultdict(str))
    pattern = re.compile(r"^-- qfp:(.+?):(.+?):(.*)$")
    for line in output.splitlines():
        found = pattern.search(line)
        if found:
            category = found.group(1).strip()
            key = found.group(2).strip()
            value = found.group(3).strip()
            result[category][key] = str(value)
    return result
