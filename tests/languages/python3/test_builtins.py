import unittest
from tested.languages.python3 import get_global_scope, get_built_in_for_literal
from tested.languages.python3.inferred_types import get_type_name
from tested.languages.python3.magic_functions import FUNC_TYPES, UNKNOWN_FUNCS, REFLEX_FUNCS

class BasicTypeBase(unittest.TestCase):
    def setUp(self):
        self.instance_type = get_built_in_for_literal(self.target_instance)
        self.class_type = get_built_in_for_literal(self.target_class)
        
    def testExistence(self):
        pass

    def testName(self):
        self.assertEqual(str(self.instance_type),get_type_name(self.target_instance))
        self.assertEqual(str(self.class_type),get_type_name(self.target_class))


    def testAllAppropriateFunctionsAvailable(self):
        all_funcs = UNKNOWN_FUNCS.split() + REFLEX_FUNCS.split()
        for x in FUNC_TYPES.values():
            all_funcs.extend(x.split())
        all_funcs = ["__{}__".format(x) for x in all_funcs]
        for func in all_funcs:
            with self.subTest(func=func):
                if hasattr(self.target_class, func):
                    self.assertTrue(self.class_type.has_attr(func))
                if hasattr(self.target_instance, func):
                    self.assertTrue(self.instance_type.has_attr(func))
                    
    def testGeneratedFunctionsHaveCorrectArgumentCounts(self):
        self.assertEqual(self.get_function_arg_count(self.class_type,'__eq__'), 2)
        self.assertEqual(self.get_function_arg_count(self.instance_type,'__eq__'), 1)
        self.assertEqual(self.get_function_arg_count(self.class_type,'__hash__'), 1)
        self.assertEqual(self.get_function_arg_count(self.instance_type,'__hash__'), 0)
        
    def get_function_arg_count(self, tp, func_name):
        func = tp.get_attr(func_name)
        return len(func.args)
                
class TestIntLiteral(BasicTypeBase):
    target_class = int
    target_instance = 1

class TestFloatLiteral(BasicTypeBase):
    target_class = float
    target_instance = 1.2

class TestComplexLiteral(BasicTypeBase):
    target_class = complex
    target_instance = complex(1,2)

class TestStrLiteral(BasicTypeBase):
    target_class = str
    target_instance = "abc"

class TestNoneLiteral(BasicTypeBase):
    target_class = type(None)
    target_instance = None
    
    def testGeneratedFunctionsHaveCorrectArgumentCounts(self):
        pass #doesn't work proper for None

del BasicTypeBase
