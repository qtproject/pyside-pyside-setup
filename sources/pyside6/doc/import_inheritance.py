import inspect
import sys

"""Helpers for determining base classes by importing the class.
When passed something like:
 PySide6.QtCore.QStateMachine.SignalEvent
try to import the underlying module and return a
handle to the object. In a loop, import
  PySide6.QtCore.QStateMachine.SignalEvent
  PySide6.QtCore.QStateMachine
  PySide6.QtCore
until the import succeeds and walk up the attributes
to obtain the object."""


TEST_DRIVER_USAGE = """Usage: import_inheritance.py class_name [current_module]

Example:
python import_inheritance.py PySide6.QtWidgets.QWizard PySide6.QtWidgets
"""


class InheritanceException(Exception):
    pass


def _importClassOrModule(name):
    components = name.split('.')
    for i in range(len(components), 0, -1):
        importPath = '.'.join(components[: i])
        try:
            __import__(importPath)
        except ImportError:
            continue
        if i == len(components):
            return sys.modules[importPath]
        remaining = components[i:]
        cls = sys.modules[importPath]
        for component in remaining:
            try:
                cls = getattr(cls, component)
            except Exception:  # No such attribute
                return None
        return cls
    return None


def _import_class_or_module(name, currmodule):
    """
    Import a class using its fully-qualified *name*.
    """
    todoc = _importClassOrModule(name)
    if not todoc and currmodule is not None:
        todoc = _importClassOrModule(f"{currmodule}.{name}")
    if not todoc:
        moduleStr = f'(module {currmodule})' if currmodule else ''
        raise InheritanceException(f'Could not import class {name} specified for '
                                   f'inheritance diagram {moduleStr}.')
    if inspect.isclass(todoc):
        return [todoc]
    elif inspect.ismodule(todoc):
        classes = []
        for cls in todoc.__dict__.values():
            if inspect.isclass(cls) and cls.__module__ == todoc.__name__:
                classes.append(cls)
        return classes
    raise InheritanceException(f'{name} specified for inheritance diagram is '
                               'not a class or module')


def _import_classes(class_names, currmodule):
    """Import a list of classes."""
    classes = []
    for name in class_names:
        classes.extend(_import_class_or_module(name, currmodule))
    return classes


def _class_name(cls, parts=0):
    """Given a class object, return a fully-qualified name.

    This works for things I've tested in matplotlib so far, but may not be
    completely general.
    """
    module = cls.__module__
    if module == '__builtin__':
        fullname = cls.__name__
    else:
        fullname = f"{module}.{cls.__qualname__}"
    if parts == 0:
        return fullname
    name_parts = fullname.split('.')
    return '.'.join(name_parts[-parts:])


def _class_info(classes, builtins=None, show_builtins=False, parts=0):
    """Return name and bases for all classes that are ancestors of
    *classes*.

    *parts* gives the number of dotted name parts that is removed from the
    displayed node names.
    """
    all_classes = {}
    builtins_list = builtins.values() if builtins else []

    def recurse(cls):
        if not show_builtins and cls in builtins_list:
            return

        nodename = _class_name(cls, parts)
        fullname = _class_name(cls, 0)

        baselist = []
        all_classes[cls] = (nodename, fullname, baselist)
        for base in cls.__bases__:
            if not show_builtins and base in builtins_list:
                continue
            if base.__name__ == "Object" and base.__module__ == "Shiboken":
                continue
            baselist.append(_class_name(base, parts))
            if base not in all_classes:
                recurse(base)

    for cls in classes:
        recurse(cls)

    return list(all_classes.values())


def get_inheritance_entries_by_import(class_names, currmodule,
                                      builtins=None,
                                      show_builtins=False, parts=0):
    classes = _import_classes(class_names, currmodule)
    class_info = _class_info(classes, builtins, show_builtins, parts)
    if not class_info:
        raise InheritanceException('No classes found for '
                                   'inheritance diagram')
    return class_info


if __name__ == "__main__":
    module = None
    if len(sys.argv) < 2:
        print(TEST_DRIVER_USAGE)
        sys.exit(-1)
    class_name = sys.argv[1]
    if len(sys.argv) >= 3:
        module = sys.argv[2]
    entries = get_inheritance_entries_by_import([class_name], module, None,
                                                False, 2)
    for e in entries:
        print(e)
