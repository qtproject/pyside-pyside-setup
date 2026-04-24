// Copyright (C) 2025 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef PYSIDE_PROPERTYBASE_P_H
#define PYSIDE_PROPERTYBASE_P_H

#include <sbkpython.h>

#include <pysidemacros.h>

#include <QtCore/qbytearray.h>
#include <QtCore/qtclasshelpermacros.h>
#include <QtCore/qflags.h>
#include <QtCore/qmetaobject.h>

struct PySideProperty;

namespace PySide::Property {

enum class PropertyFlag {
    Readable    = 0x001,
    Writable    = 0x002,
    Resettable  = 0x004,
    Designable  = 0x008,
    Scriptable  = 0x010,
    Stored      = 0x020,
    User        = 0x040,
    Constant    = 0x080,
    Final       = 0x100,
    Virtual     = 0x200,
    Override    = 0x400
};
Q_DECLARE_FLAGS(PropertyFlags, PropertyFlag)

} // namespace PySide::Property

// Base class for meta-callable properties (Normal properties, QmlListProperty)
class PYSIDE_API PySidePropertyBase
{
public:
    PySidePropertyBase &operator=(const PySidePropertyBase &) = delete;
    PySidePropertyBase(PySidePropertyBase &&) = delete;
    PySidePropertyBase &operator=(PySidePropertyBase &&) = delete;

    enum class Type : unsigned char { Property, ListProperty };

    virtual ~PySidePropertyBase() = default;

    // For handling decorator like "@property.getter"
    [[nodiscard]] virtual PySidePropertyBase *clone() const;

    virtual void metaCall(PyObject *source, QMetaObject::Call call, void **args) = 0;

    [[nodiscard]] Type type() const { return m_type; }

    [[nodiscard]] const QByteArray &typeName() const { return m_typeName; }
    void setTypeName(const QByteArray &newTypeName) { m_typeName = newTypeName; }

    [[nodiscard]] PyObject *pyTypeObject() const { return m_pyTypeObject; }
    void setPyTypeObject(PyObject *pt)  { m_pyTypeObject = pt; }

    [[nodiscard]] PyObject *notify() const { return m_notify; }
    void setNotify(PyObject *n) { m_notify = n; }

    [[nodiscard]] const QByteArray &notifySignature() const { return m_notifySignature; }
    void setNotifySignature(const QByteArray &s) { m_notifySignature = s; }

    [[nodiscard]] const QByteArray &doc() const { return m_doc; }
    void setDoc(const QByteArray &doc) { m_doc = doc; }

    [[nodiscard]] PySide::Property::PropertyFlags flags() const { return m_flags; }
    void setFlags(PySide::Property::PropertyFlags f) { m_flags = f; }
    void setFlag(PySide::Property::PropertyFlag f) { m_flags.setFlag(f); }

    static bool assignCheckCallable(PyObject *source, const char *name, PyObject **target);

protected:
    explicit PySidePropertyBase(Type t);
    PySidePropertyBase(const PySidePropertyBase &rhs);

    void tp_clearBase();
    int tp_traverseBase(visitproc visit, void *arg);
    void increfBase();

private:
    QByteArray m_typeName;
    // Type object: A real PyTypeObject ("@Property(int)") or a string
    // "@Property('QVariant')".
    PyObject *m_pyTypeObject = nullptr;
    PyObject *m_notify = nullptr;
    QByteArray m_notifySignature;
    QByteArray m_doc;
    PySide::Property::PropertyFlags m_flags;
    Type m_type;
};

#endif // PYSIDE_PROPERTYBASE_P_H
