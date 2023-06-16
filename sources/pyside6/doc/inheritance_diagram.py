# -*- coding: utf-8 -*-
r"""
    sphinx.ext.inheritance_diagram
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Defines a docutils directive for inserting inheritance diagrams.

    Provide the directive with one or more classes or modules (separated
    by whitespace).  For modules, all of the classes in that module will
    be used.

    Example::

       Given the following classes:

       class A: pass
       class B(A): pass
       class C(A): pass
       class D(B, C): pass
       class E(B): pass

       .. inheritance-diagram: D E

       Produces a graph like the following:

                   A
                  / \
                 B   C
                / \ /
               E   D

    The graph is inserted as a PNG+image map into HTML and a PDF in
    LaTeX.

    :copyright: Copyright 2007-2011 by the Sphinx team, see AUTHORS.
    :copyright: Copyright 2010-2011 by the PySide team.
    :license: BSD, see LICENSE for details.
"""

import sys
try:
    from hashlib import md5
except ImportError:
    from md5 import md5

from docutils import nodes
from docutils.parsers.rst import directives, Directive

from sphinx.ext.graphviz import render_dot_html, render_dot_latex

from inheritance_graph import InheritanceGraph
from import_inheritance import (get_inheritance_entries_by_import,
                                InheritanceException)
from json_inheritance import (is_inheritance_from_json_enabled,
                              get_inheritance_entries_from_json)


class inheritance_diagram(nodes.General, nodes.Element):
    """
    A docutils node to use as a placeholder for the inheritance diagram.
    """
    pass


class InheritanceDiagram(Directive):
    """
    Run when the inheritance_diagram directive is first encountered.
    """
    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        'parts': directives.nonnegative_int,
    }

    def run(self):
        node = inheritance_diagram()
        node.document = self.state.document
        env = self.state.document.settings.env
        class_names = self.arguments[0].split()
        class_role = env.get_domain('py').role('class')
        # Store the original content for use as a hash
        node['parts'] = self.options.get('parts', 0)
        node['content'] = ', '.join(class_names)

        # Create a graph starting with the list of classes
        try:
            graph = InheritanceGraph(
                class_names, env.temp_data.get('py:module'),
                __builtins__, parts=node['parts'])
        except InheritanceException as err:
            return [node.document.reporter.warning(err.args[0],
                                                   line=self.lineno)]

        # Create xref nodes for each target of the graph's image map and
        # add them to the doc tree so that Sphinx can resolve the
        # references to real URLs later.  These nodes will eventually be
        # removed from the doctree after we're done with them.
        for name in graph.get_all_class_names():
            refnodes, x = class_role('class', f':class:`{name}`', name,
                                     0, self.state)
            node.extend(refnodes)
        # Store the graph object so we can use it to generate the
        # dot file later
        node['graph'] = graph
        return [node]


def get_graph_hash(node):
    hashString = node['content'] + str(node['parts'])
    return md5(hashString.encode('utf-8')).hexdigest()[-10:]


def fix_class_name(name):
    """Fix duplicated modules 'PySide6.QtCore.PySide6.QtCore.QObject'"""
    mod_pos = name.rfind('.PySide')
    return name[mod_pos + 1:] if mod_pos != -1 else name


def expand_ref_uri(uri):
    """Fix a ref URI like 'QObject.html#PySide6.QtCore.PySide6.QtCore.QObject'
       to point from the image directory back to the HTML directory."""
    anchor_pos = uri.find('#')
    if anchor_pos == -1:
        return uri
    # Determine the path from the anchor "#PySide6.QtCore.PySide6.QtCore.QObject"
    class_name = fix_class_name(uri[anchor_pos + 1:])
    path = '../'
    modules = class_name.split('.')
    for m in range(min(2, len(modules))):
        path += f'{modules[m]}/'
    return path + uri[:anchor_pos]  # Strip anchor


def html_visit_inheritance_diagram(self, node):
    """
    Output the graph for HTML.  This will insert a PNG with clickable
    image map.
    """
    graph = node['graph']

    graph_hash = get_graph_hash(node)
    name = f'inheritance{graph_hash}'

    # Create a mapping from fully-qualified class names to URLs.
    urls = {}
    for child in node:
        ref_title = child.get('reftitle')
        uri = child.get('refuri')
        if uri and ref_title:
            urls[fix_class_name(ref_title)] = expand_ref_uri(uri)

    dotcode = graph.generate_dot(name, urls, env=self.builder.env)
    render_dot_html(self, node, dotcode, {}, 'inheritance', 'inheritance',
                    alt='Inheritance diagram of ' + node['content'])
    raise nodes.SkipNode


def latex_visit_inheritance_diagram(self, node):
    """
    Output the graph for LaTeX.  This will insert a PDF.
    """
    graph = node['graph']

    graph_hash = get_graph_hash(node)
    name = f'inheritance{graph_hash}'

    dotcode = graph.generate_dot(name, env=self.builder.env,
                                 graph_attrs={'size': '"6.0,6.0"'})
    render_dot_latex(self, node, dotcode, {}, 'inheritance')
    raise nodes.SkipNode


def skip(self, node):
    raise nodes.SkipNode


def setup(app):
    app.setup_extension('sphinx.ext.graphviz')
    app.add_node(
        inheritance_diagram,
        latex=(latex_visit_inheritance_diagram, None),
        html=(html_visit_inheritance_diagram, None),
        text=(skip, None),
        man=(skip, None))
    app.add_directive('inheritance-diagram', InheritanceDiagram)
    app.add_config_value('inheritance_graph_attrs', {}, False),
    app.add_config_value('inheritance_node_attrs', {}, False),
    app.add_config_value('inheritance_edge_attrs', {}, False),
