import ast
import textwrap
import unittest

import sort_imports

from cStringIO import StringIO

def sort_str(source):
    tree = ast.parse(source)
    s = sort_imports.ImportSorter()
    s.visit(tree)
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


