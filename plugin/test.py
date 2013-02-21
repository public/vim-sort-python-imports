import ast
import textwrap
import unittest

import sort_imports

from cStringIO import StringIO

def visit(source):
    tree = ast.parse(source)
    s = sort_imports.ImportSorter()
    s.visit(tree)
    return s

def sort_str(source):
    s = visit(source)
    io = StringIO()
    s.print_sorted(io)
    return io.getvalue()


class TestSortImports(unittest.TestCase):

    def _test_transform(self, input, expected):
        sorted_source = sort_str(textwrap.dedent(input))
        self.assertEqual(
            sorted_source,
            textwrap.dedent(expected)
        )

    def test_check_order_1(self):
        source = textwrap.dedent("""\
        import a
        import c
        import b
        """)
        errors = visit(source).sort_errors()
        self.assertEqual(len(errors), 1)

    @unittest.expectedFailure
    def test_check_order_2(self):
        source = textwrap.dedent("""\
        from a import a
        from a import b
        from a import c
        """)
        errors = visit(source).sort_errors()
        self.assertEqual(len(errors), 1)

    @unittest.expectedFailure
    def test_check_order_3(self):
        source = textwrap.dedent("""\
        from a import c, b, a
        """)
        errors = visit(source).sort_errors()
        self.assertEqual(len(errors), 1)

    def test_our_imports(self):
        self._test_transform(
            """\
            import tokenize
            import sys
            import re
            import pkgutil
            import os
            import keyword
            import itertools
            import imp
            import distutils.sysconfig as sysconfig
            import ast
            from collections import defaultdict
            """,

            """\
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


            """
        )

    def test_sort_many(self):
        self._test_transform(
            """\
            from example import b
            from example import f
            from example import g
            from example import c, e, d
            from example import a

            import a
            import d
            import b
            import e, g, f
            import c
            """,
            """\
            import a
            import b
            import c
            import d
            import e
            from example import a
            from example import b
            from example import c
            from example import d
            from example import e
            from example import f
            from example import g
            import f
            import g


            """
        )

    def test_split_multiple_names_and_sort(self):
        self._test_transform(
            """\
            from example import b, a
            import example
            """,
            """\
            import example
            from example import a
            from example import b


            """
        )

    def test_stdlib_goes_first(self):
        self._test_transform(
            """\
            import example
            import os
            from sys import argv
            from example import a
            """,
            """\
            import os
            from sys import argv

            import example
            from example import a


            """
        )

    def test_relative_import(self):
        self._test_transform(
            """\
            from .. import example
            from . import example
            from ... import example
            """,
            """\
            from . import example
            from .. import example
            from ... import example


            """
        )

    def test_non_module_import_ignored(self):
        self._test_transform(
            """\
            import example
            def f():
                import func_example
            """,
            """\
            import example


            """
        )

    def test_remove_duplicates(self):
        self._test_transform(
            """\
            import example
            import example, example
            from example import a, a, b
            from example import b, b, a
            """,
            """\
            import example
            from example import a
            from example import b


            """
        )


