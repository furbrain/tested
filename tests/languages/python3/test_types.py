import unittest

from tested.languages.python3.inferred_types import InferredType, InferredTuple, InferredList, InferredDict, TypeSet, UnknownType 
from tested.languages.python3.functions import FunctionType

class TestInferredType(unittest.TestCase):
    def setUp(self):
        class TempClass:
            pass
        self.test_type = InferredType.fromType(TempClass)
        
    def testInitWithSimpleVal(self):
        it_num = InferredType.fromType(1)
        it_str = InferredType.fromType("a")
        self.assertEqual(str(it_num),"<int>")
        self.assertEqual(str(it_str),"<str>")
        
    def testInitWithSimpleType(self): 
        it_num = InferredType.fromType(int)
        it_str = InferredType.fromType(str)
        self.assertEqual(str(it_num),"int")
        self.assertEqual(str(it_str),"str")
        
    def testEquality(self):
        it_num = InferredType.fromType(int)
        it_str = InferredType.fromType(str)
        self.assertEqual(it_num, it_num)
        self.assertEqual(it_num, int)
        self.assertEqual(it_str, it_str)
        self.assertEqual(it_str, str)
        self.assertNotEqual(it_num, 1)
        self.assertNotEqual(it_str, "a")

    def testInequality(self):        
        it_num = InferredType.fromType(int)
        it_str = InferredType.fromType(str)
        self.assertNotEqual(it_num, it_str)
        self.assertNotEqual(it_num, str)
        self.assertNotEqual(it_str, it_num)
        self.assertNotEqual(it_str, int)
        
    def testSingleAttributes(self):
        attr_dict = {'int':TypeSet(int),'str':TypeSet(str),'None':TypeSet(None)}
        for name, tp in attr_dict.items():
            self.test_type.add_attr(name, tp)
        for name, tp in attr_dict.items():
            self.assertEqual(self.test_type.get_attr(name), tp)
         
    def testMultiAttributes(self):
        attr_dict = {'int':TypeSet(int), 'str':TypeSet(str), 'None':TypeSet(None)}
        for tp in attr_dict.values():
            self.test_type.add_attr('multi',tp)
        self.assertEqual(self.test_type.get_attr('multi'), TypeSet(int,str,None))  
        
    def testUnknownAttribute(self):
        self.assertEqual(self.test_type.get_attr('surprise'), TypeSet(UnknownType()))
        
    def testSingleItem(self):
        self.test_type.add_item(TypeSet(int))
        self.assertEqual(self.test_type.get_item(12), TypeSet(int))

    def testMultiItem(self):
        self.test_type.add_item(TypeSet(int))
        self.test_type.add_item(TypeSet(str))
        self.assertEqual(self.test_type.get_item(12),TypeSet(int,str))
        
    def testUnknownItem(self):
        self.assertEqual(self.test_type.get_item(12), UnknownType())
        
    def testCallVia__call__(self):
        func = FunctionType('test',[],TypeSet(int),'')
        self.test_type.set_attr('__call__',func)
        self.assertEqual(self.test_type.get_call_return([]),TypeSet(int))
        
    def testBadCall(self):
        self.assertEqual(self.test_type.get_call_return([]), TypeSet(UnknownType()))

    def testAddType(self):    
        it_num = InferredType.fromType(1)
        it_num2  = InferredType.fromType(2)
        it_str = InferredType.fromType("a")
        self.assertEqual(it_num,it_num.add_type(it_num2))
        self.assertNotEqual(it_num, it_num.add_type(it_str))
        
    def testGetAllAttrs(self):
        it_num = InferredType.fromType(1)
        it_str = InferredType.fromType("a")
        self.test_type.add_attr('a',it_num)
        self.test_type.add_attr('b',it_str)
        self.test_type.add_attr('c',it_num)
        self.test_type.add_attr('c',it_str)
        self.assertEqual(self.test_type.get_all_attrs(),{'a':'<int>', 'b':'<str>', 'c':'<int>, <str>'})
       
       
class TestInferredTuple(unittest.TestCase):
    def setUp(self):
        self.int = InferredType.fromType(int)
        self.str = InferredType.fromType(str)
        self.float = InferredType.fromType(float)
        self.tuple = InferredTuple(self.int, self.str, self.float)
        
    def testInit(self):
        self.assertEqual(self.tuple, '(int, str, float)')
        
    def testIndex(self):
        self.assertEqual(self.tuple.get_item(0), self.int)
        self.assertEqual(self.tuple.get_item(1), self.str)
        self.assertEqual(self.tuple.get_item(2), self.float)
        self.assertEqual(self.tuple.get_item(self.int), TypeSet(self.int, self.str, self.float))
        
    def testBadIndex(self):
        self.assertEqual(self.tuple.get_item(3), UnknownType())    
        
    def testSlice(self):
        self.assertEqual(self.tuple.get_slice(), '[float, int, str]')
        
    def testAddItemDoesNothing(self):
        self.tuple.add_item(InferredType.fromType(complex))
        self.assertEqual(self.tuple, '(int, str, float)') 
        
class TestInferredList(unittest.TestCase):
    def setUp(self):
        self.int = InferredType.fromType(int)
        self.str = InferredType.fromType(str)
        self.float = InferredType.fromType(float)

    def testCreation(self):
        lst = InferredList(self.int,self.float)
        self.assertEqual(lst, '[float, int]')
        
    def testRecursiveList(self):
        lst = InferredList(self.int)
        lst.add_item(lst)
        self.assertEqual(lst, '[[...], int]')
            
class TestInferredDict(unittest.TestCase):
    def setUp(self):
        self.int = InferredType.fromType(int)
        self.str = InferredType.fromType(str)
        self.float = InferredType.fromType(float)
        self.dict = InferredDict(keys = [self.int, self.float], values = [self.str, self.float])

    def testInit(self):
        self.assertEqual(self.dict, '{float, int: float, str}')
        
    def testValues(self):
        self.assertEqual(self.dict.get_item(0), 'float, str')

    def testKeys(self):
        self.assertEqual(self.dict.get_key(), 'float, int')
        

class TestTypeSet(unittest.TestCase):
    def setUp(self):
        class TempClass1:
            pass
        class TempClass2:
            pass
        self.tc1 = InferredType.fromType(TempClass1)    
        self.tc2 = InferredType.fromType(TempClass2)    
        self.multiple_typeset = TypeSet(self.tc1, self.tc2)
        self.int = InferredType.fromType(int)
        self.str = InferredType.fromType(str)

    def testInitWithSingleVal(self):
        st = TypeSet(1)
        self.assertEqual(str(st),"<int>")
    
    def testInitWithSingleType(self):
        st = TypeSet(int)
        self.assertEqual(str(st),"int")
    
    def testInitWithSingleInferredType(self):
        st = TypeSet(InferredType.fromType(1))
        self.assertEqual(str(st),"<int>")
        
    def testWithMultipleVals(self):
        st = TypeSet(1,"a")
        self.assertEqual(str(st),"<int>, <str>")
        
    def testWithMixedVals(self):
        st = TypeSet(int, "a")
        self.assertEqual(str(st),"<str>, int")
        
    def testEquality(self):
        self.assertEqual(TypeSet(int), TypeSet(int))
        self.assertEqual(TypeSet(int, float), TypeSet(int, float))
        self.assertEqual(TypeSet(int, float),"float, int")
        
    def testInequality(self):
        self.assertNotEqual(TypeSet(int), TypeSet(float))
        self.assertNotEqual(TypeSet(int, float), TypeSet(int))
        self.assertNotEqual(TypeSet(int, float), "int,float")
        self.assertNotEqual(TypeSet(int),[])

    def testGetAttr(self): 
        self.tc1.add_attr('tst',self.int)
        self.tc2.add_attr('tst',self.str)
        self.assertEqual(self.multiple_typeset.get_attr('tst'), TypeSet(self.int, self.str))

    def testAddAttr(self): 
        self.multiple_typeset.add_attr('tst', self.int)
        self.assertEqual(self.tc1.get_attr('tst'), self.int)
        self.assertEqual(self.tc2.get_attr('tst'), self.int)
        
    def testGetItem(self):
        self.tc1.add_item(self.int)
        self.tc2.add_item(self.str)
        self.assertEqual(self.multiple_typeset.get_item(1), TypeSet(self.int, self.str))

    def testAddItem(self): 
        self.multiple_typeset.add_item(self.int)
        self.assertEqual(self.tc1.get_item(1),self.int)
        self.assertEqual(self.tc2.get_item(1),self.int)

    def testGetCallReturn(self): 
        func1 = FunctionType('f1',[],self.int,'')
        func2 = FunctionType('f2',[],self.str,'')
        ts = TypeSet(func1, func2)
        self.assertEqual(ts.get_call_return([]), TypeSet(self.int, self.str))

    def testGetAllAttrs(self): 
        self.tc1.add_attr('a',self.int)
        self.tc2.add_attr('b',self.str)
        self.tc1.add_attr('c',self.int)
        self.tc2.add_attr('c',self.str)
        self.assertEqual(self.multiple_typeset.get_all_attrs(),{
            'a':self.int, 
            'b':self.str, 
            'c':TypeSet(self.int, self.str)})

