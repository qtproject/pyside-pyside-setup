# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

"""
Python backing the C++ ``@auto_properties`` decorator.

This module is loaded lazily from the C++ ``@auto_properties`` decorator
via ``PyImport_ImportModule("PySide6.support.auto_property_helper")``.

@auto_properties recognises three sources of reactive state:

* **plain ``self.<name> = <value>`` assignments** found in ``__init__`` --
  a :class:`~PySide6.QtCore.Property` is *built* for each;
* **native Python ``@property`` declarations** -- *converted* into a
  :class:`~PySide6.QtCore.Property`, reusing the user's getter/setter;
* **existing :class:`~PySide6.QtCore.Property` declarations** -- left as
  declared; their setter is only wrapped when an observer eg: @watch targets them.

Built-in Python types are mapped to precise Qt types so QML sees, e.g., an
``int`` or ``QString`` property: the type comes from the ``__init__`` default
value, or from the getter's ``return`` annotation for ``@property`` and
``@computed``. If the type cannot be determined, it falls back to ``QVariant``.
"""

import ast
import inspect
import logging
import textwrap
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from PySide6.QtCore import Property, Signal
from PySide6.QtQmlFeatures import Change as ChangeType

_logger = logging.getLogger("qt.pyside.libpysideqml")

# Sentinel for first assignment from __init__
# this should not trigger the observers like @watch, @effect etc.
_UNSET = object()

# Sentinel for no cached computed value yet
_COMPUTED_NO_VALUE = object()

# Observer attribute names
_WATCH_ATTR = "_pyside_watch"
_EFFECT_ATTR = "_pyside_effect"
_COMPUTED_ATTR = "_pyside_computed"

# Built-in Python types -> Qt metatype names. Used for precise typing so
# QML sees an ``int``/``QString`` property rather than an opaque ``QVariant``.
_PY_TYPE_TO_QT = {
    bool: "bool",
    int: "int",
    float: "double",
    str: "QString",
    bytes: "QByteArray",
    list: "QVariantList",
    tuple: "QVariantList",
    dict: "QVariantMap",
}

# String annotation name (PEP 563 / forward refs) -> Qt metatype name.
_NAME_TO_QT = {
    "bool": "bool",
    "int": "int",
    "float": "double",
    "str": "QString",
    "bytes": "QByteArray",
}


def _computed_keys(name: str) -> Tuple[str, str]:
    """Return (cache_key, dirty_key) for a computed property."""
    return f"_computed_{name}_cache", f"_computed_{name}_dirty"

# __init__ assignment discovery


class InitAttributeFinder(ast.NodeVisitor):
    """AST visitor that finds all ``self.attribute = ...`` assignments
    inside ``__init__``."""

    def __init__(self):
        self.attributes: Dict[str, Any] = {}
        self.in_init = False

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if node.name == "__init__":
            self.in_init = True
            self.generic_visit(node)
            self.in_init = False

    def visit_Assign(self, node: ast.Assign):
        if not self.in_init:
            return
        for target in node.targets:
            if isinstance(target, ast.Attribute):
                if isinstance(target.value, ast.Name) and target.value.id == "self":
                    self.attributes[target.attr] = self._default(node.value)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign):
        """Handle annotated assignments like ``self.counter: int = 0``."""
        if not self.in_init:
            return
        if isinstance(node.target, ast.Attribute):
            if isinstance(node.target.value, ast.Name) and node.target.value.id == "self":
                default = self._default(node.value) if node.value else None
                self.attributes[node.target.attr] = default
        self.generic_visit(node)

    @staticmethod
    def _default(value_node) -> Any:
        """Best-effort static extraction of a literal default value."""
        if isinstance(value_node, ast.Constant):
            return value_node.value
        if isinstance(value_node, ast.List):
            return []
        if isinstance(value_node, ast.Dict):
            return {}
        return None


def find_init_attributes(cls, exclude: Optional[Set[str]] = None) -> Dict[str, Any]:
    """Find all ``self.<name> = <value>`` assignments in *cls*'s ``__init__``.

    Returns a dict mapping attribute name -> default value (or ``None``
    when the default cannot be statically determined.

    Private attributes (starting with ``_``), names in *exclude*, and
    names already backed by a native ``property`` or a PySide
    PySide6.QtCore.Property descriptor are omitted, so an
    explicitly declared member always wins over an ``__init__`` guess.
    """
    exclude = exclude or set()
    if not hasattr(cls, "__init__"):
        return {}

    try:
        source = textwrap.dedent(inspect.getsource(cls.__init__))
        tree = ast.parse(source)
    except OSError:
        # The .py file is not on disk, so the assignments cannot be read.
        # Deployed applications hit this when only .pyc files are shipped,
        # which silently leaves the class without any of its properties.
        _logger.warning("@auto_properties: no source available for %s.__init__, "
                        "so no properties were created from its assignments. "
                        "Ship the .py files alongside the .pyc ones to fix this.",
                        getattr(cls, "__qualname__", cls))
        return {}
    except (TypeError, SyntaxError):
        return {}

    finder = InitAttributeFinder()
    finder.visit(tree)

    return {
        name: default
        for name, default in finder.attributes.items()
        if not name.startswith("_")
        and name not in exclude
        and not _is_any_property(_static_lookup(cls, name))
    }

# Descriptor / signal helpers


def _is_qt_property(obj) -> bool:
    """True if *obj* is a ``PySide6.QtCore.Property`` descriptor."""
    return isinstance(obj, Property)


def _is_native_property(obj) -> bool:
    """True if *obj* is a built-in Python ``property`` descriptor."""
    return isinstance(obj, property)


def _is_any_property(obj) -> bool:
    return _is_native_property(obj) or _is_qt_property(obj)


def _is_signal(obj) -> bool:
    return isinstance(obj, Signal)


def _static_lookup(cls, name):
    """Return the class attribute *name* without invoking descriptors."""
    try:
        return inspect.getattr_static(cls, name)
    except AttributeError:
        return None


def _signal_arity(signal) -> int:
    """Number of arguments the *signal* carries.

    A change-notification signal is normally argless; Qt also allows it
    to carry the new value, e.g. ``valueChanged(int)``.  Derived from the
    signal's first signature, ``"name(int,QString)"`` -> ``2``.
    """
    signatures = getattr(signal, "signatures", None)
    if not signatures:
        return 0
    first = signatures[0]
    inside = first[first.find("(") + 1:first.rfind(")")].strip()
    return len(inside.split(",")) if inside else 0


def _ensure_changed_signal(cls, prop_name: str, *, for_emit: bool):
    """Return ``(signal_obj, arity)`` for *prop_name*'s change signal.

    Reuse an existing ``<name>Changed`` :class:`~PySide6.QtCore.Signal`
    if one is declared, otherwise create an argless one.  When the signal
    will be emitted by a setter we own (*for_emit*), a multi-argument
    signal is rejected because there is no value to pass beyond the new
    one.
    """
    signal_name = f"{prop_name}Changed"
    existing = _static_lookup(cls, signal_name)
    if _is_signal(existing):
        arity = _signal_arity(existing)
        if for_emit and arity > 1:
            raise TypeError(
                f"@auto_properties: notify signal '{signal_name}' must take "
                f"at most one argument (the new value); it takes {arity}")
        return existing, arity

    sig = Signal()
    setattr(cls, signal_name, sig)
    if hasattr(sig, "__set_name__"):
        sig.__set_name__(cls, signal_name)
    return sig, 0


def _emit_changed(instance, signal_name: str, arity: int, value) -> None:
    """Emit *instance*'s ``<name>Changed`` signal, matching its arity."""
    signal = getattr(instance, signal_name, None)
    if signal is None or not hasattr(signal, "emit"):
        return
    try:
        signal.emit() if arity == 0 else signal.emit(value)
    except RuntimeError:
        pass


def _qt_type_from_pytype(py_type) -> str:
    """Qt metatype name for a Python *type*; ``QVariant`` when unknown.

    Exact built-in types are matched first; subclasses fall back to their
    nearest built-in base (``bool`` before ``int``).
    """
    name = _PY_TYPE_TO_QT.get(py_type)
    if name is not None:
        return name
    if isinstance(py_type, type):
        if issubclass(py_type, bool):
            return "bool"
        if issubclass(py_type, int):
            return "int"
        if issubclass(py_type, float):
            return "double"
        if issubclass(py_type, str):
            return "QString"
        if issubclass(py_type, (list, tuple)):
            return "QVariantList"
        if issubclass(py_type, dict):
            return "QVariantMap"
    return "QVariant"


def _qt_type_for_value(default) -> str:
    """Qt metatype name inferred from an ``__init__`` default *value*.

    ``QVariant`` when the value is ``None`` or its type is not a known
    built-in (e.g. the default could not be determined statically).
    """
    if default is None:
        return "QVariant"
    return _qt_type_from_pytype(type(default))


def _resolve_qt_type(getter) -> str:
    """Qt metatype name for a property, from its *getter* return annotation.

    Built-in primitives map to their precise Qt type (``int``, ``double``,
    ``bool``, ``QString``, ...); ``list``/``dict`` map to ``QVariantList``/
    ``QVariantMap``; anything unknown or unannotated falls back to
    ``QVariant``.  Both real annotation objects and PEP 563 string
    annotations are handled.
    """
    if getter is None:
        return "QVariant"
    annotations = getattr(getter, "__annotations__", None)
    if not isinstance(annotations, dict):
        return "QVariant"
    ret = annotations.get("return")
    if ret is None:
        return "QVariant"
    if isinstance(ret, type):
        return _qt_type_from_pytype(ret)
    # Parameterised (``list[int]``) or PEP 563 string annotations.
    text = str(ret)
    if "list[" in text or text.startswith(("typing.List", "List[")):
        return "QVariantList"
    if "dict[" in text or text.startswith(("typing.Dict", "Dict[")):
        return "QVariantMap"
    return _NAME_TO_QT.get(text, "QVariant")


# Observer collection

def _collect_observers(cls) -> Dict[str, Dict[str, List[Callable]]]:
    """Scan *cls* for methods decorated with @watch / @effect."""
    observers: Dict[str, Dict[str, List[Callable]]] = {}
    for name in dir(cls):
        try:
            obj = getattr(cls, name)
        except AttributeError:
            continue
        watched_props = getattr(obj, _WATCH_ATTR, None)
        if watched_props and isinstance(watched_props, list):
            for prop in watched_props:
                observers.setdefault(prop, {"watchers": [], "effects": []})
                observers[prop]["watchers"].append(obj)
        effect_props = getattr(obj, _EFFECT_ATTR, None)
        if effect_props and isinstance(effect_props, list):
            for prop in effect_props:
                observers.setdefault(prop, {"watchers": [], "effects": []})
                observers[prop]["effects"].append(obj)
    return observers


def _collect_computed(cls) -> Dict[str, Dict[str, Any]]:
    """Scan *cls* for methods decorated with @computed.

    The ``@computed`` decorator stores its dependency names as a plain
    list on the method under ``_pyside_computed``.
    """
    result: Dict[str, Dict[str, Any]] = {}
    for name in dir(cls):
        try:
            obj = getattr(cls, name)
        except AttributeError:
            continue
        deps = getattr(obj, _COMPUTED_ATTR, None)
        if isinstance(deps, list):
            result[name] = {"func": obj, "deps": list(deps)}
    return result


def _computed_invalidators(prop_name, computed_methods, cls_name):
    """Return the ``@computed`` entries that depend on *prop_name*."""
    invalidators = []
    for comp_name, comp_info in computed_methods.items():
        if comp_info["deps"] and prop_name in comp_info["deps"]:
            comp_sig = f"{comp_name}Changed"
            invalidators.append(
                (comp_name, comp_sig, comp_info["func"], cls_name))
    return invalidators


# the computed property value is cached in self.__dict__[cache_key], and
# self.__dict__[dirty_key] tracks whether it needs to be recomputed on next access.
# When a dependency changes, the dirty flag is set to True, so the next access will
# recompute the value and emit change if needed.
def _recompute(instance, comp_name, comp_sig_name, comp_fn, cls_name):
    """Re-evaluate a computed property and emit its signal if changed."""
    cache_key, dirty_key = _computed_keys(comp_name)
    old_value = instance.__dict__.get(cache_key, _COMPUTED_NO_VALUE)
    try:
        new_value = comp_fn(instance)
    except Exception:
        _logger.exception("@computed re-evaluation of %s.%s failed",
                          cls_name, comp_name)
        return
    instance.__dict__[cache_key] = new_value
    instance.__dict__[dirty_key] = False
    if old_value is not _COMPUTED_NO_VALUE and old_value != new_value:
        _emit_changed(instance, comp_sig_name, 0, new_value)


def _run_observers(instance, prop_name, old_value, new_value,
                   watchers, effects, computed_invalidators, cls_name):
    """Invoke @watch / @effect / @computed observers for one change."""
    for watcher in watchers:
        try:
            watcher(instance, ChangeType(name=prop_name, old=old_value,
                                         new=new_value, owner=instance))
        except Exception:
            _logger.exception("@watch %s failed for %s.%s",
                              getattr(watcher, "__name__", watcher),
                              cls_name, prop_name)
    for eff in effects:
        try:
            eff(instance)
        except Exception:
            _logger.exception("@effect %s failed for %s.%s",
                              getattr(eff, "__name__", eff),
                              cls_name, prop_name)
    for c_name, c_sig, c_fn, c_cls in computed_invalidators:
        try:
            _recompute(instance, c_name, c_sig, c_fn, c_cls)
        except Exception:
            _logger.exception("@computed %s failed for %s.%s",
                              c_name, cls_name, prop_name)


# Case 1: plain __init__ attribute -> built Property

def _build_init_property(cls, attr_name, default, observers,
                         computed_methods, cls_name):
    private_name = f"_{attr_name}"
    signal_obj, arity = _ensure_changed_signal(cls, attr_name, for_emit=True)
    signal_name = f"{attr_name}Changed"

    obs = observers.get(attr_name, {"watchers": [], "effects": []})
    watchers = list(obs["watchers"])
    effects = list(obs["effects"])
    # return the list of @computed methods that depend on this property, so they can be invalidated
    # when this property changes
    invalidators = _computed_invalidators(attr_name, computed_methods, cls_name)

    def make_getter(priv, dflt):
        def getter(self):
            return getattr(self, priv, dflt)
        return getter

    def make_setter(priv, sig_name, sig_arity, prop_name, w, e, c,
                    _cls=cls_name):
        def setter(self, value):
            old_value = getattr(self, priv, _UNSET)
            if old_value is _UNSET:
                # First assignment (from __init__)
                # store silently.
                setattr(self, priv, value)
                return
            if old_value == value:
                return
            setattr(self, priv, value)
            _run_observers(self, prop_name, old_value, value, w, e, c, _cls)
            _emit_changed(self, sig_name, sig_arity, value)
        return setter

    prop = Property(
        _qt_type_for_value(default),
        make_getter(private_name, default),
        make_setter(private_name, signal_name, arity, attr_name,
                    watchers, effects, invalidators),
        notify=signal_obj,
    )
    setattr(cls, attr_name, prop)


# Case 2: native @property -> converted Property

def _convert_native_property(cls, prop_name, pyprop, observers,
                             computed_methods, cls_name):
    type_name = _resolve_qt_type(pyprop.fget)

    if pyprop.fset is None:
        # Read-only: a getter-only Q_PROPERTY already raises on write,
        # so QML cannot set it
        # no change signal is needed.
        if prop_name in observers:
            _logger.warning("@auto_properties: %s.%s is read-only; @watch/"
                            "@effect cannot be wired to it",
                            cls_name, prop_name)
        setattr(cls, prop_name, Property(type_name, pyprop.fget))
        return

    signal_obj, arity = _ensure_changed_signal(cls, prop_name, for_emit=True)
    signal_name = f"{prop_name}Changed"
    obs = observers.get(prop_name, {"watchers": [], "effects": []})
    watchers = list(obs["watchers"])
    effects = list(obs["effects"])
    invalidators = _computed_invalidators(prop_name, computed_methods, cls_name)

    def make_setter(orig_fget, orig_fset, sig_name, sig_arity, prop_nm,
                    w, e, c, _cls=cls_name):
        def setter(self, value):
            try:
                old_value = orig_fget(self)
            except Exception:
                old_value = _UNSET
            orig_fset(self, value)
            if old_value is _UNSET:
                return
            try:
                new_value = orig_fget(self)
            except Exception:
                new_value = value
            if old_value == new_value:
                return
            _run_observers(self, prop_nm, old_value, new_value, w, e, c, _cls)
            _emit_changed(self, sig_name, sig_arity, new_value)
        return setter

    prop = Property(
        type_name,
        pyprop.fget,
        make_setter(pyprop.fget, pyprop.fset, signal_name, arity,
                    prop_name, watchers, effects, invalidators),
        notify=signal_obj,
    )
    setattr(cls, prop_name, prop)


# Case 3: existing PySide Property -> wire observers only

def _wire_existing_qt_property(cls, prop_name, qtprop, observers,
                               computed_methods, cls_name):
    invalidators = _computed_invalidators(prop_name, computed_methods, cls_name)
    obs = observers.get(prop_name)
    if not obs and not invalidators:
        # Nothing references it
        # it is already a Q_PROPERTY, leave as is.
        return

    if qtprop.fset is None:
        _logger.warning("@auto_properties: %s.%s is a read-only Property; "
                        "@watch/@effect/@computed cannot be wired to it",
                        cls_name, prop_name)
        return

    watchers = list(obs["watchers"]) if obs else []
    effects = list(obs["effects"]) if obs else []
    orig_fget = qtprop.fget
    orig_fset = qtprop.fset

    def wrapped_setter(self, value, _fget=orig_fget, _fset=orig_fset,
                       _prop=prop_name, _w=watchers, _e=effects,
                       _c=invalidators, _cls=cls_name):
        old_value = _fget(self) if _fget else None
        _fset(self, value)
        new_value = _fget(self) if _fget else value
        if old_value == new_value:
            return
        # The user's own setter owns the Qt notify emission; we only add
        # the observer callbacks, so the notify is never double-fired.
        _run_observers(self, _prop, old_value, new_value, _w, _e, _c, _cls)

    # Property.write() clones the descriptor, preserving its type and the
    # declared notify signal, swapping in our observer-aware setter.
    setattr(cls, prop_name, qtprop.write(wrapped_setter))


# Case 4: @computed -> read-only Property

def _build_computed_property(cls, comp_name, comp_info, cls_name):
    comp_fn = comp_info["func"]
    signal_obj, _ = _ensure_changed_signal(cls, comp_name, for_emit=True)
    signal_name = f"{comp_name}Changed"
    type_name = _resolve_qt_type(comp_fn)

    def make_getter(fn, name, sig_name, _cls=cls_name):
        def getter(self):
            cache_key, dirty_key = _computed_keys(name)
            if self.__dict__.get(dirty_key, True):
                try:
                    value = fn(self)
                except Exception:
                    _logger.exception("@computed %s.%s failed", _cls, name)
                    return self.__dict__.get(cache_key)
                old_value = self.__dict__.get(cache_key, _COMPUTED_NO_VALUE)
                self.__dict__[cache_key] = value
                self.__dict__[dirty_key] = False
                if old_value is not _COMPUTED_NO_VALUE and old_value != value:
                    _emit_changed(self, sig_name, 0, value)
            return self.__dict__.get(cache_key)
        return getter

    prop = Property(type_name,
                    make_getter(comp_fn, comp_name, signal_name),
                    notify=signal_obj)
    setattr(cls, comp_name, prop)


# Orchestration

def _declared_properties(cls):
    """Return (native_props, qt_props) declared on *cls* or its bases.

    Each is a dict mapping public attribute name -> descriptor.
    """
    native: Dict[str, Any] = {}
    qt: Dict[str, Any] = {}
    for name in dir(cls):
        if name.startswith("_"):
            continue
        obj = _static_lookup(cls, name)
        if _is_qt_property(obj):
            qt[name] = obj
        elif _is_native_property(obj):
            native[name] = obj
    return native, qt


def augment_class(cls):
    """Make *cls* fully reactive and QML-bindable.

    Builds PySide6.QtCore.Property objects for ``__init__``
    attributes, converts native ``@property`` declarations, wires
    observers onto existing PySide6.QtCore.Property objects, and
    materialises ``@computed`` properties.  Called from the C++
    ``@auto_properties`` class decorator after QObject validation; the
    decorator rebuilds the ``QMetaObject`` afterwards.

    Returns *cls* (modified in-place).
    """
    cls_name = getattr(cls, "__name__", str(cls))
    observers = _collect_observers(cls)
    computed_methods = _collect_computed(cls)
    native_props, qt_props = _declared_properties(cls)

    # Declared members win over __init__ guesses of the same name.
    reserved = set(native_props) | set(qt_props) | set(computed_methods)
    attributes = find_init_attributes(cls, exclude=reserved)

    for attr_name, default in attributes.items():
        _build_init_property(cls, attr_name, default, observers,
                             computed_methods, cls_name)

    for prop_name, pyprop in native_props.items():
        _convert_native_property(cls, prop_name, pyprop, observers,
                                 computed_methods, cls_name)

    for prop_name, qtprop in qt_props.items():
        _wire_existing_qt_property(cls, prop_name, qtprop, observers,
                                   computed_methods, cls_name)

    for comp_name, comp_info in computed_methods.items():
        _build_computed_property(cls, comp_name, comp_info, cls_name)

    cls._pyside_auto_props_applied = True
    cls._pyside_computed_props = frozenset(computed_methods.keys())
    return cls
