// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef GRAPH_H
#define GRAPH_H

#include "dotview.h"

#include <QtCore/qdebug.h>
#include <QtCore/qfile.h>
#include <QtCore/qhash.h>
#include <QtCore/qlist.h>
#include <QtCore/qstring.h>
#include <QtCore/qtextstream.h>

#include <algorithm>

/// Result of topologically sorting of a graph (list of nodes in order
/// or list of nodes that have cyclic dependencies).
template <class Node>
struct GraphSortResult
{
    using NodeList = QList<Node>;

    bool isValid() const { return !result.isEmpty() && cyclic.isEmpty(); }
    void format(QDebug &debug) const;

    NodeList result;
    NodeList cyclic;
};

/// A graph that can have its nodes topologically sorted. The nodes need to
/// have operator==().
template <class Node>
class Graph
{
    using IndexList = QList<qsizetype>;

public:
    using NodeList = QList<Node>;

    Graph() = default;

    // Construct from a QList of nodes (unchecked, does not require operator==())
    explicit Graph(const NodeList &list) : m_nodes(list)
    {
        m_nodeEntries.resize(list.size());
    }

    // Construct from a sequence of nodes (checks for duplicated nodes using operator==())
    template<class It>
    explicit Graph(It i1, It i2)
    {
        const auto size = std::distance(i1, i2);
        m_nodes.reserve(size);
        m_nodeEntries.reserve(size);
        setNodes(i1, i2);
    }

    template<class It>
    void setNodes(It i1, It i2)
    {
        for (; i1 != i2; ++i1)
            addNode(*i1);
    }

    bool addNode(Node n);

    /// Returns whether node was registered
    bool hasNode(Node node) { return m_nodes.contains(node); }

    /// Returns the numbed of nodes in this graph.
    qsizetype nodeCount() const { return m_nodeEntries.size(); }

    /// Returns true if the graph contains the edge from -> to
    bool containsEdge(Node from, Node to) const;
    bool containsEdgeByIndexes(qsizetype fromIndex, qsizetype toIndex) const;
    /// Returns true if the graph has any edges
    bool hasEdges() const;

    /// Adds an edge to this graph.
    bool addEdge(Node from, Node to);
    bool addEdgeByIndexes(qsizetype fromIndex, qsizetype toIndex);
    /// Removes an edge from this graph.
    bool removeEdge(Node from, Node to);
    bool removeEdgeByIndexes(qsizetype fromIndex, qsizetype toIndex);
    /// Clears the graph
    void clear()
    {
        m_nodes.clear();
        m_nodeEntries.clear();
    }

    /// Dumps a dot graph to a file named \p filename.
    /// \param fileName file name where the output should be written.
    /// \param f function returning the name of a node
    template <class NameFunction>
    bool dumpDot(const QString& fileName, NameFunction nameFunction) const;
    template <class NameFunction>
    void formatDot(QTextStream &str, NameFunction nameFunction) const;
    template <class NameFunction>
    bool showGraph(const QString &name, NameFunction nameFunction) const;

    void format(QDebug &debug) const;

    /**
    *   Topologically sort this graph.
    *   \return A collection with all nodes topologically sorted or an empty collection if a cyclic
    *   dependency was found.
    */
    GraphSortResult<Node> topologicalSort() const;

private:
    enum Color : quint8 { WHITE, GRAY, BLACK };

    struct NodeEntry
    {
        IndexList targets;
        mutable Color color = WHITE;
    };

    Color colorAt(qsizetype i) const { return m_nodeEntries.at(i).color; }
    void depthFirstVisit(qsizetype i, IndexList *result) const;

    NodeList m_nodes;
    QList<NodeEntry> m_nodeEntries;
};

template <class Node>
bool Graph<Node>::addNode(Node n)
{
    if (hasNode(n))
        return false;
    m_nodes.append(n);
    m_nodeEntries.append(NodeEntry{});
    return true;
}

template <class Node>
void Graph<Node>::depthFirstVisit(qsizetype i, IndexList *result) const
{
    m_nodeEntries[i].color = GRAY;

    for (qsizetype toIndex : m_nodeEntries.at(i).targets) {
        switch (colorAt(toIndex)) {
        case WHITE:
            depthFirstVisit(toIndex, result);
            break;
        case GRAY:
            return; // This is not a DAG!
        case BLACK:
            break;
        }
    }

    m_nodeEntries[i].color = BLACK;

    result->append(i);
}

template <class Node>
GraphSortResult<Node> Graph<Node>::topologicalSort() const
{
    const qsizetype size = m_nodeEntries.size();

    GraphSortResult<Node> result;

    if (size > 1 && hasEdges()) {
        result.result.reserve(size);
        IndexList indexList;
        indexList.reserve(size);
        for (qsizetype i = 0; i < size; ++i)
            m_nodeEntries[i].color = WHITE;
        for (qsizetype i = 0; i < size; ++i)  {
            if (colorAt(i) == WHITE) // recursive calls may have set it to black
                depthFirstVisit(i, &indexList);
        }
        if (indexList.size() == size) { // Succeeded, all traversed
            for (qsizetype i = size - 1; i >= 0; --i)
                result.result.append(m_nodes.at(indexList.at(i)));
        } else { // Cyclic, Not a DAG!
            for (qsizetype i = 0; i < size; ++i) {
                if (!indexList.contains(i))
                    result.cyclic.append(m_nodes.at(i));
            }
        }
    } else { // no edges, shortcut. Legacy behavior: Also reverse in this case.
        result.result = m_nodes;
        std::reverse(result.result.begin(), result.result.end());
    }
    return result;
}

template <class Node>
bool Graph<Node>::containsEdge(Node from, Node to) const
{
    return containsEdgeByIndexes(m_nodes.indexOf(from), m_nodes.indexOf(to));
}

template <class Node>
bool Graph<Node>::containsEdgeByIndexes(qsizetype fromIndex, qsizetype toIndex) const
{
    return fromIndex >= 0 && fromIndex < m_nodeEntries.size()
        && m_nodeEntries.at(fromIndex).targets.contains(toIndex);
}

template <class Node>
bool Graph<Node>::hasEdges() const
{
    auto hashEdgesPred = [](const NodeEntry &nodeEntry) { return !nodeEntry.targets.isEmpty(); };
    return std::any_of(m_nodeEntries.cbegin(), m_nodeEntries.cend(), hashEdgesPred);
}

template <class Node>
bool Graph<Node>::addEdge(Node from, Node to)
{
    return addEdgeByIndexes(m_nodes.indexOf(from), m_nodes.indexOf(to));
}

template <class Node>
bool Graph<Node>::addEdgeByIndexes(qsizetype fromIndex, qsizetype toIndex)
{
    if (fromIndex < 0 || fromIndex >= m_nodeEntries.size()
        || toIndex < 0 || toIndex >= m_nodeEntries.size()
        || m_nodeEntries.at(fromIndex).targets.contains(toIndex)) {
        return false;
    }
    m_nodeEntries[fromIndex].targets.append(toIndex);
    return true;
}

template <class Node>
bool Graph<Node>::removeEdge(Node from, Node to)
{
    return removeEdgeByIndexes(m_nodes.indexOf(from), m_nodes.indexOf(to));
}

template <class Node>
bool Graph<Node>::removeEdgeByIndexes(qsizetype fromIndex, qsizetype toIndex)
{
    if (fromIndex < 0 || fromIndex >= m_nodeEntries.size()
        || toIndex < 0 || toIndex >= m_nodeEntries.size()) {
        return false;
    }
    auto &targets = m_nodeEntries[fromIndex].targets;
    const qsizetype toPos = targets.indexOf(toIndex);
    if (toPos == -1)
        return false;
    targets.removeAt(toPos);
    return true;
}

template <class Node>
template <class NameFunction>
bool Graph<Node>::dumpDot(const QString& fileName,
                          NameFunction nameFunction) const
{
    QFile output(fileName);
    if (!output.open(QIODevice::WriteOnly))
        return false;
    QTextStream s(&output);
    formatDot(s, nameFunction);
    return true;
}

template <class Node>
template <class NameFunction>
void Graph<Node>::formatDot(QTextStream &s,
                            NameFunction nameFunction) const
{
    s << "digraph D {\n";
    for (qsizetype i = 0, size = m_nodes.size(); i < size; ++i) {
        const auto &nodeEntry = m_nodeEntries.at(i);
        if (!nodeEntry.targets.isEmpty()) {
            const QString fromName = nameFunction(m_nodes.at(i));
            for (qsizetype i : nodeEntry.targets)
                s << '"' << fromName << "\" -> \"" << nameFunction(m_nodes.at(i)) << "\"\n";
        }
    }
    s << "}\n";
}

template <class Node>
template <class NameFunction>
bool Graph<Node>::showGraph(const QString &name, NameFunction nameFunction) const
{
    QString graph;
    QTextStream s(&graph);
    formatDot(s, nameFunction);
    return showDotGraph(name, graph);
}

template <class Node>
void Graph<Node>::format(QDebug &debug) const
{
    const qsizetype size = m_nodeEntries.size();
    debug << "nodes[" << size << "] = (";
    for (qsizetype i = 0; i < size; ++i) {
        const auto &nodeEntry = m_nodeEntries.at(i);
        if (i)
            debug << ", ";
        debug << m_nodes.at(i);
        if (!nodeEntry.targets.isEmpty()) {
            debug << " -> [";
            for (qsizetype t = 0, tsize = nodeEntry.targets.size(); t < tsize; ++t) {
                if (t)
                    debug << ", ";
                debug << m_nodes.at(nodeEntry.targets.at(t));
            }
            debug << ']';
        }
    }
    debug << ')';
}

template <class Node>
QDebug operator<<(QDebug debug, const Graph<Node> &g)
{
    QDebugStateSaver saver(debug);
    debug.noquote();
    debug.nospace();
    debug << "Graph(";
    g.format(debug);
    debug << ')';
    return debug;
}

template <class Node>
void GraphSortResult<Node>::format(QDebug &debug) const
{
    if (isValid())
        debug << "Valid, " << result;
    else
        debug << "Invalid, cyclic dependencies: " << cyclic;
}

template <class Node>
QDebug operator<<(QDebug debug, const GraphSortResult<Node> &r)
{
    QDebugStateSaver saver(debug);
    debug.noquote();
    debug.nospace();
    debug << "Graph::SortResult(";
    r.format(debug);
    debug << ')';
    return debug;
}

#endif // GRAPH_H
