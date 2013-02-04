


import ast
import sys
from collections import defaultdict
import distutils.sysconfig as sysconfig
import os
import re, keyword, tokenize

def isidentifier(value):
    if value in keyword.kwlist:
        return False
    return re.match('^' + tokenize.Name  + '$', value, re.I) is not None

class ImportVisitor(ast.NodeVisitor):
    """
    This class visits all the import nodes at the root of tree
    and generates new import nodes that are sorted according to the Google
    and PEP8 coding guidelines.

    In practice this means that they are sorted according to this tuple.

        (stdlib, site_packages, names)

    Before that happens though we group by type (Import/FromImport) and sort
    the names within the import.

    This means things like

        import sys, os

    become

        import os, sys

    And

        from sys import path, args

    become

        from sys import args, path
    """

    def __init__(self):
        self.imports = set()
        self.from_imports = defaultdict(set)
        self.stdlibs = set(self.iter_stdlibs()) | set(['sys'])
        self.site_packages = set()

    def visit_Import(self, node):
        if node.col_offset != 0:
            return
        else:
            # collect all the import names together in a big set.
            self.imports.update((nm.name, nm.asname) for nm in node.names)
    def visit_ImportFrom(self, node):
        # we need to group the names imported from each module
        # into single from X import N,M,P,... groups so we store the names
        # and regenerate the node when we find more
        # we'll then insert this into the full imports chain when we're done
        if node.col_offset != 0:
            return
        else:
            self.from_imports[(node.level, node.module)].update((nm.name, nm.asname) for nm in node.names)

    def sorted_nodes(self):
        nodes = []

        # first turn all the from imports back into proper nodes
        for (level, module), names in self.from_imports.iteritems():
            node = ast.ImportFrom(
                module=module,
                names=[ast.alias(name=nm, asname=asnm)
                       for nm, asnm in sorted(names)],
                level=level
            )
            nodes.append(node)

        for nm, asnm in self.imports:
            node = ast.Import(names=[ast.alias(name=nm, asname=asnm)])
            nodes.append(node)

        nodes.sort(key=self._node_sort_key)

        wraplen = 79
        for node in nodes:
            if isinstance(node, ast.Import):
                print "import %s" % node.names[0].name
            elif isinstance(node, ast.ImportFrom):
                from_line = "from %s import" % (node.module or '.' * node.level)
                name_lines = []
                for name in node.names:
                    if name.asname:
                        name = "%s as %s" % (name.name, name.asname)
                    else:
                        name = name.name

                    if (
                        not name_lines or
                        len(name) + 4 +
                        sum(len(n) for n in name_lines[-1]) +
                        (2 * len(name_lines[-1])) > wraplen
                    ):
                        name_lines.append([name])
                    else:
                        name_lines[-1].append(name)

                if len(name_lines) > 1:
                    from_line += ' (\n   '

                print from_line,
                print '\n    '.join(', '.join(ln) for ln in name_lines)

                if len(name_lines) > 1:
                    print ')'

    def _node_sort_key(self, node):
        if isinstance(node, ast.Import):
            module = node.names[0].name
        elif isinstance(node, ast.ImportFrom):
            module = node.module
        else:
            raise TypeError(node)

        key = [True, True, module]

        if module:
            key[2] = module
            p = ast.parse(module)
            for node in ast.walk(p):
                if isinstance(node, ast.Name):
                    if node.id in self.stdlibs:
                        key[0] = False
                    elif node.id in self.site_packages:
                        key[1] = False
                    break
        else:
            key[2] = node.level

        return key

    @classmethod
    def iter_stdlibs(cls):
        """
        Find quite a lot of stdlib.
        Some things like os.path can't be found this way. You actually need to
        *run* Python code to fully expand all valid import statements, so
        instead we're just going to rely on getting most of them and then only
        matching on the root of import statements the rest of the time.
        """
        def modules(path):
            for name in os.listdir(path):
                if name.endswith('.py') and isidentifier(name[:-3]):
                        yield name[:-3]

                elif os.path.isfile(os.path.join(path, name, '__init__.py')):
                    if isidentifier(name):
                        yield name

        stdlib_path = sysconfig.get_python_lib(standard_lib=True)
        return modules(stdlib_path)

tree = ast.parse(open(sys.argv[1]).read())

i = ImportVisitor()
i.visit(tree)
i.sorted_nodes()

