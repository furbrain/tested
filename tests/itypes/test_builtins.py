import unittest
import unittest.mock
import tested.itypes.builtins as builtins
import tested.itypes.basics as basics

#get_global_scope = builtins.get_global_scope

class BasicTypeBase(unittest.TestCase):
    def setUp(self):
        self.instance_type = builtins.get_type_by_value(self.target_instance)
        self.class_type = builtins.get_type_by_value(self.target_class)

    def testName(self):
        self.assertEqual(str(self.instance_type), basics.get_type_name(self.target_instance))
        self.assertEqual(str(self.class_type), basics.get_type_name(self.target_class))

    def testAllAppropriateFunctionsAvailable(self):
        for func in dir(self.target_class):
            with self.subTest(func=func):
                if hasattr(self.target_class, func):
                    self.assertTrue(self.class_type.has_attr(func))
                if hasattr(self.target_instance, func):
                    self.assertTrue(self.instance_type.has_attr(func))

    def testAttributesPresent(self):
        self.assertEqual(self.class_type.get_attr('__class__'),'<type>')
                    
    def testGeneratedFunctionsHaveCorrectArgumentCounts(self):
        self.assertEqual(self.get_function_arg_count(self.class_type,'__eq__'), 2)
        self.assertEqual(self.get_function_arg_count(self.class_type,'__hash__'), 1)
        
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
        self.assertEqual(self.get_return_value(self.class_type,'to_bytes'), builtins.get_type_by_value(b'abc'))

class TestFloatLiteral(BasicTypeBase):
    target_class = float
    target_instance = 1.2

    def testIsInteger(self):
        self.assertTrue(len(self.get_function_docstring(self.class_type,'is_integer'))>1)
        self.assertEqual(self.get_return_value(self.class_type,'is_integer'), builtins.get_type_by_value(True))


class TestComplexLiteral(BasicTypeBase):
    target_class = complex
    target_instance = complex(1,2)

    def testConjugate(self):
        self.assertTrue(len(self.get_function_docstring(self.class_type,'conjugate'))>1)
        self.assertEqual(self.get_return_value(self.class_type,'conjugate'), self.instance_type)

    def testAbs(self):
        self.assertEqual(self.get_return_value(self.instance_type,'__abs__'), builtins.get_type_by_value(1.2))

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
            tp = builtins.get_type_by_value(literal)
            self.assertEqual(tp,'<{}>'.format(type(literal).__name__))
            
    def testUnknownClass(self):
        class Temp:
            pass
        t = Temp()
        with self.assertRaises(AttributeError):
            builtins.get_type_by_value(t)
    
class TestGetGlobalScope(unittest.TestCase):
    @unittest.mock.patch('tested.itypes.builtins.create_scope')
    def testCreateScopeCalledOnceOnly(self, mock_create):
        builtins._scope = None #reset scope
        mock_create.ret_val = {'l':'something'}
        f = builtins.get_global_scope()
        g = builtins.get_global_scope()
        builtins._scope = None #reset scope
        self.assertEqual(mock_create.call_count,1)

class TestCreateFuncs(unittest.TestCase):
    def setUp(self):
        self.int = builtins.get_type_by_value(1)
        self.str = builtins.get_type_by_value('abc')
        self.float = builtins.get_type_by_value(2.2)
        
    def testCreateList(self):
        self.assertEqual(builtins.create_list(self.int),'[<int>]')
        
    def testCreatedListsAreIndividual(self):
        self.assertFalse(builtins.create_list(self.int) is builtins.create_list(self.int))
        
    def testCreateTuple(self):
        self.assertEqual(builtins.create_tuple(self.int, self.str, self.float),'(<int>, <str>, <float>)')
        
    def testCreatedTuplesAreIndividual(self):
        self.assertFalse(builtins.create_tuple(self.int) is builtins.create_tuple(self.int))
        
    def testCreateSet(self):
        self.assertEqual(builtins.create_set(self.int, self.float),'{<float> | <int>}')
        
    def testCreatedSetsAreIndividual(self):
        self.assertFalse(builtins.create_set(self.int) is builtins.create_set(self.int))
        
    def testCreateDict(self):
        self.assertEqual(builtins.create_dict([self.int],[self.float]),'{<int>: <float>}')
        
    def testCreatedDictsAreIndividual(self):
        self.assertFalse(builtins.create_dict([self.int],[self.float]) is builtins.create_dict([self.int],[self.float]))
        
class TestSpecialTypeClass(unittest.TestCase):
    def testUniqueInstanceCreation(self):
        special_class = builtins.get_type_by_name('list')
        lst1 = special_class.get_call_return([])
        lst2 = special_class.get_call_return([])
        self.assertFalse(lst1 is lst2)
        
