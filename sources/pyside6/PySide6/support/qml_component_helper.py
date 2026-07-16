# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

"""
Python backing the C++ ``load_qml_component`` type in ``PySide6.QtQmlFeatures``.

This module is loaded lazily from the C++ ``load_qml_component`` type via
``PyImport_ImportModule("PySide6.support.qml_component_helper")``. It
holds the actual QML component loading logic and the Pythonic wrappers
returned to user code.

``load_qml_component(engine, ...)`` returns a :class:`QmlComponentFactory`;
its ``create()`` instantiates the component and returns a
:class:`QmlObject` that exposes QML properties, signals, and methods as
plain Python attributes.
"""

from __future__ import annotations

import inspect
import logging
from pathlib import Path
from typing import Any

from PySide6.QtCore import QMetaMethod, QMetaObject, QObject, QUrl, Qt
from PySide6.QtQml import QQmlComponent

_logger = logging.getLogger("qt.pyside.libpysideqml")


class _MethodInvoker:
    """Callable wrapper around QMetaObject.invokeMethod for one method."""

    def __init__(self, qobj: QObject, method_name: str) -> None:
        self._qobj = qobj
        self._method_name = method_name

    def __call__(self, *args: Any) -> Any:
        # NOTE: DirectConnection invoke returns a success flag, not the
        # QML function's return value (current preview limitation).
        return QMetaObject.invokeMethod(
            self._qobj, self._method_name, Qt.ConnectionType.DirectConnection, *args)

    def __repr__(self) -> str:
        return f"<QmlMethod {self._method_name} of {self._qobj}>"


class QmlObject:
    """Python wrapper around a QML-created QObject using composition."""

    def __init__(self, qobj: QObject, component=None) -> None:
        # object.__setattr__ bypasses our custom __setattr__.
        object.__setattr__(self, "_qobj", qobj)
        # Keep the QQmlComponent alive for the object's lifetime.
        object.__setattr__(self, "_component", component)
        object.__setattr__(self, "_method_cache", {})

        meta = qobj.metaObject()
        methods: set[str] = set()
        for i in range(meta.methodOffset(), meta.methodCount()):
            method = meta.method(i)
            if method.methodType() in (QMetaMethod.MethodType.Method,
                                       QMetaMethod.MethodType.Slot):
                methods.add(bytes(method.name().data()).decode("utf-8"))
        object.__setattr__(self, "_methods", methods)

    def __getattr__(self, name: str) -> Any:
        qobj = object.__getattribute__(self, "_qobj")
        methods = object.__getattribute__(self, "_methods")

        # Q_PROPERTY lookup first so typed properties (width/height)
        # return their value rather than a bound C++ getter.
        meta = qobj.metaObject()
        if meta.indexOfProperty(name) >= 0:
            val = qobj.property(name)
            # Wrap QObject-typed values so chained access keeps working.
            if isinstance(val, QObject):
                return QmlObject(val)
            return val

        if name in methods:
            cache = object.__getattribute__(self, "_method_cache")
            if name not in cache:
                cache[name] = _MethodInvoker(qobj, name)
            return cache[name]

        try:
            return getattr(qobj, name)
        except AttributeError:
            pass

        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'")

    def __setattr__(self, name: str, value: Any) -> None:
        # Underscore attributes are stored on the wrapper itself.
        if name.startswith("_"):
            object.__setattr__(self, name, value)
            return

        qobj = object.__getattribute__(self, "_qobj")
        if qobj.metaObject().indexOfProperty(name) >= 0:
            # Unwrap QmlObject values so ``child.parent = column`` works.
            actual = (object.__getattribute__(value, "_qobj")
                      if isinstance(value, QmlObject) else value)
            if not qobj.setProperty(name, actual):
                _logger.warning("setProperty('%s', %r) returned False",
                                name, value)
            return

        # Unknown property: store on the wrapper (plain Python attribute).
        object.__setattr__(self, name, value)

    @property
    def qobject(self) -> QObject:
        """Access the underlying QObject directly (escape hatch)."""
        return object.__getattribute__(self, "_qobj")

    def __repr__(self) -> str:
        qobj = object.__getattribute__(self, "_qobj")
        return f"<QmlObject wrapping {qobj.metaObject().className()}>"


class QmlComponentFactory:
    """Factory for creating instances of a QML component from Python.

    Returned by :func:`load_qml_component`. Holds the engine and the component
    source; ``create()`` builds and returns a :class:`QmlObject`.
    """

    def __init__(self, engine, *, file_path: str | None = None,
                 module: str | None = None,
                 type_name: str | None = None) -> None:
        self._engine = engine
        self._file_path = file_path
        self._module = module
        self._type_name = type_name

    def create(self, **initial_properties: Any) -> QmlObject:
        """Create a new instance of the QML component."""
        component = QQmlComponent(self._engine)

        if self._file_path is not None:
            component.loadUrl(QUrl.fromLocalFile(self._file_path))
        elif self._module is not None and self._type_name is not None:
            component.loadFromModule(self._module, self._type_name)
        else:
            raise RuntimeError(
                "QmlComponentFactory has no valid source. Provide either "
                "a file path or module + type_name.")

        if component.isError():
            raise RuntimeError(
                f"Failed to load QML component: {component.errorString()}")

        if not component.isReady():
            raise RuntimeError(
                f"QML component is not ready (status: {component.status()})."
                f" Errors: {component.errorString()}")

        if initial_properties:
            obj = component.createWithInitialProperties_withownership(
                initial_properties)
        else:
            obj = component.create_withownership()

        if obj is None:
            raise RuntimeError(
                f"QQmlComponent.create() returned None. "
                f"Errors: {component.errorString()}")

        _logger.debug("Created QML object: %s",
                      obj.metaObject().className())
        return QmlObject(obj, component)

    def __repr__(self) -> str:
        if self._file_path:
            return f"<QmlComponentFactory file='{self._file_path}'>"
        return (f"<QmlComponentFactory module='{self._module}' "
                f"type='{self._type_name}'>")


def create_factory(engine, source: str | None = None, *,
                   module: str | None = None,
                   type_name: str | None = None) -> QmlComponentFactory:
    """Build a :class:`QmlComponentFactory` for a QML component.

    Backs the public ``load_qml_component(engine, ...)`` type. Exactly one of
    ``source`` or (``module`` + ``type_name``) must be supplied. Relative
    ``source`` paths are resolved against the calling frame's directory.
    """
    if engine is None:
        raise TypeError(
            "load_qml_component requires a QQmlEngine as its first argument")

    if source is not None:
        path = Path(source)
        if not path.is_absolute():
            # The C++ trampoline adds no Python frame, so stack()[1] is
            # the user's calling frame; when called directly it is the
            # caller of create_factory. Both resolve correctly.
            caller_frame = inspect.stack()[1]
            caller_dir = Path(caller_frame.filename).resolve().parent
            path = (caller_dir / path).resolve()
        return QmlComponentFactory(engine, file_path=str(path))

    if module is not None and type_name is not None:
        return QmlComponentFactory(engine, module=module,
                                   type_name=type_name)

    raise ValueError(
        "load_qml_component requires either a QML file path as the second "
        "argument, or both 'module' and 'type_name' keyword arguments.")
