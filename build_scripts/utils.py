# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import errno
import fnmatch
import glob
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
from textwrap import dedent, indent

from .log import log
from . import (PYSIDE_PYTHON_TOOLS, PYSIDE_LINUX_BIN_TOOLS, PYSIDE_UNIX_LIBEXEC_TOOLS,
               PYSIDE_WINDOWS_BIN_TOOLS, PYSIDE_UNIX_BIN_TOOLS, PYSIDE_UNIX_BUNDLED_TOOLS)

try:
    # Using the distutils implementation within setuptools
    from setuptools.errors import SetupError
except ModuleNotFoundError:
    # This is motivated by our CI using an old version of setuptools
    # so then the coin_build_instructions.py script is executed, and
    # import from this file, it was failing.
    from distutils.errors import DistutilsSetupError as SetupError

try:
    WindowsError
except NameError:
    WindowsError = None


def which(name):
    """
    Like shutil.which, but accepts a string or a PathLike and returns a Path
    """
    path = None
    try:
        if isinstance(name, Path):
            name = str(name)
        path = shutil.which(name)
        if path is None:
            raise TypeError("None was returned")
        path = Path(path)
    except TypeError as e:
        log.error(f"{name} was not found in PATH: {e}")
    return path


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
        if str(path).lower() not in paths:
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


def copyfile(src, dst, force=True, _vars=None, force_copy_symlink=False,
             make_writable_by_owner=False):
    if isinstance(src, str):
        src = Path(src.format(**_vars)) if _vars else Path(src)
    if isinstance(dst, str):
        dst = Path(dst.format(**_vars)) if _vars else Path(dst)
    assert(isinstance(src, Path))
    assert(isinstance(dst, Path))

    if not src.exists() and not force:
        log.info(f"**Skipping copy file\n  {src} to\n  {dst}\n  Source does not exist")
        return

    if not src.is_symlink() or force_copy_symlink:
        if dst.is_file():
            src_stat = os.stat(src)
            dst_stat = os.stat(dst)
            if (src_stat.st_size == dst_stat.st_size
                    and src_stat.st_mtime <= dst_stat.st_mtime):
                log.info(f"{dst} is up to date.")
                return dst

        log.debug(f"Copying file\n  {src} to\n  {dst}.")
        shutil.copy2(src, dst)
        if make_writable_by_owner:
            make_file_writable_by_owner(dst)

        return dst

    # We use 'strict=False' to mimic os.path.realpath in case
    # the directory doesn't exist.
    link_target_path = src.resolve(strict=False)
    if link_target_path.parent == src.parent:
        link_target = Path(link_target_path.name)
        link_name = Path(src.name)
        current_directory = Path.cwd()
        try:
            target_dir = dst if dst.is_dir() else dst.parent
            os.chdir(target_dir)
            if link_name.exists():
                if (link_name.is_symlink()
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


def makefile(dst, content=None, _vars=None):
    if _vars is not None:
        if content is not None:
            content = content.format(**_vars)
        dst = Path(dst.format(**_vars))

    log.info(f"Making file {dst}.")

    dstdir = dst.parent
    if not dstdir.exists():
        dstdir.mkdir(parents=True)

    with open(dst, "wt") as f:
        if content is not None:
            f.write(content)


def copydir(src, dst, _filter=None, ignore=None, force=True, recursive=True, _vars=None,
            dir_filter_function=None, file_filter_function=None, force_copy_symlinks=False):

    if isinstance(src, str):
        src = Path(src.format(**_vars)) if _vars else Path(src)
    if isinstance(dst, str):
        dst = Path(dst.format(**_vars)) if _vars else Path(dst)
    assert(isinstance(src, Path))
    assert(isinstance(dst, Path))

    if _vars is not None:
        if _filter is not None:
            _filter = [i.format(**_vars) for i in _filter]
        if ignore is not None:
            ignore = [i.format(**_vars) for i in ignore]

    if not src.exists() and not force:
        log.info(f"**Skipping copy tree\n  {src} to\n  {dst}\n  Source does not exist. "
                 f"filter={_filter}. ignore={ignore}.")
        return []

    log.debug(f"Copying tree\n  {src} to\n  {dst}. filter={_filter}. ignore={ignore}.")

    names = os.listdir(src)

    results = []
    copy_errors = []
    for name in names:
        srcname = src / name
        dstname = dst / name
        try:
            if srcname.is_dir():
                if (dir_filter_function and not dir_filter_function(name, src, srcname)):
                    continue
                if recursive:
                    results.extend(copydir(srcname, dstname, _filter, ignore, force, recursive,
                                           _vars, dir_filter_function, file_filter_function,
                                           force_copy_symlinks))
            else:
                if ((file_filter_function is not None and not file_filter_function(name, srcname))
                        or (_filter is not None and not filter_match(name, _filter))
                        or (ignore is not None and filter_match(name, ignore))):
                    continue
                if not dst.is_dir():
                    dst.mkdir(parents=True)
                results.append(copyfile(srcname, dstname, True, _vars, force_copy_symlinks))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except shutil.Error as err:
            copy_errors.extend(err.args[0])
        except EnvironmentError as why:
            copy_errors.append((srcname, dstname, str(why)))
    try:
        if dst.exists():
            shutil.copystat(str(src), str(dst))
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


def remove_tree(dirname, ignore=False):
    def handle_remove_readonly(func, path, exc):
        # exc returns like 'sys.exc_info()': type, value, traceback
        _, excvalue, _ = exc
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
    log.debug(f"In directory {Path.cwd()}:\n\tRunning command:  {command}")

    if initial_env is None:
        initial_env = os.environ

    kwargs = {}
    kwargs['env'] = initial_env

    exit_code = subprocess.call(args, **kwargs)
    return exit_code


def back_tick(cmd, ret_err=False):
    """
    Run command `cmd`, return stdout, or (stdout, stderr,
    return_code) if `ret_err` is True.

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
    with subprocess.Popen(cmd, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, shell=True) as proc:
        out_bytes, err_bytes = proc.communicate()
        out = out_bytes.decode().strip()
        err = err_bytes.decode().strip()
        retcode = proc.returncode
        if retcode is None and not ret_err:
            proc.terminate()
            raise RuntimeError(f"{cmd} process did not terminate")
        if retcode != 0 and not ret_err:
            raise RuntimeError(f"{cmd} process returned code {retcode}\n*** {err}")
    if not ret_err:
        return out
    return out, err, retcode


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
    try:
        back_tick(f"install_name_tool -add_rpath {rpath} {library_path}")
    except RuntimeError as e:
        print(f"Exception {type(e).__name__}: {e}")


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


def macos_add_qt_rpath(library_path, qt_lib_dir, existing_rpath_commands=None,
                       library_dependencies=None):
    """
    Adds an rpath load command to the Qt lib directory if necessary

    Checks if library pointed to by 'library_path' has Qt dependencies,
    and adds an rpath load command that points to the Qt lib directory
    (qt_lib_dir).
    """
    if existing_rpath_commands is None:
        existing_rpath_commands = []

    if library_dependencies is None:
        library_dependencies = []

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
        for match in glob.glob(str(Path(path) / pattern)):
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
    return (Path(clang_dir), source)


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
                candidate = Path("c:\\Program Files\\7-Zip\\7z.exe")
                if candidate.exists():
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
        rtld = Path(rtld)
        if rtld.is_file() and os.access(rtld, os.X_OK):
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
        log.warning(message)
    if not result:
        result = _ldd_ldso(executable_path)
    return result


def find_files_using_glob(path, pattern):
    """ Returns list of files that matched glob `pattern` in `path`. """
    final_pattern = Path(path) / pattern
    maybe_files = glob.glob(str(final_pattern))
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
# Note: Uses ldd to query shared library dependencies and thus does not
# work for cross builds.
def copy_icu_libs(patchelf, destination_lib_dir):
    """
    Copy ICU libraries that QtCore depends on,
    to given `destination_lib_dir`.
    """
    qt_core_library_path = Path(find_qt_core_library_glob(destination_lib_dir))

    if not qt_core_library_path or not qt_core_library_path.exists():
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
        log.debug('Copying the detected ICU libraries required by QtCore.')

        destination_lib_dir = Path(destination_lib_dir)
        if not destination_lib_dir.exists():
            destination_lib_dir.mkdir(parents=True)

        for path in paths:
            basename = Path(path).name
            destination = destination_lib_dir / basename
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

    cmd = [str(patchelf), '--set-rpath', str(rpath_string), str(executable_path)]

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

    qt_rpath = str(qt_rpath)
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


def get_qtci_virtualEnv(python_ver, host, hostArch, targetArch):
    _pExe = "python"
    _env = f"{os.environ.get('PYSIDE_VIRTUALENV') or 'env'+python_ver}"
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
                _path = Path(os.getenv(var, ""))
                _pExe = _path / "python.exe"
                if not _pExe.is_file():
                    log.warn(f"Can't find python.exe from {_pExe}, using default python3")
                    _pExe = Path(os.getenv("PYTHON3_32_PATH")) / "python.exe"
            else:
                _pExe = Path(os.getenv("PYTHON2_32_PATH")) / "python.exe"
        else:
            if python_ver.startswith("3"):
                var = f"PYTHON{python_ver}-64_PATH"
                log.info(f"Try to find python from {var} env variable")
                _path = Path(os.getenv(var, ""))
                _pExe = _path / "python.exe"
                if not _pExe.is_file():
                    log.warn(f"Can't find python.exe from {_pExe}, using default python3")
                    _pExe = Path(os.getenv("PYTHON3_PATH")) / "python.exe"
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

    contents = (Path(source_dir) / ".cmake.conf").read_text()
    matches = re.findall(r'set\((.+?) "(.*?)"\)', contents)
    d = {key: value for key, value in matches}
    return d


def _configure_failure_message(project_path, cmd, return_code, output, error, env):
    """Format a verbose message about configure_cmake_project() failures."""
    cmd_string = ' '.join(cmd)
    error_text = indent(error.strip(), "    ")
    output_text = indent(output.strip(), "    ")
    result = dedent(f"""
                 Failed to configure CMake project: '{project_path}'
                 Configure args were:
                     {cmd_string}
                 Return code: {return_code}
                 """)

    first = True
    for k, v in env.items():
        if k.startswith("CMAKE"):
            if first:
                result += "Environment:\n"
                first = False
            result += f"    {k}={v}\n"

    result += f"\nwith error:\n{error_text}\n"

    CMAKE_CMAKEOUTPUT_LOG_PATTERN = r'See also "([^"]+CMakeOutput\.log)"\.'
    cmakeoutput_log_match = re.search(CMAKE_CMAKEOUTPUT_LOG_PATTERN, output)
    if cmakeoutput_log_match:
        cmakeoutput_log = Path(cmakeoutput_log_match.group(1))
        if cmakeoutput_log.is_file():
            log = indent(cmakeoutput_log.read_text().strip(), "    ")
            result += f"CMakeOutput.log:\n{log}\n"

    result += f"Output:\n{output_text}\n"
    return result


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

    cmd = [str(i) for i in cmd]

    proc = subprocess.run(cmd, shell=False, cwd=build_path,
                          capture_output=True, universal_newlines=True)
    return_code = proc.returncode
    output = proc.stdout
    error = proc.stderr

    if return_code != 0:
        m = _configure_failure_message(project_path, cmd, return_code,
                                       output, error, os.environ)
        raise RuntimeError(m)

    if clean_temp_dir:
        remove_tree(build_path)

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


def available_pyside_tools(qt_tools_path: Path, package_for_wheels: bool = False):
    pyside_tools = PYSIDE_PYTHON_TOOLS.copy()

    if package_for_wheels:
        # Qt wrappers in build/{python_env_name}/package_for_wheels/PySide6
        bin_path = qt_tools_path
    else:
        bin_path = qt_tools_path / "bin"

    def tool_exist(tool_path: Path):
        if tool_path.exists():
            return True
        else:
            log.warning(f"{tool_path} not found. pyside-{tool_path.name} not included.")
            return False

    if sys.platform == 'win32':
        pyside_tools.extend([tool for tool in PYSIDE_WINDOWS_BIN_TOOLS
                             if tool_exist(bin_path / f"{tool}.exe")])
    else:
        lib_exec_path = qt_tools_path / "Qt" / "libexec" if package_for_wheels \
                        else qt_tools_path / "libexec"
        pyside_tools.extend([tool for tool in PYSIDE_UNIX_LIBEXEC_TOOLS
                             if tool_exist(lib_exec_path / tool)])
        if sys.platform == 'darwin':
            def name_to_path(name):
                return f"{name.capitalize()}.app/Contents/MacOS/{name.capitalize()}"

            pyside_tools.extend([tool for tool in PYSIDE_UNIX_BIN_TOOLS
                                if tool_exist(bin_path / tool)])
            pyside_tools.extend([tool for tool in PYSIDE_UNIX_BUNDLED_TOOLS
                                if tool_exist(bin_path / name_to_path(tool))])
        else:
            pyside_tools.extend([tool for tool in PYSIDE_LINUX_BIN_TOOLS
                                if tool_exist(bin_path / tool)])

    return pyside_tools


def copy_qt_metatypes(destination_qt_dir, _vars):
    """Copy the Qt metatypes files which changed location in 6.5"""
    # <qt>/[lib]?/metatypes/* -> <setup>/{st_package_name}/Qt/[lib]?/metatypes
    qt_meta_types_dir = "{qt_metatypes_dir}".format(**_vars)
    qt_prefix_dir = "{qt_prefix_dir}".format(**_vars)
    rel_meta_data_dir = os.fspath(Path(qt_meta_types_dir).relative_to(qt_prefix_dir))
    copydir(qt_meta_types_dir, destination_qt_dir / rel_meta_data_dir,
            _filter=["*.json"],
            recursive=False, _vars=_vars, force_copy_symlinks=True)
