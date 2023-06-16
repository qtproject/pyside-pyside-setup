# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import sys

from import_inheritance import (get_inheritance_entries_by_import,
                                InheritanceException)
from json_inheritance import (is_inheritance_from_json_enabled,
                              get_inheritance_entries_from_json)


TEST_DRIVER_USAGE = """Usage: inheritance_graph.py [module] [class]

Example:
python inheritance_graph.py  PySide6.QtWidgets PySide6.QtWidgets.QWizard
"""


class InheritanceGraph(object):
    """
    Given a list of classes, determines the set of classes that they inherit
    from all the way to the root "object", and then is able to generate a
    graphviz dot graph from them.
    """
    def __init__(self, class_names, currmodule, builtins=None, show_builtins=False, parts=0):
        """
        *class_names* is a list of child classes to show bases from.

        If *show_builtins* is True, then Python builtins will be shown
        in the graph.
        """
        self.class_names = class_names
        if is_inheritance_from_json_enabled():
            self.class_info = get_inheritance_entries_from_json(class_names)
        else:
            self.class_info = get_inheritance_entries_by_import(class_names,
                                                                currmodule,
                                                                builtins,
                                                                show_builtins,
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


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(TEST_DRIVER_USAGE)
        sys.exit(-1)
    module = sys.argv[1]
    class_names = sys.argv[2:]
    graph = InheritanceGraph(class_names, module)
    dot = graph.generate_dot("test")
    print(dot)
