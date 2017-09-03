import unittest
import unittest.mock
import tested.languages.python3.builtins
from tested.languages.python3 import get_built_in_for_literal
from tested.languages.python3.inferred_types import get_type_name
from tested.languages.python3.magic_functions import FUNC_TYPES, UNKNOWN_FUNCS, REFLEX_FUNCS
get_global_scope = tested.languages.python3.builtins.get_global_scope
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
        
    def testGeneratedFunctionsHaveDocStrings(self): 
        self.assertTrue(len(self.get_function_docstring(self.class_type,'__eq__'))>1)   
        self.assertTrue(len(self.get_function_docstring(self.instance_type,'__eq__'))>1)   
        
    def get_function_arg_count(self, tp, func_name):
        func = tp.get_attr(func_name)
        return len(func.args)
        
    def get_function_docstring(self, tp, func_name):
        func = tp.get_attr(func_name)
        return func.docstring
        
    def get_return_value(self, tp, func_name):
        func = tp.get_attr(func_name)
        return func.get_call_return([])
                
class TestIntLiteral(BasicTypeBase):
    target_class = int
    target_instance = 1
    
    def testToBytes(self):
        self.assertTrue(len(self.get_function_docstring(self.class_type,'to_bytes'))>1)
        self.assertEqual(self.get_return_value(self.class_type,'to_bytes'), get_built_in_for_literal(b'abc'))

class TestFloatLiteral(BasicTypeBase):
    target_class = float
    target_instance = 1.2

    def testIsInteger(self):
        self.assertTrue(len(self.get_function_docstring(self.class_type,'is_integer'))>1)
        self.assertEqual(self.get_return_value(self.class_type,'is_integer'), get_built_in_for_literal(True))


class TestComplexLiteral(BasicTypeBase):
    target_class = complex
    target_instance = complex(1,2)

    def testConjugate(self):
        self.assertTrue(len(self.get_function_docstring(self.class_type,'conjugate'))>1)
        self.assertEqual(self.get_return_value(self.class_type,'conjugate'), self.instance_type)

    def testAbs(self):
        self.assertEqual(self.get_return_value(self.instance_type,'__abs__'), get_built_in_for_literal(1.2))

class TestStrLiteral(BasicTypeBase):
    target_class = str
    target_instance = "abc"

    def testFormat(self):
        self.assertTrue(len(self.get_function_docstring(self.class_type,'format'))>1)
        self.assertEqual(self.get_return_value(self.class_type,'format'), self.instance_type)

class TestBytesLiteral(BasicTypeBase):
    target_class = bytes
    target_instance = b"abc"

    def testCenter(self):
        self.assertTrue(len(self.get_function_docstring(self.class_type,'center'))>1)
        self.assertEqual(self.get_return_value(self.class_type,'center'), self.instance_type)


class TestNoneLiteral(BasicTypeBase):
    target_class = type(None)
    target_instance = None
    
    def testGeneratedFunctionsHaveCorrectArgumentCounts(self):
        pass #doesn't work proper for None

del BasicTypeBase

class TestGetBuiltInForLiteral(unittest.TestCase):
    def testGetSimpleTypes(self):
        for literal in (1, 2.0, True, "abc", b"abc"):
            tp = get_built_in_for_literal(literal)
            self.assertEqual(tp,'<{}>'.format(type(literal).__name__))
            
    def testUnknownClass(self):
        class Temp:
            pass
        t = Temp()
        with self.assertRaises(AttributeError):
            get_built_in_for_literal(t)
    
class TestGetGlobalScope(unittest.TestCase):
    @unittest.mock.patch('tested.languages.python3.builtins.create_scope')
    def testCreateScopeCalledOnceOnly(self, mock_create):
        tested.languages.python3.builtins._scope = None #reset scope
        mock_create.ret_val = {'l':'something'}
        f = get_global_scope()
        g = get_global_scope()
        tested.languages.python3.builtins._scope = None #reset scope
        self.assertEqual(mock_create.call_count,1)

