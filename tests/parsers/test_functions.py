import unittest
from tested import utils, itypes
from tested.parsers import functions

class TestFunctionASTParser(unittest.TestCase):
    def testCreateFromSimpleNode(self):
        func_node = utils.get_matching_node('def f(a, b):\n    """Sample docstring"""\n    pass', 'FunctionDef')
        f = functions.get_function_skeleton_from_node(func_node)
        self.assertEqual(f.args,['a','b'])
        self.assertEqual(f.docstring,"Sample docstring")
        self.assertEqual(f.return_values, itypes.UnknownType('return'))

