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

#include <abstractmetafunction.h>
#include <apiextractorresult.h>
#include <abstractmetalang.h>
#include <dotview.h>
#include <reporthandler.h>
#include <typesystem.h>
#include <graph.h>
#include "overloaddata.h"
#include "messages.h"
#include "ctypenames.h"
#include "pytypenames.h"
#include "textstream.h"
#include "exception.h"
#include "messages.h"

#include <QtCore/QDir>
#include <QtCore/QFile>
#include <QtCore/QTemporaryFile>

#include <algorithm>
#include <utility>

static QString getTypeName(const AbstractMetaType &type)
{
    const TypeEntry *typeEntry = type.typeEntry();
    if (typeEntry->isPrimitive())
        typeEntry = typeEntry->asPrimitive()->basicReferencedTypeEntry();
    QString typeName = typeEntry->name();
    if (typeEntry->isContainer()) {
        QStringList types;
        for (const auto &cType : type.instantiations()) {
            const TypeEntry *typeEntry = cType.typeEntry();
            if (typeEntry->isPrimitive())
                typeEntry = typeEntry->asPrimitive()->basicReferencedTypeEntry();
            types << typeEntry->name();
        }
        typeName += QLatin1Char('<') + types.join(QLatin1Char(',')) + QLatin1String(" >");
    }
    return typeName;
}

static bool typesAreEqual(const AbstractMetaType &typeA, const AbstractMetaType &typeB)
{
    if (typeA.typeEntry() == typeB.typeEntry()) {
        if (typeA.isContainer() || typeA.isSmartPointer()) {
            if (typeA.instantiations().size() != typeB.instantiations().size())
                return false;

            for (int i = 0; i < typeA.instantiations().size(); ++i) {
                if (!typesAreEqual(typeA.instantiations().at(i), typeB.instantiations().at(i)))
                    return false;
            }
            return true;
        }

        return !(typeA.isCString() ^ typeB.isCString());
    }
    return false;
}

/**
 * Helper function that returns the name of a container get from containerType argument and
 * an instantiation taken either from an implicit conversion expressed by the function argument,
 * or from the string argument implicitConvTypeName.
 */
static QString getImplicitConversionTypeName(const AbstractMetaType &containerType,
                                             const AbstractMetaType &instantiation,
                                             const AbstractMetaFunctionCPtr &function,
                                             const QString &implicitConvTypeName = QString())
{
    QString impConv;
    if (!implicitConvTypeName.isEmpty())
        impConv = implicitConvTypeName;
    else if (function->isConversionOperator())
        impConv = function->ownerClass()->typeEntry()->name();
    else
        impConv = getTypeName(function->arguments().constFirst().type());

    QStringList types;
    for (const auto &otherType : containerType.instantiations())
        types << (otherType == instantiation ? impConv : getTypeName(otherType));

    return containerType.typeEntry()->qualifiedCppName() + QLatin1Char('<')
           + types.join(QLatin1String(", ")) + QLatin1String(" >");
}

static inline int overloadNumber(const OverloadDataNodePtr &o)
{
    return o->referenceFunction()->overloadNumber();
}

static bool sortByOverloadNumberModification(OverloadDataList &list)
{
    if (std::all_of(list.cbegin(), list.cend(),
                    [](const OverloadDataNodePtr &o) { return overloadNumber(o) == TypeSystem::OverloadNumberDefault; })) {
        return false;
    }
    std::stable_sort(list.begin(), list.end(),
                     [] (const OverloadDataNodePtr &o1, const OverloadDataNodePtr &o2) {
                         return overloadNumber(o1) < overloadNumber(o2);
                     });
    return true;
}

using OverloadGraph = Graph<QString>;

/**
 * Topologically sort the overloads by implicit convertion order
 *
 * This avoids using an implicit conversion if there's an explicit
 * overload for the convertible type. So, if there's an implicit convert
 * like TargetType(ConvertibleType foo) and both are in the overload list,
 * ConvertibleType is checked before TargetType.
 *
 * Side effects: Modifies m_nextOverloadData
 */
void OverloadDataRootNode::sortNextOverloads(const ApiExtractorResult &api)
{
    QHash<QString, OverloadDataList> typeToOverloads;

    bool checkPyObject = false;
    bool checkPySequence = false;
    bool checkQString = false;
    bool checkQVariant = false;
    bool checkPyBuffer = false;

    // Primitive types that are not int, long, short,
    // char and their respective unsigned counterparts.
    static const QStringList nonIntegerPrimitives{floatT(), doubleT(), boolT()};

    // Signed integer primitive types.
    static const QStringList signedIntegerPrimitives{intT(), shortT(), longT(), longLongT()};

    // sort the children overloads
    for (const auto &ov : qAsConst(m_children))
        ov->sortNextOverloads(api);

    if (m_children.size() <= 1 || sortByOverloadNumberModification(m_children))
        return;

    // Populates the OverloadSortData object containing map and reverseMap, to map type names to ids,
    // these ids will be used by the topological sort algorithm, because is easier and faster to work
    // with graph sorting using integers.

    OverloadGraph graph;
    for (const auto &ov : qAsConst(m_children)) {
        const QString typeName = getTypeName(ov->modifiedArgType());
        auto it = typeToOverloads.find(typeName);
        if (it == typeToOverloads.end()) {
            typeToOverloads.insert(typeName, {ov});
            graph.addNode(typeName);
        } else {
            it.value().append(ov);
        }

        if (!checkPyObject && typeName == cPyObjectT())
            checkPyObject = true;
        else if (!checkPySequence && typeName == cPySequenceT())
            checkPySequence = true;
        else if (!checkPyBuffer && typeName == cPyBufferT())
            checkPyBuffer = true;
        else if (!checkQVariant && typeName == qVariantT())
            checkQVariant = true;
        else if (!checkQString && typeName == qStringT())
            checkQString = true;

        for (const auto &instantiation : ov->argType().instantiations()) {
            // Add dependencies for type instantiation of container.
            graph.addNode(getTypeName(instantiation));

            // Build dependency for implicit conversion types instantiations for base container.
            // For example, considering signatures "method(list<PointF>)" and "method(list<Point>)",
            // and being PointF implicitly convertible from Point, an list<T> instantiation with T
            // as Point must come before the PointF instantiation, or else list<Point> will never
            // be called. In the case of primitive types, list<double> must come before list<int>.
            if (instantiation.isPrimitive() && (signedIntegerPrimitives.contains(instantiation.name()))) {
                for (const QString &primitive : qAsConst(nonIntegerPrimitives))
                    graph.addNode(getImplicitConversionTypeName(ov->argType(), instantiation, nullptr, primitive));
            } else {
                const auto &funcs = api.implicitConversions(instantiation);
                for (const auto &function : funcs)
                    graph.addNode(getImplicitConversionTypeName(ov->argType(), instantiation, function));
            }
        }
    }


    // Create the graph of type dependencies based on implicit conversions.
    // All C++ primitive types, add any forgotten type AT THE END OF THIS LIST!
    static const QStringList primitiveTypes{intT(), unsignedIntT(), longT(), unsignedLongT(),
        shortT(), unsignedShortT(), boolT(), unsignedCharT(), charT(), floatT(),
        doubleT(), constCharPtrT()};

    QStringList foundPrimitiveTypeIds;
    for (const auto &p : primitiveTypes) {
        if (graph.hasNode(p))
            foundPrimitiveTypeIds.append(p);
    }

    if (checkPySequence && checkPyObject)
        graph.addEdge(cPySequenceT(), cPyObjectT());

    QStringList classesWithIntegerImplicitConversion;

    AbstractMetaFunctionCList involvedConversions;

    for (const auto &ov : qAsConst(m_children)) {
        const AbstractMetaType &targetType = ov->argType();
        const QString targetTypeEntryName = getTypeName(ov->modifiedArgType());

        // Process implicit conversions
        const auto &functions = api.implicitConversions(targetType);
        for (const auto &function : functions) {
            QString convertibleType;
            if (function->isConversionOperator())
                convertibleType = function->ownerClass()->typeEntry()->name();
            else
                convertibleType = getTypeName(function->arguments().constFirst().type());

            if (convertibleType == intT() || convertibleType == unsignedIntT())
                classesWithIntegerImplicitConversion << targetTypeEntryName;

            if (!graph.hasNode(convertibleType))
                continue;

            // If a reverse pair already exists, remove it. Probably due to the
            // container check (This happened to QVariant and QHash)
            graph.removeEdge(targetTypeEntryName, convertibleType);
            graph.addEdge(convertibleType, targetTypeEntryName);
            involvedConversions.append(function);
        }

        // Process inheritance relationships
        if (targetType.isValue() || targetType.isObject()) {
            auto *te = targetType.typeEntry();
            auto metaClass = AbstractMetaClass::findClass(api.classes(), te);
            if (!metaClass)
                throw Exception(msgArgumentClassNotFound(m_overloads.constFirst(), te));
            const AbstractMetaClassList &ancestors = metaClass->allTypeSystemAncestors();
            for (const AbstractMetaClass *ancestor : ancestors) {
                QString ancestorTypeName = ancestor->typeEntry()->name();
                if (!graph.hasNode(ancestorTypeName))
                    continue;
                graph.removeEdge(ancestorTypeName, targetTypeEntryName);
                graph.addEdge(targetTypeEntryName, ancestorTypeName);
            }
        }

        // Process template instantiations
        for (const auto &instantiation : targetType.instantiations()) {
            const QString convertible = getTypeName(instantiation);
            if (graph.hasNode(convertible)) {
                if (!graph.containsEdge(targetTypeEntryName, convertible)) // Avoid cyclic dependency.
                    graph.addEdge(convertible, targetTypeEntryName);

                if (instantiation.isPrimitive() && (signedIntegerPrimitives.contains(instantiation.name()))) {
                    for (const QString &primitive : qAsConst(nonIntegerPrimitives)) {
                        QString convertibleTypeName =
                            getImplicitConversionTypeName(ov->argType(), instantiation, nullptr, primitive);
                        // Avoid cyclic dependency.
                        if (!graph.containsEdge(targetTypeEntryName, convertibleTypeName))
                            graph.addEdge(convertibleTypeName, targetTypeEntryName);
                    }

                } else {
                    const auto &funcs = api.implicitConversions(instantiation);
                    for (const auto &function : funcs) {
                        QString convertibleTypeName =
                            getImplicitConversionTypeName(ov->argType(), instantiation, function);
                        // Avoid cyclic dependency.
                        if (!graph.containsEdge(targetTypeEntryName, convertibleTypeName)) {
                            graph.addEdge(convertibleTypeName, targetTypeEntryName);
                            involvedConversions.append(function);
                        }
                    }
                }
            }
        }


        if ((checkPySequence || checkPyObject || checkPyBuffer)
            && !targetTypeEntryName.contains(cPyObjectT())
            && !targetTypeEntryName.contains(cPyBufferT())
            && !targetTypeEntryName.contains(cPySequenceT())) {
            if (checkPySequence) {
                // PySequence will be checked after all more specific types, but before PyObject.
                graph.addEdge(targetTypeEntryName, cPySequenceT());
            } else if (checkPyBuffer) {
                // PySequence will be checked after all more specific types, but before PyObject.
                graph.addEdge(targetTypeEntryName, cPyBufferT());
            } else {
                // Add dependency on PyObject, so its check is the last one (too generic).
                graph.addEdge(targetTypeEntryName, cPyObjectT());
            }
        } else if (checkQVariant && targetTypeEntryName != qVariantT()) {
            if (!graph.containsEdge(qVariantT(), targetTypeEntryName)) // Avoid cyclic dependency.
                graph.addEdge(targetTypeEntryName, qVariantT());
        } else if (checkQString && ov->argType().isPointer()
            && targetTypeEntryName != qStringT()
            && targetTypeEntryName != qByteArrayT()
            && (!checkPyObject || targetTypeEntryName != cPyObjectT())) {
            if (!graph.containsEdge(qStringT(), targetTypeEntryName)) // Avoid cyclic dependency.
                graph.addEdge(targetTypeEntryName, qStringT());
        }

        if (targetType.isEnum()) {
            // Enum values must precede primitive types.
            for (const auto &id : foundPrimitiveTypeIds)
                graph.addEdge(targetTypeEntryName, id);
        }
    }

    // QByteArray args need to be checked after QString args
    if (graph.hasNode(qStringT()) && graph.hasNode(qByteArrayT()))
        graph.addEdge(qStringT(), qByteArrayT());

    for (const auto &ov : qAsConst(m_children)) {
        const AbstractMetaType &targetType = ov->argType();
        if (!targetType.isEnum())
            continue;

        QString targetTypeEntryName = getTypeName(targetType);
        // Enum values must precede types implicitly convertible from "int" or "unsigned int".
        for (const QString &implicitFromInt : qAsConst(classesWithIntegerImplicitConversion))
            graph.addEdge(targetTypeEntryName, implicitFromInt);
    }


    // Special case for double(int i) (not tracked by m_generator->implicitConversions
    for (const QString &signedIntegerName : qAsConst(signedIntegerPrimitives)) {
        if (graph.hasNode(signedIntegerName)) {
            for (const QString &nonIntegerName : qAsConst(nonIntegerPrimitives)) {
                if (graph.hasNode(nonIntegerName))
                    graph.addEdge(nonIntegerName, signedIntegerName);
            }
        }
    }

    // sort the overloads topologically based on the dependency graph.
    const auto unmappedResult = graph.topologicalSort();
    if (!unmappedResult.isValid()) {
        QString funcName = referenceFunction()->name();
        if (auto owner = referenceFunction()->ownerClass())
            funcName.prepend(owner->name() + QLatin1Char('.'));

        // Dump overload graph
        QString graphName = QDir::tempPath() + QLatin1Char('/') + funcName + QLatin1String(".dot");
        graph.dumpDot(graphName, [] (const QString &n) { return n; });
        AbstractMetaFunctionCList cyclic;
        for (const auto &typeName : unmappedResult.cyclic) {
            const auto oit = typeToOverloads.constFind(typeName);
            if (oit != typeToOverloads.cend())
                cyclic.append(oit.value().constFirst()->referenceFunction());
        }
        qCWarning(lcShiboken, "%s", qPrintable(msgCyclicDependency(funcName, graphName, cyclic, involvedConversions)));
    }

    m_children.clear();
    for (const auto &typeName : unmappedResult.result) {
        const auto oit = typeToOverloads.constFind(typeName);
        if (oit != typeToOverloads.cend()) {
            std::copy(oit.value().crbegin(), oit.value().crend(),
                      std::back_inserter(m_children));
        }
    }
}

// Determine the minimum (first default argument)/maximum arguments (size)
// of a function (taking into account the removed arguments).
static std::pair<int, int> getMinMaxArgs(const AbstractMetaFunctionCPtr &func)
{
    int defaultValueIndex = -1;
    const auto &arguments = func->arguments();
    int argIndex = 0;
    for (qsizetype i = 0, size = arguments.size(); i < size; ++i) {
        const auto &arg =  arguments.at(i);
        if (!arg.isModifiedRemoved()) {
            if (defaultValueIndex < 0 && arg.hasDefaultValueExpression())
                defaultValueIndex = argIndex;
            ++argIndex;
        }
    }
    const int maxArgs = argIndex;
    const int minArgs = defaultValueIndex >= 0 ? defaultValueIndex : maxArgs;
    return {minArgs, maxArgs};
}

const OverloadDataRootNode *OverloadDataNode::parent() const
{
    return m_parent;
}

/**
 * Root constructor for OverloadData
 *
 * This constructor receives the list of overloads for a given function and iterates generating
 * the graph of OverloadData instances. Each OverloadDataNode instance references an argument/type
 * combination.
 *
 * Example:
 *      addStuff(double, PyObject *)
 *      addStuff(double, int)
 *
 * Given these two overloads, there will be the following graph:
 *
 *   addStuff - double - PyObject *
 *                    \- int
 *
 */
OverloadData::OverloadData(const AbstractMetaFunctionCList &overloads,
                           const ApiExtractorResult &api) :
    OverloadDataRootNode(overloads)
{
    for (const auto &func : overloads) {
        const auto minMaxArgs = getMinMaxArgs(func);
        if (minMaxArgs.first < m_minArgs)
            m_minArgs = minMaxArgs.first;
        if (minMaxArgs.second > m_maxArgs)
            m_maxArgs = minMaxArgs.second;
        OverloadDataRootNode *currentOverloadData = this;
        const AbstractMetaArgumentList &arguments = func->arguments();
        for (const AbstractMetaArgument &arg : arguments) {
            if (!arg.isModifiedRemoved())
                currentOverloadData = currentOverloadData->addOverloadDataNode(func, arg);
        }
    }

    // Sort the overload possibilities so that the overload decisor code goes for the most
    // important cases first, based on the topological order of the implicit conversions
    sortNextOverloads(api);
}

OverloadDataNode::OverloadDataNode(const AbstractMetaFunctionCPtr &func,
                                   OverloadDataRootNode *parent,
                                   const AbstractMetaArgument &argument,
                                   int argPos,
                                   const QString argTypeReplaced) :
      m_argument(argument),
      m_argTypeReplaced(argTypeReplaced),
      m_parent(parent),
      m_argPos(argPos)
{
    if (func)
        this->addOverload(func);
}

void OverloadDataNode::addOverload(const AbstractMetaFunctionCPtr &func)
{
    m_overloads.append(func);
}

OverloadDataNode *OverloadDataRootNode::addOverloadDataNode(const AbstractMetaFunctionCPtr &func,
                                                            const AbstractMetaArgument &arg)
{
    OverloadDataNodePtr overloadData;
    if (!func->isOperatorOverload()) {
        for (const auto &tmp : qAsConst(m_children)) {
            // TODO: 'const char *', 'char *' and 'char' will have the same TypeEntry?

            // If an argument have a type replacement, then we should create a new overloaddata
            // for it, unless the next argument also have a identical type replacement.
            if (typesAreEqual(tmp->modifiedArgType(), arg.modifiedType())) {
                tmp->addOverload(func);
                overloadData = tmp;
            }
        }
    }

    if (overloadData.isNull()) {
        const int argpos = argPos() + 1;
        overloadData.reset(new OverloadDataNode(func, this, arg, argpos));
        m_children.append(overloadData);
    }

    return overloadData.data();
}

bool OverloadData::hasNonVoidReturnType() const
{
    for (const auto &func : m_overloads) {
        if (func->isTypeModified()) {
            if (func->modifiedTypeName() != u"void")
                return true;
        } else {
            if (!func->argumentRemoved(0) && !func->type().isVoid())
                return true;
        }
    }
    return false;
}

bool OverloadData::hasVarargs() const
{
    for (const auto &func : m_overloads) {
        AbstractMetaArgumentList args = func->arguments();
        if (args.size() > 1 && args.constLast().type().isVarargs())
            return true;
    }
    return false;
}

bool OverloadData::hasStaticFunction(const AbstractMetaFunctionCList &overloads)
{
    for (const auto &func : overloads) {
        if (func->isStatic())
            return true;
    }
    return false;
}

bool OverloadData::hasStaticFunction() const
{
    for (const auto &func : m_overloads) {
        if (func->isStatic())
            return true;
    }
    return false;
}

bool OverloadData::hasClassMethod(const AbstractMetaFunctionCList &overloads)
{
    for (const auto &func : overloads) {
        if (func->isClassMethod())
            return true;
    }
    return false;
}

bool OverloadData::hasClassMethod() const
{
    for (const auto &func : m_overloads) {
        if (func->isClassMethod())
            return true;
    }
    return false;
}

bool OverloadData::hasInstanceFunction(const AbstractMetaFunctionCList &overloads)
{
    for (const auto &func : overloads) {
        if (!func->isStatic())
            return true;
    }
    return false;
}

bool OverloadData::hasInstanceFunction() const
{
    for (const auto &func : m_overloads) {
        if (!func->isStatic())
            return true;
    }
    return false;
}

bool OverloadData::hasStaticAndInstanceFunctions(const AbstractMetaFunctionCList &overloads)
{
    return OverloadData::hasStaticFunction(overloads) && OverloadData::hasInstanceFunction(overloads);
}

bool OverloadData::hasStaticAndInstanceFunctions() const
{
    return OverloadData::hasStaticFunction() && OverloadData::hasInstanceFunction();
}

OverloadDataRootNode::OverloadDataRootNode(const AbstractMetaFunctionCList &o) :
    m_overloads(o)
{
}

OverloadDataRootNode::~OverloadDataRootNode() = default;

AbstractMetaFunctionCPtr OverloadDataRootNode::referenceFunction() const
{
    return m_overloads.constFirst();
}

const AbstractMetaArgument *OverloadDataNode::overloadArgument(const AbstractMetaFunctionCPtr &func) const
{
    if (isRoot() || !m_overloads.contains(func))
        return nullptr;

    int argPos = 0;
    int removed = 0;
    for (int i = 0; argPos <= m_argPos; i++) {
        if (func->arguments().at(i).isModifiedRemoved())
            removed++;
        else
            argPos++;
    }

    return &func->arguments().at(m_argPos + removed);
}

bool OverloadDataRootNode::nextArgumentHasDefaultValue() const
{
    for (const auto &overloadData : m_children) {
        if (!overloadData->getFunctionWithDefaultValue().isNull())
            return true;
    }
    return false;
}

static const OverloadDataRootNode *_findNextArgWithDefault(const OverloadDataRootNode *overloadData)
{
    if (!overloadData->getFunctionWithDefaultValue().isNull())
        return overloadData;

    const OverloadDataRootNode *result = nullptr;
    const OverloadDataList &data = overloadData->children();
    for (const auto &odata : data) {
        const auto *tmp = _findNextArgWithDefault(odata.data());
        if (!result || (tmp && result->argPos() > tmp->argPos()))
            result = tmp;
    }
    return result;
}

const OverloadDataRootNode *OverloadDataRootNode::findNextArgWithDefault()
{
    return _findNextArgWithDefault(this);
}

bool OverloadDataRootNode::isFinalOccurrence(const AbstractMetaFunctionCPtr &func) const
{
    for (const auto &pd : m_children) {
        if (pd->overloads().contains(func))
            return false;
    }
    return true;
}

AbstractMetaFunctionCPtr OverloadDataRootNode::getFunctionWithDefaultValue() const
{
    const int argpos = argPos();
    for (const auto &func : m_overloads) {
        int removedArgs = 0;
        for (int i = 0; i <= argpos + removedArgs; i++) {
            if (func->arguments().at(i).isModifiedRemoved())
                removedArgs++;
        }
        if (func->arguments().at(argpos + removedArgs).hasDefaultValueExpression())
            return func;
    }
    return {};
}

QList<int> OverloadData::invalidArgumentLengths() const
{
    QSet<int> validArgLengths;

    for (const auto &func : m_overloads) {
        const AbstractMetaArgumentList args = func->arguments();
        int offset = 0;
        for (int i = 0; i < args.size(); ++i) {
            if (func->arguments().at(i).isModifiedRemoved()) {
                offset++;
            } else {
                if (args.at(i).hasDefaultValueExpression())
                    validArgLengths << i-offset;
            }
        }
        validArgLengths << args.size() - offset;
    }

    QList<int> invalidArgLengths;
    for (int i = m_minArgs + 1; i < m_maxArgs; i++) {
        if (!validArgLengths.contains(i))
            invalidArgLengths.append(i);
    }

    return invalidArgLengths;
}

int OverloadData::numberOfRemovedArguments(const AbstractMetaFunctionCPtr &func)
{
    return std::count_if(func->arguments().cbegin(), func->arguments().cend(),
                         [](const AbstractMetaArgument &a) { return a.isModifiedRemoved(); });
}

int OverloadData::numberOfRemovedArguments(const AbstractMetaFunctionCPtr &func, int finalArgPos)
{
    Q_ASSERT(finalArgPos >= 0);
    int removed = 0;
    const int size = func->arguments().size();
    for (int i = 0; i < qMin(size, finalArgPos + removed); ++i) {
        if (func->arguments().at(i).isModifiedRemoved())
            ++removed;
    }
    return removed;
}

void OverloadData::dumpGraph(const QString &filename) const
{
    QFile file(filename);
    if (file.open(QFile::WriteOnly)) {
        QTextStream s(&file);
        dumpRootGraph(s, m_minArgs, m_maxArgs);
    }
}

QString OverloadData::dumpGraph() const
{
    QString result;
    QTextStream s(&result);
    dumpRootGraph(s, m_minArgs, m_maxArgs);
    return result;
}

bool OverloadData::showGraph() const
{
    return showDotGraph(referenceFunction()->name(), dumpGraph());
}

static inline QString toHtml(QString s)
{
    s.replace(QLatin1Char('<'), QLatin1String("&lt;"));
    s.replace(QLatin1Char('>'), QLatin1String("&gt;"));
    s.replace(QLatin1Char('&'), QLatin1String("&amp;"));
    return s;
}

void OverloadDataRootNode::dumpRootGraph(QTextStream &s, int minArgs, int maxArgs) const
{
    const auto rfunc = referenceFunction();
    s << "digraph OverloadedFunction {\n";
    s << "    graph [fontsize=12 fontname=freemono labelloc=t splines=true overlap=false rankdir=LR];\n";

    // Shows all function signatures
    s << "legend [fontsize=9 fontname=freemono shape=rect label=\"";
    for (const auto &func : m_overloads) {
        s << "f" << functionNumber(func) << " : "
            << toHtml(func->type().cppSignature())
            << ' ' << toHtml(func->minimalSignature()) << "\\l";
    }
    s << "\"];\n";

    // Function box title
    s << "    \"" << rfunc->name() << "\" [shape=plaintext style=\"filled,bold\" margin=0 fontname=freemono fillcolor=white penwidth=1 ";
    s << "label=<<table border=\"0\" cellborder=\"0\" cellpadding=\"3\" bgcolor=\"white\">";
    s << "<tr><td bgcolor=\"black\" align=\"center\" cellpadding=\"6\" colspan=\"2\"><font color=\"white\">";
    if (rfunc->ownerClass())
        s << rfunc->ownerClass()->name() << "::";
    s << toHtml(rfunc->name()) << "</font>";
    if (rfunc->isVirtual()) {
        s << "<br/><font color=\"white\" point-size=\"10\">&lt;&lt;";
        if (rfunc->isAbstract())
            s << "pure ";
        s << "virtual&gt;&gt;</font>";
    }
    s << "</td></tr>";

    // Function return type
    s << "<tr><td bgcolor=\"gray\" align=\"right\">original type</td><td bgcolor=\"gray\" align=\"left\">"
        << toHtml(rfunc->type().cppSignature())
        << "</td></tr>";

    // Shows type changes for all function signatures
    for (const auto &func : m_overloads) {
        if (!func->isTypeModified())
            continue;
        s << "<tr><td bgcolor=\"gray\" align=\"right\">f" << functionNumber(func);
        s << "-type</td><td bgcolor=\"gray\" align=\"left\">";
        s << toHtml(func->modifiedTypeName()) << "</td></tr>";
    }

    // Minimum and maximum number of arguments
    s << "<tr><td bgcolor=\"gray\" align=\"right\">minArgs</td><td bgcolor=\"gray\" align=\"left\">";
    s << minArgs << "</td></tr>";
    s << "<tr><td bgcolor=\"gray\" align=\"right\">maxArgs</td><td bgcolor=\"gray\" align=\"left\">";
    s << maxArgs << "</td></tr>";

    if (rfunc->ownerClass()) {
        if (rfunc->implementingClass() != rfunc->ownerClass())
            s << "<tr><td align=\"right\">implementor</td><td align=\"left\">" << rfunc->implementingClass()->name() << "</td></tr>";
        if (rfunc->declaringClass() != rfunc->ownerClass() && rfunc->declaringClass() != rfunc->implementingClass())
            s << "<tr><td align=\"right\">declarator</td><td align=\"left\">" << rfunc->declaringClass()->name() << "</td></tr>";
    }

    // Overloads for the signature to present point
    s << "<tr><td bgcolor=\"gray\" align=\"right\">overloads</td><td bgcolor=\"gray\" align=\"left\">";
    for (const auto &func : m_overloads)
        s << 'f' << functionNumber(func) << ' ';
    s << "</td></tr>";

    s << "</table>> ];\n";

    for (const auto &pd : m_children) {
        s << "    \""  << rfunc->name() << "\" -> ";
        pd->dumpNodeGraph(s);
    }

    s << "}\n";
}

void OverloadDataNode::dumpNodeGraph(QTextStream &s) const
{
    QString argId = QLatin1String("arg_") + QString::number(quintptr(this));
    s << argId << ";\n";

    s << "    \"" << argId << "\" [shape=\"plaintext\" style=\"filled,bold\" margin=\"0\" fontname=\"freemono\" fillcolor=\"white\" penwidth=1 ";
    s << "label=<<table border=\"0\" cellborder=\"0\" cellpadding=\"3\" bgcolor=\"white\">";

    // Argument box title
    s << "<tr><td bgcolor=\"black\" align=\"left\" cellpadding=\"2\" colspan=\"2\">";
    s << "<font color=\"white\" point-size=\"11\">arg #" << argPos() << "</font></td></tr>";

    // Argument type information
    const QString type = modifiedArgType().cppSignature();
    s << "<tr><td bgcolor=\"gray\" align=\"right\">type</td><td bgcolor=\"gray\" align=\"left\">";
    s << toHtml(type) << "</td></tr>";
    if (isTypeModified()) {
        s << "<tr><td bgcolor=\"gray\" align=\"right\">orig. type</td><td bgcolor=\"gray\" align=\"left\">";
        s << toHtml(argType().cppSignature()) << "</td></tr>";
    }

    const OverloadDataRootNode *root = this;
    while (!root->isRoot())
        root = root->parent();

    // Overloads for the signature to present point
    s << "<tr><td bgcolor=\"gray\" align=\"right\">overloads</td><td bgcolor=\"gray\" align=\"left\">";
    for (const auto &func : m_overloads)
        s << 'f' << root->functionNumber(func) << ' ';
    s << "</td></tr>";

    // Show default values (original and modified) for various functions
    for (const auto &func : m_overloads) {
        const AbstractMetaArgument *arg = overloadArgument(func);
        if (!arg)
            continue;
        const int n = root->functionNumber(func);
        QString argDefault = arg->defaultValueExpression();
        if (!argDefault.isEmpty() ||
            argDefault != arg->originalDefaultValueExpression()) {
            s << "<tr><td bgcolor=\"gray\" align=\"right\">f" << n;
            s << "-default</td><td bgcolor=\"gray\" align=\"left\">";
            s << argDefault << "</td></tr>";
        }
        if (argDefault != arg->originalDefaultValueExpression()) {
            s << "<tr><td bgcolor=\"gray\" align=\"right\">f" << n;
            s << "-orig-default</td><td bgcolor=\"gray\" align=\"left\">";
            s << arg->originalDefaultValueExpression() << "</td></tr>";
        }
    }

    s << "</table>>];\n";

    for (const auto &pd : m_children) {
        s << "    " << argId << " -> ";
        pd->dumpNodeGraph(s);
    }
}

int OverloadDataRootNode::functionNumber(const AbstractMetaFunctionCPtr &func) const
{
    return m_overloads.indexOf(func);
}

bool OverloadData::pythonFunctionWrapperUsesListOfArguments() const
{
    auto referenceFunction = m_overloads.constFirst();
    if (referenceFunction->isCallOperator())
        return true;
    if (referenceFunction->isOperatorOverload())
        return false;
    const int maxArgs = this->maxArgs();
    const int minArgs = this->minArgs();
    return (minArgs != maxArgs)
           || (maxArgs > 1)
           || referenceFunction->isConstructor()
           || hasArgumentWithDefaultValue();
}

bool OverloadData::hasArgumentWithDefaultValue() const
{
    if (maxArgs() == 0)
        return false;
    for (const auto &func : m_overloads) {
        if (hasArgumentWithDefaultValue(func))
            return true;
    }
    return false;
}

bool OverloadData::hasArgumentWithDefaultValue(const AbstractMetaFunctionCPtr &func)
{
    const AbstractMetaArgumentList &arguments = func->arguments();
    for (const AbstractMetaArgument &arg : arguments) {
        if (!arg.isModifiedRemoved() && arg.hasDefaultValueExpression())
            return true;
    }
    return false;
}

AbstractMetaArgumentList OverloadData::getArgumentsWithDefaultValues(const AbstractMetaFunctionCPtr &func)
{
    AbstractMetaArgumentList args;
    const AbstractMetaArgumentList &arguments = func->arguments();
    for (const AbstractMetaArgument &arg : arguments) {
        if (!arg.hasDefaultValueExpression()
            || arg.isModifiedRemoved())
            continue;
        args << arg;
    }
    return args;
}

#ifndef QT_NO_DEBUG_STREAM

void OverloadDataRootNode::formatReferenceFunction(QDebug &d) const
{
    auto refFunc = referenceFunction();
    d << '"';
    if (auto owner = refFunc->ownerClass())
        d << owner->qualifiedCppName() << "::";
    d << refFunc->minimalSignature() << '"';
    if (m_overloads.constFirst()->isReverseOperator())
        d << " [reverseop]";
}

void OverloadDataRootNode::formatOverloads(QDebug &d) const
{
    const qsizetype count = m_overloads.size();
    d << ", overloads[" << count << ']';
    if (count < 2)
        return;
    d << "=(";
    for (int i = 0; i < count; ++i) {
        if (i)
            d << '\n';
        d << m_overloads.at(i)->signature();
    }
    d << ')';
}

void OverloadDataRootNode::formatNextOverloadData(QDebug &d) const
{
    const qsizetype count = m_children.size();
    d << ", next[" << count << ']';
    if (d.verbosity() >= 3) {
        d << "=(";
        for (int i = 0; i < count; ++i) {
            if (i)
                d << '\n';
            m_children.at(i)->formatDebug(d);
        }
        d << ')';
    }
}

void OverloadDataRootNode::formatDebug(QDebug &d) const
{
    formatReferenceFunction(d);
    formatOverloads(d);
    formatNextOverloadData(d);
}

void OverloadDataNode::formatDebug(QDebug &d) const
{
    d << "OverloadDataNode(";
    formatReferenceFunction(d);
    d << ", argPos=" << m_argPos;
    if (m_argument.argumentIndex() != m_argPos)
        d << ", argIndex=" << m_argument.argumentIndex();
    d << ", argType=\"" << m_argument.type().cppSignature() << '"';
    if (isTypeModified())
        d << ", modifiedArgType=\"" << modifiedArgType().cppSignature() << '"';
    formatOverloads(d);
    formatNextOverloadData(d);
    d << ')';
}

void OverloadData::formatDebug(QDebug &d) const
{
    d << "OverloadData(";
    formatReferenceFunction(d);
    d << ", minArgs=" << m_minArgs << ", maxArgs=" << m_maxArgs;
    formatOverloads(d);
    formatNextOverloadData(d);
    d << ')';
}

QDebug operator<<(QDebug d, const OverloadData &od)
{
    QDebugStateSaver saver(d);
    d.noquote();
    d.nospace();
    od.formatDebug(d);
    return d;
}
#endif // !QT_NO_DEBUG_STREAM
