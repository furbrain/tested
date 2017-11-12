import unittest
import tested.itypes.functions as functions
import tested.itypes.builtins as builtins
import tested.itypes.basics as basics

class TestFunctionType(unittest.TestCase):
    def setUp(self):
        self.int = builtins.get_type_by_name('<int>')
        self.str = builtins.get_type_by_name('<str>')
        self.float = builtins.get_type_by_name('<float>')

    @unittest.skip("should be elsewhere - needs moving")
    def testCreateFromSimpleNode(self):
        node = ast.parse('def f(a, b):\n    """Sample docstring"""\n    pass')
        f = functions.FunctionType.from_ast_node(node.body[0])
        self.assertEqual(f.args,['a','b'])
        self.assertEqual(f.docstring,"Sample docstring")
        self.assertEqual(f.return_values, basics.TypeSet())
        
        
    def testSimpleReturnType(self):
        f = functions.FunctionType('f', [], self.int, "")
        self.assertEqual(f.get_call_return([]),"<int>")
        
    def testMultpleReturnType(self):
        f = functions.FunctionType('f', [], basics.TypeSet(self.int, self.float), "")
        self.assertEqual(f.get_call_return([]),"<float> | <int>")
        
    def testContingentReturnType(self):
        f = functions.FunctionType('f', ['a', 'b'], basics.UnknownType('a'), "")
        self.assertEqual(f.get_call_return([self.int, self.float]), "<int>")

        f = functions.FunctionType('f', ['a', 'b'], basics.UnknownType('b'), "")
        self.assertEqual(f.get_call_return([self.int, self.float]), "<float>")
        
    def testContingentMultipleReturnType(self):
        return_type = basics.TypeSet(basics.UnknownType('a'), basics.UnknownType('b'))
        f = functions.FunctionType('f', ['a', 'b'], return_type, "")
        self.assertEqual(f.get_call_return([self.int, self.float]), "<float> | <int>")

    def testBadlyMatchedArgsReturnType(self):
        f = functions.FunctionType('f', ['a', 'b'], basics.UnknownType('a'), "")
        self.assertEqual(f.get_call_return([self.int]), "<int>")
    
        f = functions.FunctionType('f', ['a'], basics.UnknownType('a'), "")
        self.assertEqual(f.get_call_return([self.int, self.float]), "<int>")
        
    def testRecursiveFunction(self):
        f = functions.FunctionType('f', [], None, "")
        f.return_values = f
        self.assertEqual(f, 'f() -> (...)')
        

