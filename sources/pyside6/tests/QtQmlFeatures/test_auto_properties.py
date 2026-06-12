# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, Signal, Property, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QmlElement, QQmlComponent, QQmlEngine
from PySide6.QtQmlFeatures import auto_properties, watch, effect, computed, Change


# @QmlElement reads these module-level names to register the type with the
# QML engine under "import QmlFeaturesTest 1.0".
QML_IMPORT_NAME = "QmlFeaturesTest"
QML_IMPORT_MAJOR_VERSION = 1


class AutoPropertiesBasicTest(unittest.TestCase):
    """@auto_properties on plain __init__ assignments."""

    def test_generates_real_qproperty(self):
        """Generated members are real Q_PROPERTYs, not plain python ones."""
        @auto_properties
        class Cart(QObject):
            def __init__(self):
                super().__init__()
                self.price = 10

        # is a PySide Property, not a python property.
        self.assertIsInstance(Cart.__dict__["price"], Property)
        self.assertNotIsInstance(Cart.__dict__["price"], property)

        # is registered in the QMetaObject with a notify signal.
        mo = Cart().metaObject()
        idx = mo.indexOfProperty("price")
        self.assertGreaterEqual(idx, 0)
        self.assertTrue(mo.property(idx).hasNotifySignal())
        self.assertEqual(bytes(mo.property(idx).notifySignal().name()),
                         b"priceChanged")

    def test_builtin_types_are_precise(self):
        """Built-in Python types map to precise Qt types, not QVariant."""
        @auto_properties
        class Bag(QObject):
            def __init__(self):
                super().__init__()
                self.count = 1
                self.ratio = 1.5
                self.flag = True
                self.label = "x"
                self.items = []
                self.mapping = {}
                self.other = None

        mo = Bag().metaObject()

        def type_of(name):
            idx = mo.indexOfProperty(name)
            self.assertGreaterEqual(idx, 0, name)
            return mo.property(idx).typeName()

        self.assertEqual(type_of("count"), "int")
        self.assertEqual(type_of("ratio"), "double")
        self.assertEqual(type_of("flag"), "bool")
        self.assertEqual(type_of("label"), "QString")
        self.assertEqual(type_of("items"), "QVariantList")
        self.assertEqual(type_of("mapping"), "QVariantMap")
        # Undeterminable default -> QVariant fallback.
        self.assertEqual(type_of("other"), "QVariant")

    def test_native_property_type_from_annotation(self):
        """A converted @property takes its Qt type from the getter annotation."""
        @auto_properties
        class Item(QObject):
            def __init__(self):
                super().__init__()
                self._name = ""

            @property
            def name(self) -> str:
                return self._name

            @name.setter
            def name(self, value):
                self._name = value

        mo = Item().metaObject()
        idx = mo.indexOfProperty("name")
        self.assertEqual(mo.property(idx).typeName(), "QString")

    def test_changed_signal_exists(self):
        @auto_properties
        class Cart(QObject):
            def __init__(self):
                super().__init__()
                self.price = 10
                self.quantity = 2

        cart = Cart()
        self.assertTrue(hasattr(cart, "priceChanged"))
        self.assertTrue(hasattr(cart, "quantityChanged"))

    def test_requires_qobject(self):
        with self.assertRaises(TypeError):
            @auto_properties
            class Plain:
                def __init__(self):
                    self.x = 1

    def test_private_attrs_excluded(self):
        @auto_properties
        class Foo(QObject):
            def __init__(self):
                super().__init__()
                self.public = 1
                self._private = 2

        self.assertIsInstance(Foo.__dict__["public"], Property)
        self.assertNotIn("_private", Foo.__dict__)

    def test_double_decoration_is_noop(self):
        @auto_properties
        @auto_properties
        class Foo(QObject):
            def __init__(self):
                super().__init__()
                self.x = 1

        self.assertEqual(Foo().x, 1)


class AutoPropertiesQmlWriteTest(unittest.TestCase):
    """Writes through the Qt meta-property system (the QML write path)."""

    def test_set_property_runs_setter_and_watch(self):
        changes = []

        @auto_properties
        class Cart(QObject):
            def __init__(self):
                super().__init__()
                self.price = 10

            @watch("price")
            def on_price(self, chg: Change):
                changes.append(chg)

        cart = Cart()
        # setProperty() goes through QMetaObject::WriteProperty, exactly as a
        # QML binding assignment does.
        self.assertTrue(cart.setProperty("price", 42))
        self.assertEqual(cart.property("price"), 42)
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0].new, 42)

    def test_set_property_emits_notify_once(self):
        emitted = []

        @auto_properties
        class Cart(QObject):
            def __init__(self):
                super().__init__()
                self.price = 10

        cart = Cart()
        cart.priceChanged.connect(lambda: emitted.append(1))
        cart.setProperty("price", 5)
        self.assertEqual(len(emitted), 1)


class AutoPropertiesWatchTest(unittest.TestCase):

    def test_watch_fires_on_change(self):
        changes = []

        @auto_properties
        class Cart(QObject):
            def __init__(self):
                super().__init__()
                self.price = 10

            @watch("price")
            def on_price(self, chg: Change):
                changes.append(chg)

        cart = Cart()
        cart.price = 20
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0].old, 10)
        self.assertEqual(changes[0].new, 20)
        self.assertEqual(changes[0].name, "price")

    def test_watch_not_fired_same_value(self):
        calls = []

        @auto_properties
        class Cart(QObject):
            def __init__(self):
                super().__init__()
                self.price = 10

            @watch("price")
            def on_price(self, chg):
                calls.append(chg)

        cart = Cart()
        cart.price = 10  # same value
        self.assertEqual(len(calls), 0)

    def test_effect(self):
        fired = []

        @auto_properties
        class Item(QObject):
            def __init__(self):
                super().__init__()
                self.value = 0

            @effect("value")
            def on_value(self):
                fired.append(self.value)

        item = Item()
        item.value = 5
        self.assertEqual(fired, [5])

    def test_computed(self):
        @auto_properties
        class Cart(QObject):
            def __init__(self):
                super().__init__()
                self.price = 10
                self.quantity = 2

            @computed("price", "quantity")
            def total(self):
                return self.price * self.quantity

        cart = Cart()
        self.assertEqual(cart.total, 20)
        cart.price = 5
        self.assertEqual(cart.total, 10)


class NativePropertyConversionTest(unittest.TestCase):
    """Native @property declarations are converted to Q_PROPERTYs."""

    def test_readwrite_property_converted(self):
        changes = []

        @auto_properties
        class Item(QObject):
            def __init__(self):
                super().__init__()
                self._price = 0

            @property
            def price(self) -> int:
                return self._price

            @price.setter
            def price(self, value):
                self._price = value

            @watch("price")
            def on_price(self, chg: Change):
                changes.append(chg)

        # Converted to a PySide Property (a Q_PROPERTY).
        self.assertIsInstance(Item.__dict__["price"], Property)
        item = Item()
        item.price = 7
        self.assertEqual(item.price, 7)
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0].new, 7)
        # Writable through the QML path too.
        self.assertTrue(item.setProperty("price", 9))
        self.assertEqual(item.property("price"), 9)

    def test_readonly_property_raises_on_write(self):
        @auto_properties
        class Item(QObject):
            def __init__(self):
                super().__init__()
                self._value = 3

            @property
            def value(self) -> int:
                return self._value

        item = Item()
        self.assertEqual(item.value, 3)
        # A getter-only Q_PROPERTY cannot be written (QML or meta path).
        self.assertFalse(item.setProperty("value", 99))
        self.assertEqual(item.property("value"), 3)


class ExistingPropertyTest(unittest.TestCase):
    """Existing PySide Property declarations are respected, not rebuilt."""

    def test_observers_wired_without_double_emit(self):
        changes = []
        emitted = []

        @auto_properties
        class Item(QObject):
            priceChanged = Signal()

            def __init__(self):
                super().__init__()
                self._price = 0

            def _get_price(self):
                return self._price

            def _set_price(self, value):
                if value != self._price:
                    self._price = value
                    self.priceChanged.emit()

            price = Property(int, _get_price, _set_price, notify=priceChanged)

            @watch("price")
            def on_price(self, chg: Change):
                changes.append(chg)

        item = Item()
        item.priceChanged.connect(lambda: emitted.append(1))
        item.price = 42
        self.assertEqual(item.price, 42)
        self.assertEqual(len(changes), 1)        # observer fired
        self.assertEqual(changes[0].new, 42)
        self.assertEqual(len(emitted), 1)        # notify emitted exactly once

    def test_property_without_observers_untouched(self):
        @auto_properties
        class Item(QObject):
            valueChanged = Signal()

            def __init__(self):
                super().__init__()
                self._value = 1

            def _get(self):
                return self._value

            def _set(self, v):
                self._value = v
                self.valueChanged.emit()

            value = Property(int, _get, _set, notify=valueChanged)

        item = Item()
        item.value = 5
        self.assertEqual(item.value, 5)


@QmlElement
@auto_properties
class QmlCart(QObject):
    """The intended use: an @auto_properties type instantiated from QML.

    @auto_properties must run first (inner decorator) so the generated
    Q_PROPERTYs and notify signals are in the QMetaObject before
    @QmlElement registers the type with the QML engine.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.price = 10
        self.quantity = 2
        QmlCart.last_watch = None

    @computed("price", "quantity")
    def total(self) -> int:
        return self.price * self.quantity

    @watch("price")
    def on_price(self, chg: Change):
        QmlCart.last_watch = chg


class AutoPropertiesFromQmlTest(unittest.TestCase):
    """Instantiate an @auto_properties type from QML (the intended path).

    Exercises the full QML round trip: the generated properties must be
    creatable and settable from QML, and @computed must notify QML bindings.
    """

    @classmethod
    def setUpClass(cls):
        cls.app = QGuiApplication.instance() or QGuiApplication([])

    def _build(self, qml: bytes):
        engine = QQmlEngine()
        component = QQmlComponent(engine)
        component.setData(qml, QUrl())
        self.assertEqual(component.status(), QQmlComponent.Status.Ready,
                         component.errorString())
        root = component.create()
        self.assertIsNotNone(root)
        # Keep engine/component alive for the lifetime of root.
        root._engine = engine
        root._component = component
        return root

    def test_properties_are_visible_and_settable_from_qml(self):
        """QML can set generated properties at creation time."""
        root = self._build(
            b"import QmlFeaturesTest 1.0\n"
            b"QmlCart { price: 7; quantity: 3 }\n")
        self.assertEqual(root.property("price"), 7)
        self.assertEqual(root.property("quantity"), 3)
        self.assertEqual(root.property("total"), 21)

    def test_computed_notifies_qml_binding(self):
        """A QML binding on a @computed property re-evaluates on change."""
        root = self._build(
            b"import QmlFeaturesTest 1.0\n"
            b"QmlCart {\n"
            b"    price: 10\n"
            b"    quantity: 3\n"
            b"    property int mirroredTotal: total\n"
            b"}\n")
        self.assertEqual(root.property("mirroredTotal"), 30)

        # Write through the meta-property system, exactly as a QML
        # assignment does; the computed binding must refresh.
        root.setProperty("price", 5)
        self.assertEqual(root.property("total"), 15)
        self.assertEqual(root.property("mirroredTotal"), 15)
        # The Python-side @watch observer also fired on the QML write.
        self.assertIsNotNone(QmlCart.last_watch)
        self.assertEqual(QmlCart.last_watch.new, 5)


if __name__ == "__main__":
    unittest.main()
