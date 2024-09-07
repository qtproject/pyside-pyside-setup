// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include <qtcorehelper.h>

#include <QtCore/qdebug.h>

QT_BEGIN_NAMESPACE

namespace QtCoreHelper {

// Data classes for the generic argument data classes. The argument is freed
// via QMetaType
class QGenericArgumentData
{
public:
    explicit QGenericArgumentData(const QMetaType &type, const void *aData) :
        m_type(type), m_argument(m_type.name(), aData)
    {
    }

    ~QGenericArgumentData()
    {
        if (m_type.isValid())
            m_type.destroy(m_argument.data());
    }

    const QMetaType m_type;
    const QGenericArgument m_argument;
};

class QGenericReturnArgumentData
{
public:
    explicit QGenericReturnArgumentData(const QMetaType &type, void *aData) :
          m_type(type), m_argument(m_type.name(), aData)
    {
    }

    ~QGenericReturnArgumentData()
    {
        if (m_type.isValid())
            m_type.destroy(m_argument.data());
    }

    const QMetaType m_type;
    const QGenericReturnArgument m_argument;
};

QGenericArgumentHolder::QGenericArgumentHolder()
{
}

QGenericArgumentHolder::QGenericArgumentHolder(const QMetaType &type, const void *aData) :
    d(std::make_shared<QGenericArgumentData>(type, aData))
{
}

QGenericArgumentHolder::QGenericArgumentHolder(const QGenericArgumentHolder &) = default;
QGenericArgumentHolder::QGenericArgumentHolder(QGenericArgumentHolder &&) = default;
QGenericArgumentHolder &QGenericArgumentHolder::operator=(const QGenericArgumentHolder &) = default;
QGenericArgumentHolder &QGenericArgumentHolder::operator=(QGenericArgumentHolder &&) = default;
QGenericArgumentHolder::~QGenericArgumentHolder() = default;

QGenericArgument QGenericArgumentHolder::toGenericArgument() const
{
    return d ? d->m_argument : QGenericArgument{};
}

QMetaType QGenericArgumentHolder::metaType() const
{
    return d ? d->m_type : QMetaType{};
}

const void *QGenericArgumentHolder::data() const
{
    return d ? d->m_argument.data() : nullptr;
}

QGenericReturnArgumentHolder::QGenericReturnArgumentHolder(const QMetaType &type, void *aData) :
      d(std::make_shared<QGenericReturnArgumentData>(type, aData))
{
}

QGenericReturnArgumentHolder::QGenericReturnArgumentHolder(const QGenericReturnArgumentHolder &) = default;
QGenericReturnArgumentHolder::QGenericReturnArgumentHolder(QGenericReturnArgumentHolder &&) = default;
QGenericReturnArgumentHolder &QGenericReturnArgumentHolder::operator=(const QGenericReturnArgumentHolder &) = default;
QGenericReturnArgumentHolder &QGenericReturnArgumentHolder::operator=(QGenericReturnArgumentHolder &&) = default;
QGenericReturnArgumentHolder::~QGenericReturnArgumentHolder() = default;

QGenericReturnArgument QGenericReturnArgumentHolder::toGenericReturnArgument() const
{
    return d->m_argument;
}

QMetaType QGenericReturnArgumentHolder::metaType() const
{
    return d->m_type;
}

const void *QGenericReturnArgumentHolder::data() const
{
    return d->m_argument.data();
}

// QDirListing::const_iterator has no copy semantics (shared internal state, QTBUG-125512).
// The Python iterable semantics (calling __next__() first before retrieving the first value)
// can therefore not be implemented as "return iterator++;". Wrap a helper class
// around it that does a no-op in the first call to __next__().
struct QDirListingIteratorPrivate
{
    enum State { First, Iterating, End };

    explicit QDirListingIteratorPrivate(const QDirListing &dl) :
        iterator(dl.cbegin()), state(First) {}
    QDirListingIteratorPrivate() : state(End) {}

    bool next();

    QDirListing::const_iterator iterator;
    State state;
};

inline bool QDirListingIteratorPrivate::next()
{
    switch (state) {
    case First:
        state = iterator != QDirListing::sentinel{} ? Iterating : End;
        break;
    case Iterating:
        if (++iterator == QDirListing::sentinel{})
            state = End;
        break;
    case End:
        break;
    }
    return state != End;
}

QDirListingIterator::QDirListingIterator(const QDirListing &dl) :
    d(std::make_shared<QDirListingIteratorPrivate>(dl))
{
}

QDirListingIterator::QDirListingIterator() :
    d(std::make_shared<QDirListingIteratorPrivate>())
{
}

QDirListingIterator::QDirListingIterator(const QDirListingIterator &) = default;
QDirListingIterator &QDirListingIterator::operator=(const QDirListingIterator &) = default;
QDirListingIterator::QDirListingIterator(QDirListingIterator &&) noexcept = default;
QDirListingIterator &QDirListingIterator::operator=(QDirListingIterator &&) noexcept = default;
QDirListingIterator::~QDirListingIterator() = default;

bool QDirListingIterator::next()
{
    return d->next();
}

const QDirListing::DirEntry &QDirListingIterator::value() const
{
    Q_ASSERT(d->state == QDirListingIteratorPrivate::Iterating);
    return *d->iterator;
}

bool QDirListingIterator::atEnd() const
{
    return d->state == QDirListingIteratorPrivate::End;
}

} // namespace QtCoreHelper

QT_END_NAMESPACE
