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

from import_inheritance import (get_inheritance_entries_by_import,
                                InheritanceException)


class InheritanceGraph(object):
    """
    Given a list of classes, determines the set of classes that they inherit
    from all the way to the root "object", and then is able to generate a
    graphviz dot graph from them.
    """
    def __init__(self, class_names, currmodule, show_builtins=False, parts=0):
        """
        *class_names* is a list of child classes to show bases from.

        If *show_builtins* is True, then Python builtins will be shown
        in the graph.
        """
        self.class_names = class_names
        self.class_info = get_inheritance_entries_by_import(class_names, currmodule,
                                                            __builtins__, show_builtins,
                                                            parts)

    def get_all_class_names(self):
        """
        Get all of the class names involved in the graph.
        """
        return [fullname for (_, fullname, _) in self.class_info]

    # These are the default attrs for graphviz
    default_graph_attrs = {
        'rankdir': 'LR',
        'size': '"8.0, 12.0"',
    }
    default_node_attrs = {
        'shape': 'box',
        'fontsize': 10,
        'height': 0.25,
        'fontname': '"Vera Sans, DejaVu Sans, Liberation Sans, '
                    'Arial, Helvetica, sans"',
        'style': '"setlinewidth(0.5)"',
    }
    default_edge_attrs = {
        'arrowsize': 0.5,
        'style': '"setlinewidth(0.5)"',
    }

    def _format_node_attrs(self, attrs):
        return ','.join([f'{x[0]}={x[1]}' for x in attrs.items()])

    def _format_graph_attrs(self, attrs):
        return ''.join([f"{x[0]}={x[1]};\n" for x in attrs.items()])

    def generate_dot(self, name, urls={}, env=None,
                     graph_attrs={}, node_attrs={}, edge_attrs={}):
        """
        Generate a graphviz dot graph from the classes that
        were passed in to __init__.

        *name* is the name of the graph.

        *urls* is a dictionary mapping class names to HTTP URLs.

        *graph_attrs*, *node_attrs*, *edge_attrs* are dictionaries containing
        key/value pairs to pass on as graphviz properties.
        """
        g_attrs = self.default_graph_attrs.copy()
        n_attrs = self.default_node_attrs.copy()
        e_attrs = self.default_edge_attrs.copy()
        g_attrs.update(graph_attrs)
        n_attrs.update(node_attrs)
        e_attrs.update(edge_attrs)
        if env:
            g_attrs.update(env.config.inheritance_graph_attrs)
            n_attrs.update(env.config.inheritance_node_attrs)
            e_attrs.update(env.config.inheritance_edge_attrs)

        res = []
        res.append(f'digraph {name} {{\n')
        res.append(self._format_graph_attrs(g_attrs))

        for name, fullname, bases in self.class_info:
            # Write the node
            this_node_attrs = n_attrs.copy()
            url = urls.get(fullname)
            if url is not None:
                this_node_attrs['URL'] = f'"{url}"'
                this_node_attrs['target'] = '"_top"'  # Browser target frame attribute (same page)
            attribute = self._format_node_attrs(this_node_attrs)
            res.append(f'  "{name}" [{attribute}];\n')

            # Write the edges
            for base_name in bases:
                attribute = self._format_node_attrs(e_attrs)
                res.append(f'  "{base_name}" -> "{name}" [{attribute}];\n')
        res.append('}\n')
        return ''.join(res)


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
                parts=node['parts'])
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
