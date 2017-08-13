import unittest
import ast

from tested.languages.python2.functions import FunctionType
from tested.languages.python2.inferred_types import TypeSet, UnknownType

class TestFunctionType(unittest.TestCase):
    def testCreateFromSimpleNode(self):
        node = ast.parse('def f(a, b):\n    """Sample docstring"""\n    pass')
        f = FunctionType.fromASTNode(node.body[0])
        self.assertEqual(f.args,['a','b'])
        self.assertEqual(f.docstring,"Sample docstring")
        self.assertEqual(f.returns,TypeSet(UnknownType("return")))
