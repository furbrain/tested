import unittest
import ast

from tested.languages.python3.functions import FunctionType
from tested.languages.python3.inferred_types import TypeSet, UnknownType

class TestFunctionType(unittest.TestCase):
    def testCreateFromSimpleNode(self):
        node = ast.parse('def f(a, b):\n    """Sample docstring"""\n    pass')
        f = FunctionType.fromASTNode(node.body[0])
        self.assertEqual(f.args,['a','b'])
        self.assertEqual(f.docstring,"Sample docstring")
        self.assertEqual(f.returns,TypeSet(UnknownType("return")))
        
        
    def testSimpleReturnType(self):
        f = FunctionType('f', [], TypeSet(int), "")
        self.assertEqual(f.getReturnTypeSet([]),"int")
        
    def testMultpleReturnType(self):
        f = FunctionType('f', [], TypeSet(int, float), "")
        self.assertEqual(f.getReturnTypeSet([]),"float, int")
        
    def testContingentReturnType(self):
        f = FunctionType('f', ['a', 'b'], TypeSet(UnknownType('a')), "")
        self.assertEqual(f.getReturnTypeSet([TypeSet(int), TypeSet(float)]), "int")

        f = FunctionType('f', ['a', 'b'], TypeSet(UnknownType('b')), "")
        self.assertEqual(f.getReturnTypeSet([TypeSet(int), TypeSet(float)]), "float")
        
    def testContingentMultipleReturnType(self):
        f = FunctionType('f', ['a', 'b'], TypeSet(UnknownType('a'),UnknownType('b')), "")
        self.assertEqual(f.getReturnTypeSet([TypeSet(int), TypeSet(float)]), "float, int")

    def testBadlyMatchedArgsReturnType(self):
        f = FunctionType('f', ['a', 'b'], TypeSet(UnknownType('a')), "")
        self.assertEqual(f.getReturnTypeSet([TypeSet(int)]), "int")
    
        f = FunctionType('f', ['a'], TypeSet(UnknownType('a')), "")
        self.assertEqual(f.getReturnTypeSet([TypeSet(int), TypeSet(float)]), "int")

