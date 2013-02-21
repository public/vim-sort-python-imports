import ast
from collections import defaultdict
import distutils.sysconfig as sysconfig
import imp
import itertools
import keyword
import os
import pkgutil
import re
import sys
import tokenize


def isidentifier(value):
    if value in keyword.kwlist:
        return False
    return re.match('^' + tokenize.Name + '$', value, re.I) is not None


class ImportSorter(ast.NodeVisitor):
    """
    This class visits all the import nodes at the root of tree
    and generates new import nodes that are sorted according to the Google
    and PEP8 coding guidelines.

    In practice this means that they are sorted according to this tuple.

        (stdlib, site_packages, names)

    We also make sure only 1 name is imported per import statement.
    """

    def __init__(self):
        self.original_nodes = []
        self.imports = set()
        self.from_imports = defaultdict(set)
        self.stdlibs = set(self.iter_stdlibs()) | set(sys.builtin_module_names)
        self.python_paths = [p for p in sys.path if p]

    @classmethod
    def iter_stdlibs(cls):
        """
        Find quite a lot of stdlib.
        Some things like os.path can't be found this way. You actually need to
        *run* Python code to fully expand all valid import statements, so
        instead we're just going to rely on getting most of them and then only
        matching on the root of import statements the rest of the time.
        """
        stdlib_path = sysconfig.get_python_lib(standard_lib=True)
        stdlib_paths = [
            path
            for path in sys.path
            if path.startswith(stdlib_path)
        ]
        return (nm for _, nm, _ in pkgutil.iter_modules(stdlib_paths))

    def visit_Import(self, node):
        if node.col_offset != 0:
            return
        else:
            # collect all the import names together in a big set.
            self.imports.update((nm.name, nm.asname) for nm in node.names)
            self.original_nodes.append(node)

    def visit_ImportFrom(self, node):
        # we need to group the names imported from each module
        # into single from X import N,M,P,... groups so we store the names
        # and regenerate the node when we find more
        # we'll then insert this into the full imports chain when we're done
        if node.col_offset != 0:
            return
        else:
            self.from_imports[(node.level, node.module)].update(
                (nm.name, nm.asname) for nm in node.names
            )
            self.original_nodes.append(node)

    def _node_sort_key(self, node):
        """
        Return a key that will sort the nodes in the correct
        order for the Google Code Style guidelines.
        """
        if isinstance(node, ast.Import):
            if node.names[0].asname:
                name = [node.names[0].name, node.names[0].asname]
            else:
                name = [node.names[0].name]
            from_names = None

        elif isinstance(node, ast.ImportFrom):
            name = [node.module]
            from_names = [nm.name for nm in node.names]
        else:
            raise TypeError(node)

        # stdlib, site package, name, is_fromimport, from_names
        key = [True, True, name, from_names]

        if not name[0]:
            key[2] = [node.level]
        else:
            name = [v.lower() for v in name]
            key[2] = name
            p = ast.parse(name[0])
            for n in ast.walk(p):
                if not isinstance(n, ast.Name):
                    continue

                if n.id in self.stdlibs:
                    key[0] = False
                else:
                    try:
                        key[1] = not imp.find_module(
                            n.id,
                            self.python_paths
                        )
                    except ImportError:
                        continue
        return key

    def new_nodes(self):
        nodes = []

        # first turn all the from imports back into proper nodes
        for (level, module), names in self.from_imports.iteritems():
            for nm, asnm in sorted(names):
                node = ast.ImportFrom(
                    module=module,
                    names=[ast.alias(name=nm, asname=asnm)],
                    level=level
                )
                nodes.append((self._node_sort_key(node), node))

        # then build the normal imports again
        for nm, asnm in self.imports:
            node = ast.Import(names=[ast.alias(name=nm, asname=asnm)])
            nodes.append((self._node_sort_key(node), node))

        return nodes

    def sorted_nodes(self):
        nodes = self.new_nodes()
        nodes.sort()
        return nodes

    def sort_errors(self):
        errors = []
        nodes = [(self._node_sort_key(n), n) for n in self.original_nodes]
        nodes_iter = iter(nodes[1:])
        for (a_k, a), (b_k, b) in itertools.izip(nodes, nodes_iter):
            if a_k > b_k:
                errors.append(((a_k, a), (b_k, b)))
        return errors

    def print_sorted(self, io=sys.stdout):
        nodes = self.sorted_nodes()

        pkey = None
        for key, node in nodes:
            # insert new lines between groups
            if pkey and key[:2] != pkey[:2]:
                print >>io
            pkey = key

            # names here will actually always only have 1 element in it
            # because we are only allowed 1 per line, but it's easy
            # enough to cope with multiple anyway.
            all_names = ', '.join(
                (' as '.join(nm for nm in (name.name, name.asname) if nm))
                for name in node.names
            )

            if isinstance(node, ast.Import):
                print >>io, "import %s" % all_names
            elif isinstance(node, ast.ImportFrom):
                print >>io, "from %s import %s" % (
                    node.module or '.' * node.level,
                    all_names
                )

        print >>io
        print >>io

        return nodes

if __name__ == '__main__':
    tree = ast.parse(open(sys.argv[1]).read())
    i = ImportSorter()
    i.visit(tree)
    i.print_sorted()
