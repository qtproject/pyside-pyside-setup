/****************************************************************************
**
** Copyright (C) 2016 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:GPL-EXCEPT$
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** GNU General Public License Usage
** Alternatively, this file may be used under the terms of the GNU
** General Public License version 3 as published by the Free Software
** Foundation with exceptions as appearing in the file LICENSE.GPL3-EXCEPT
** included in the packaging of this file. Please review the following
** information to ensure the GNU General Public License requirements will
** be met: https://www.gnu.org/licenses/gpl-3.0.html.
**
** $QT_END_LICENSE$
**
****************************************************************************/

#ifndef OVERLOADDATA_H
#define OVERLOADDATA_H

#include <apiextractorresult.h>
#include <abstractmetaargument.h>

#include <QtCore/QBitArray>
#include <QtCore/QList>
#include <QtCore/QSharedPointer>

QT_FORWARD_DECLARE_CLASS(QDebug)
QT_FORWARD_DECLARE_CLASS(QTextStream)

class OverloadDataNode;
using OverloadDataNodePtr = QSharedPointer<OverloadDataNode>;
using OverloadDataList = QList<OverloadDataNodePtr>;

/// The root node of OverloadData. It contains all functions
class OverloadDataRootNode
{
public:
    virtual ~OverloadDataRootNode();

    OverloadDataRootNode(const OverloadDataRootNode &) = delete;
    OverloadDataRootNode &operator=(const OverloadDataRootNode &) = delete;
    OverloadDataRootNode(OverloadDataRootNode &&) = delete;
    OverloadDataRootNode &operator=(OverloadDataRootNode &&) = delete;

    virtual int argPos() const { return -1; }
    virtual const OverloadDataRootNode *parent() const { return nullptr; }

    bool isRoot() const { return parent() == nullptr; }

    AbstractMetaFunctionCPtr referenceFunction() const;

    const AbstractMetaFunctionCList &overloads() const { return m_overloads; }
    const OverloadDataList &children() const { return m_children; }

    bool nextArgumentHasDefaultValue() const;

    /// Returns the function that has a default value at the current OverloadData argument position, otherwise returns null.
    AbstractMetaFunctionCPtr getFunctionWithDefaultValue() const;

    /// Returns the nearest occurrence, including this instance, of an argument with a default value.
    const OverloadDataRootNode *findNextArgWithDefault();
    bool isFinalOccurrence(const AbstractMetaFunctionCPtr &func) const;

    int functionNumber(const AbstractMetaFunctionCPtr &func) const;

#ifndef QT_NO_DEBUG_STREAM
    virtual void formatDebug(QDebug &d) const;
#endif

    OverloadDataNode *addOverloadDataNode(const AbstractMetaFunctionCPtr &func,
                                          const AbstractMetaArgument &arg);

protected:
    OverloadDataRootNode(const AbstractMetaFunctionCList &o= {});

    void dumpRootGraph(QTextStream &s, int minArgs, int maxArgs) const;
    void sortNextOverloads(const ApiExtractorResult &api);


#ifndef QT_NO_DEBUG_STREAM
    void formatReferenceFunction(QDebug &d) const;
    void formatOverloads(QDebug &d) const;
    void formatNextOverloadData(QDebug &d) const;
#endif

    AbstractMetaFunctionCList m_overloads;
    OverloadDataList m_children;
};

/// OverloadDataNode references an argument/type combination.
class OverloadDataNode : public OverloadDataRootNode
{
public:
    explicit OverloadDataNode(const AbstractMetaFunctionCPtr &func,
                              OverloadDataRootNode *parent,
                              const AbstractMetaArgument &arg, int argPos,
                              const QString argTypeReplaced = {});
    void addOverload(const AbstractMetaFunctionCPtr &func);

    int argPos() const override { return m_argPos; }
    const OverloadDataRootNode *parent() const override;
    void dumpNodeGraph(QTextStream &s) const;

    const AbstractMetaArgument &argument() const
    {  return m_argument; }
    const AbstractMetaType &argType() const { return m_argument.type(); }

    bool hasArgumentTypeReplace() const { return !m_argTypeReplaced.isEmpty(); }
    const QString &argumentTypeReplaced() const { return m_argTypeReplaced; }

    const AbstractMetaArgument *overloadArgument(const AbstractMetaFunctionCPtr &func) const;

#ifndef QT_NO_DEBUG_STREAM
    void formatDebug(QDebug &d) const override;
#endif

private:
    AbstractMetaArgument m_argument;
    QString m_argTypeReplaced;
    OverloadDataRootNode *m_parent = nullptr;

    int m_argPos = -1; // Position excluding modified/removed arguments.
};

class OverloadData : public OverloadDataRootNode
{
public:
    explicit OverloadData(const AbstractMetaFunctionCList &overloads,
                          const ApiExtractorResult &api);

    int minArgs() const { return m_minArgs; }
    int maxArgs() const { return m_maxArgs; }

    /// Returns true if any of the overloads for the current OverloadData has a return type different from void.
    bool hasNonVoidReturnType() const;

    /// Returns true if any of the overloads for the current OverloadData has a varargs argument.
    bool hasVarargs() const;

    /// Returns true if any of the overloads for the current OverloadData is static.
    bool hasStaticFunction() const;

    /// Returns true if any of the overloads passed as argument is static.
    static bool hasStaticFunction(const AbstractMetaFunctionCList &overloads);

    /// Returns true if any of the overloads for the current OverloadData is classmethod.
    bool hasClassMethod() const;

    /// Returns true if any of the overloads passed as argument is classmethod.
    static bool hasClassMethod(const AbstractMetaFunctionCList &overloads);

    /// Returns true if any of the overloads for the current OverloadData is not static.
    bool hasInstanceFunction() const;

    /// Returns true if any of the overloads passed as argument is not static.
    static bool hasInstanceFunction(const AbstractMetaFunctionCList &overloads);

    /// Returns true if among the overloads for the current OverloadData there are static and non-static methods altogether.
    bool hasStaticAndInstanceFunctions() const;

    /// Returns true if among the overloads passed as argument there are static and non-static methods altogether.
    static bool hasStaticAndInstanceFunctions(const AbstractMetaFunctionCList &overloads);

    QList<int> invalidArgumentLengths() const;

    static int numberOfRemovedArguments(const AbstractMetaFunctionCPtr &func);
    static int numberOfRemovedArguments(const AbstractMetaFunctionCPtr &func, int finalArgPos);
    /// Returns true if all overloads have no more than one argument.
    static bool isSingleArgument(const AbstractMetaFunctionCList &overloads);

    void dumpGraph(const QString &filename) const;
    QString dumpGraph() const;
    bool showGraph() const;

    /// Returns true if a list of arguments is used (METH_VARARGS)
    bool pythonFunctionWrapperUsesListOfArguments() const;

    bool hasArgumentWithDefaultValue() const;
    static bool hasArgumentWithDefaultValue(const AbstractMetaFunctionCPtr &func);

    /// Returns a list of function arguments which have default values and were not removed.
    static AbstractMetaArgumentList getArgumentsWithDefaultValues(const AbstractMetaFunctionCPtr &func);

#ifndef QT_NO_DEBUG_STREAM
    void formatDebug(QDebug &) const override;
#endif

private:
    int m_minArgs = 256;
    int m_maxArgs = 0;
};

#ifndef QT_NO_DEBUG_STREAM
QDebug operator<<(QDebug, const OverloadData &);
#endif

#endif // OVERLOADDATA_H
